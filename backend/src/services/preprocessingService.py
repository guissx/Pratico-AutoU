import io
import re
import string
from typing import Tuple

import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from pypdf import PdfReader
from langdetect import detect, DetectorFactory

# -stopwords br
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

PT_STOPS = set(stopwords.words("portuguese"))
STEMMER = RSLPStemmer()


SIG_PATTERNS = [
    r"(?im)atenciosamente[,]?.*$",
    r"(?im)enviado do meu iphone.*$",
    r"(?im)enviado do meu android.*$",
    r"(?im)^--\s*$.*",
]
QUOTE_PATTERNS = [
    r"(?im)^>+.*$",
    r"(?is)-----Mensagem original-----.*",
    r"(?im)^de:\s.*$.*",
]

EMOJI_PATTERN = re.compile("["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # símbolos/misc
    u"\U0001F680-\U0001F6FF"  # transportes
    u"\U0001F1E0-\U0001F1FF"  # bandeiras
    u"\u2600-\u26FF"          # misc símbolos
    "]+", flags=re.UNICODE)

def extract_text(filename: str, file_bytes: bytes) -> str:
    """Extrair texto de .pdf ou .txt."""
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    if name.endswith(".txt"):
        for enc in ("utf-8", "latin-1"):
            try:
                return file_bytes.decode(enc)
            except Exception:
                continue
        return file_bytes.decode("utf-8", errors="ignore")
    raise ValueError("Formato não suportado: envie .pdf ou .txt")

def basic_clean(text: str) -> str:
    """
    Limpeza básica, para geração de texto e parte do pré-processamento para classificação.
    Remover elementos de formatação e ruído, mantendo a estrutura para não atrapalhar a geração de linguagem natural.
    """
    # Remover encadeamentos/quotas e assinaturas
    for pat in QUOTE_PATTERNS:
        text = re.sub(pat, "", text)
    for pat in SIG_PATTERNS:
        text = re.sub(pat, "", text)
    
    # Remover URLs e e-mails
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    
    # Remover emojis
    text = EMOJI_PATTERN.sub(r"", text)
    
    # Normalização de espaços
    text = text.replace("\r", " ")
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

def normalize(text: str, use_stemming: bool = False) -> str:
    """
    PRÉ-PROCESSAMENTO mais pesado para classificação/análise.
    Aplica transformações agressivas para features de ML.
    """
    # Aplica limpeza básica primeiro
    t = basic_clean(text)
    
    # Remove pontuação
    t = t.translate(str.maketrans("", "", string.punctuation))
    
    # Remove números isolados 
    t = re.sub(r"\d+\b", " ", t)
    
    # Tokeniza e remove stopwords 
    tokens = [w for w in t.split() if w not in PT_STOPS]
    
    # Stemming 
    if use_stemming:
        tokens = [STEMMER.stem(w) for w in tokens]
    
    return " ".join(tokens)


DetectorFactory.seed = 0  

def detect_language(text: str) -> str:
    """
    Langdetect Detecta o idioma principal do texto retornando os códigos ISO 
    """
    if not text or not text.strip():
        return "desconhecido"
    try:
        lang = detect(text)
        # Se for português, padroniza para pt-BR
        return "pt-BR" if lang == "pt" else lang
    except Exception:
        return "desconhecido"
