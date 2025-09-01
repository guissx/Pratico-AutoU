# 📧 Classificador Inteligente de E-mails

Projeto de IA que classifica e responde e-mails automaticamente:

- **Produtivo** → requer ação/resposta (ex: dúvidas, suporte, problemas).  
- **Improdutivo** → não requer ação (ex: agradecimentos, parabéns, comunicações genéricas).  

O sistema utiliza **FastAPI (backend)** + **Next.js (frontend)** com suporte a **modelos OpenAI** e **Hugging Face**.

---

## 🚀 Tecnologias
- **Backend**: Python 3.10+, FastAPI, Transformers, OpenAI SDK  
- **Frontend**: Next.js 14, TypeScript, TailwindCSS  
- **IA**:
  - Classificação → `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` (HF) ou GPT  
  - Geração de resposta → `unicamp-dl/ptt5-base-portuguese-vocab`, `flan-t5` ou GPT  

---

## 📂 Estrutura do Projeto

```
Pratico-AutoU/
├── backend/
│   └── src/
│       ├── app.py              # Endpoints FastAPI
│       ├── services/           # Serviços de NLP e classificação
│       ├── preprocessingService.py
│       └── replyService.py
└── frontend/
    └── src/
        ├── app/                # App Router (Next.js 14)
        └── components/         # UploadForm
```

---

## ⚙️ Configuração Local

### 1. Clone o projeto
```bash
git clone https://github.com/guissx/Pratico-AutoU.git
cd Pratico-AutoU
```

### 2. Backend (FastAPI)

#### Criar venv e instalar dependências

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

#### Configurar variáveis de ambiente

Crie um arquivo `.env` dentro de `backend/`:

```
OPENAI_API_KEY=sk-xxxx
HF_MODEL=MoritzLaurer/mDeBERTa-v3-base-mnli-xnli
HF_GENERATOR=unicamp-dl/ptt5-base-portuguese-vocab
```

#### Rodar servidor

```bash
uvicorn src.app:app --reload --port 8000
```

Servidor local → [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 3. Frontend (Next.js)

#### Instalar dependências

```bash
cd ../frontend
npm install
```

#### Rodar servidor de dev

```bash
npm run dev
```

Frontend local → [http://localhost:3000](http://localhost:3000)

---

## 🌐 Deploy em Produção

* **Frontend**: [Vercel](https://pr-tico-auto-u-front-h66duebh8-guissxs-projects.vercel.app/) → conectar repositório `frontend/`
* **Backend**:
  * [Render](https://render.com/), [Railway](https://railway.app/) ou AWS EC2
  * Configure variáveis de ambiente no painel de deploy
  * Exponha a API (ex: `https://seu-backend.com/classify`)

⚠️ Importante: no `frontend/src/components/UploadForm.tsx`, ajuste a constante `apiBase` para a URL do backend em produção.

```ts
const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
```

No `.env.local` do frontend:

```
NEXT_PUBLIC_API_URL=https://seu-backend.com
```

---

## 🧪 Testes Rápidos

### Endpoint de Saúde

```bash
curl http://localhost:8000/health
```

### Upload via cURL

```bash
curl -X POST "http://localhost:8000/classify?provider=openai" \
  -F "file=@exemplo_email.txt"
```

---

## ✅ Checklist

* [x] Upload de PDF/TXT
* [x] Pré-processamento (limpeza, normalização, stemming opcional)
* [x] Classificação com OpenAI ou Hugging Face
* [x] Geração de resposta automática
* [x] Interface web com upload e exibição dos resultados

---

👨‍💻 **Autor**: Gustavo Ferreira Cabral
📌 Projeto para estudo de **IA Generativa + NLP + Web Fullstack**

---

