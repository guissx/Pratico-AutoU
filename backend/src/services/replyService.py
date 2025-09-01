import os
import json
from openai import OpenAI
from typing import Dict
from dotenv import load_dotenv
from .preprocessingService import (
    extract_text,
    basic_clean,
    detect_language,
    normalize
)
from transformers import pipeline


HF_MODEL = os.getenv("HF_MODEL", "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
HF_GENERATOR = os.getenv("HF_GENERATOR", "google/flan-t5-large")

_hf_classifier = None
_hf_generator = None

def get_hf_classifier():
    """Inicializa classificador HuggingFace apenas uma vez"""
    global _hf_classifier
    if _hf_classifier is None:
        _hf_classifier = pipeline(
            "zero-shot-classification",
            model=HF_MODEL,
            device=-1  # CPU
        )
    return _hf_classifier

def get_hf_generator():
    """Inicializa gerador HuggingFace apenas uma vez"""
    global _hf_generator
    if _hf_generator is None:
        if "t5" in HF_GENERATOR or "ptt5" in HF_GENERATOR or "mt5" in HF_GENERATOR:
            _hf_generator = pipeline(
                # flan-t5, ptt5, mt5
                "text2text-generation",
                model=HF_GENERATOR,
                device=-1
            )
        else:
            # BLOOM, Falcon, GPT-like
            _hf_generator = pipeline(
                "text-generation",
                model=HF_GENERATOR,
                device=-1
            )
    return _hf_generator


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()


system_prompt = """
    Você é um classificador especializado em e-mails corporativos com duas responsabilidades principais:

    1. CLASSIFICAÇÃO:
    Analise o e-mail e categorize como:
    - "Produtivo": Requer ação imediata, resposta específica, investigação ou follow-up
    - "Improdutivo": Não requer ação (agradecimentos, elogios, comunicações informativas, spams)

    2. RESPOSTA AUTOMÁTICA:
    Gere uma resposta profissional adequada à categoria, com até 80 palavras, seguindo estas diretrizes:
    - Tom cordial e objetivo
    - No mesmo idioma do e-mail original
    - Estrutura clara: saudação, mensagem principal e encerramento

    REGRA CRÍTICA: Em caso de dúvida, classifique como "Produtivo"

    FORMATO DE SAÍDA:
    Responda APENAS em JSON válido com este formato exato:
    {
    "categoria": "Produtivo"|"Improdutivo",
    "resposta": "Texto da resposta aqui"
    }

    EXEMPLOS:
    Input: "Obrigado pelo suporte! Tudo resolvido."
    Output: {"categoria": "Improdutivo", "resposta": "Olá! Agradecemos o feedback positivo. Ficamos felizes em poder ajudar. Conte conosco sempre que necessário."}

    Input: "Erro 503 no sistema desde ontem às 15h."
    Output: {"categoria": "Produtivo", "resposta": "Olá! Reportamos seu problema de acesso ao time técnico. Para agilizar, envie prints do erro e detalhes do navegador utilizado. Retornaremos em até 2h."}
    """.strip()


def classify_email(filename: str, file_bytes: bytes, provider: str = "openai", stemming: bool = False) -> Dict:
    raw = extract_text(filename, file_bytes)
    
    if not raw.strip():
        raise ValueError("Não foi possível extrair texto do arquivo.")

    cleaned = basic_clean(raw)
    normalized = normalize(raw, use_stemming=stemming)



    # ========== OPENAI ==========
    if provider == "openai":
        client = OpenAI(api_key=OPENAI_API_KEY)

        user_prompt = f"""
Analise e classifique o seguinte e-mail:

\"\"\"{normalized[:1200]}\"\"\"
        """.strip()

        try:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.4,
            )

            content = res.choices[0].message.content.strip()

            try:
                parsed = json.loads(content)
            except Exception:
                print("[OpenAI erro] resposta não era JSON, fallback aplicado")
                parsed = {
                    "categoria": "Produtivo",
                    "resposta": "Olá! Obrigado pela mensagem. Registramos sua solicitação."
                }

            # normalizar
            categoria = parsed.get("categoria", "Indefinido").strip()
            if categoria.lower().startswith("produtivo"):
                categoria = "Produtivo"
            elif categoria.lower().startswith("improdutivo"):
                categoria = "Improdutivo"
            else:
                categoria = "Produtivo"  # fallback

            return {
                "category": categoria,
                "confidence": 1.0 if categoria in ["Produtivo", "Improdutivo"] else 0.0,
                "suggested_reply": parsed.get("resposta", "").strip(),
                "language": detect_language(cleaned),
                "preview": raw[:300],
                "provider": "openai",
            }

        except Exception as e:
            print("[OpenAI exceção]", str(e))
            return {
                "category": "Produtivo",
                "confidence": 0.0,
                "suggested_reply": "Olá! Obrigado pela mensagem. Registramos sua solicitação.",
                "language": detect_language(cleaned),
                "preview": normalized[:300],
                "provider": "openai-fallback",
            }

    # HUGGING FACE
    if provider == "huggingface":

        hypothesis_template = (
        "Analise este e-mail e classifique rigorosamente como '{}':\n"
        "PRODUTIVO: Se exigir qualquer tipo de ação, resposta, investigação, "
        "resolução, aprovação, orçamento ou follow-up\n"
        "IMPRODUTIVO: Se for apenas comunicação social, agradecimento, "
        "reconhecimento, informação ou conteúdo promocional\n"
        "Classificação final:"
    )


        try:
            clf = get_hf_classifier()
            generator = get_hf_generator()

            labels = ["Produtivo", "Improdutivo"]
            result = clf(normalized, candidate_labels=labels, hypothesis_template=hypothesis_template)
            category = result["labels"][0]
            confidence = float(result["scores"][0])
            
            # Mudar o prompt, para gerar uma resposta que seja mais satisfatória
            """
            if category == "Produtivo":
                gen_prompt = f"Write a professional response (2 lines max) to the e-mail: {cleaned[:150]}"
            else:  # Improdutivo
                gen_prompt= f"Write a one-line thank you reply to the e-mail: {cleaned[:120]}"

            gen_out = generator(
                gen_prompt,
                max_new_tokens=30,
                num_return_sequences=1,
                do_sample=True,
                temperature=0.3,  #respostas mais conservadoras
                top_p=0.9,
                repetition_penalty=1.2
            )[0]["generated_text"]
            """


            #Gerando a resposta com OpenIA
            client = OpenAI(api_key=OPENAI_API_KEY)
            user_prompt = f"""
            Analise e classifique o seguinte e-mail:
            \"\"\"{normalized[:1200]}\"\"\"
            """.strip()
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.4,
            )

            content = res.choices[0].message.content.strip()
            parsed = json.loads(content)

            return {
                "category": category,
                "confidence": round(confidence, 4),
                "suggested_reply": parsed.get("resposta", "").strip(),
                "language": detect_language(cleaned),
                "preview": raw[:300],
                "provider": "huggingface",
            }


        except Exception as e:
            print("[HF erro]", str(e))
            return {
                "category": "Produtivo",
                "confidence": 0.0,
                "suggested_reply": "Olá! Obrigado pela mensagem. Registramos sua solicitação.",
                "language": detect_language(cleaned),
                "preview": raw[:300],
                "provider": "huggingface-fallback",
            }

    # ========== FALLBACK GERAL ==========
    return {
        "category": "Produtivo",
        "confidence": 0.0,
        "suggested_reply": "Olá! Obrigado pela mensagem. Registramos sua solicitação.",
        "language": detect_language(cleaned),
        "preview":raw[:300],
        "provider": "fallback",
    }
