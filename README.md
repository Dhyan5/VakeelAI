# ⚖️ VakeelAI: Production-Grade Multilingual Indian Legal RAG Platform

> **Zero-Budget Architecture ($0 total cost, no credit card, no bank account required, zero local Docker container overhead)**

VakeelAI is an end-to-end, production-grade legal research and Retrieval-Augmented Generation (RAG) platform tailored for the Indian legal system. It provides cross-lingual querying across **English, Hindi (Devanagari), and Kannada**, strict anti-hallucination citation verification against authentic statutory texts (IPC, CrPC, Evidence Act, BNS, BNSS, BSA), and automated safety guardrails.

---

## 🚀 Key Features

- **🌐 Cross-Lingual RAG Engine**: Query in English, Hindi, or Kannada and retrieve relevant legal provisions indexed in a unified multilingual vector space (`paraphrase-multilingual-MiniLM-L12-v2`).
- **🛡️ Anti-Hallucination Discipline**: Strict citation grounding logic. Answers include verifiable statute section links; ungrounded citations are automatically flagged or suppressed with clear "NO LAW FOUND IN RETRIEVED CONTEXT" disclaimers.
- **🚫 Pre-Generation Safety Guardrails**: Hardened intent filter blocks assistance with illegal acts (evidence fabrication, perjury coaching, document forgery, warrant evasion) before LLM prompt generation.
- **📄 Multilingual OCR & Document Parsing**: Extracts text from PDFs, DOCX, and scanned images/scans in English, Hindi, and Kannada via Tesseract OCR engine.
- **⚡ Zero-Cost Cloud Ready**: Architected for free deployment on Hugging Face Spaces (backend Docker image built remotely) and Vercel (static React frontend).

---

## 💳 $0 Budget Stack Proof

| Component | Technology / Service | Free Tier Allocation | Credit Card Required? |
| :--- | :--- | :--- | :--- |
| **LLM Provider** | Groq (`llama-3.3-70b-versatile`) | 14,400 requests/day, 30 req/min | ❌ No |
| **Embedding Model** | `paraphrase-multilingual-MiniLM-L12-v2` | Open-Source Hugging Face model | ❌ No |
| **Vector Engine** | In-Memory NumPy Cosine Similarity Index | Unlimited local / container RAM | ❌ No |
| **Backend Host** | Hugging Face Spaces (Docker engine) | 16 GB RAM, 2 vCPU free container | ❌ No |
| **Frontend Host** | Vercel | Unlimited static hosting + CDN | ❌ No |
| **Database** | Turso (libSQL) / SQLite local fallback | 9 GB storage, 500 databases | ❌ No |
| **OCR Engine** | Tesseract OCR (`hin`, `kan`, `eng`) | Open-source system package | ❌ No |

---

## 🏗️ Architecture Blueprint

```
                     ┌──────────────────────────────────────────────┐
                     │            User Query (UI)                   │
                     │       (English / Hindi / Kannada)            │
                     └──────────────────────┬───────────────────────┘
                                            │
                                            ▼
                     ┌──────────────────────────────────────────────┐
                     │     Safety Guardrail Intent Filter           │
                     │   (Checks illegal intent / perjury / etc)    │
                     └──────┬────────────────────────────────┬──────┘
                            │ Allowed                        │ Blocked
                            ▼                                ▼
┌──────────────────────────────────────────────┐    ┌────────────────────────┐
│     Multilingual Vector Retrieval            │    │  Immediate Refusal     │
│   (paraphrase-multilingual-MiniLM-L12-v2)    │    │  (Safety Guardrail)    │
└──────────────────────┬───────────────────────┘    └────────────────────────┘
                       │
                       ▼ Cosine Similarity Cutoff (>= 0.35)
┌──────────────────────────────────────────────┐
│       Retrieved Legal Context & Statutes     │
│    (IPC, CrPC, BNS, BNSS, BSA, Act Sections) │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│     Groq LLM Legal Analysis Engine           │
│       (llama-3.3-70b-versatile)              │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│   Post-Processing Citation Grounding Audit   │
│ (Verifies cited sections against context)   │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│       Multilingual Response + Citations      │
└──────────────────────────────────────────────┘
```

---

## 🛠️ Local Development Setup (Plain Python venv, No Local Docker)

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend)
- Tesseract OCR installed on host system (optional for OCR testing)

### 2. Environment Setup
Clone the repository and copy the environment template:
```bash
git clone https://github.com/Dhyan5/VakeelAI.git
cd VakeelAI
cp .env.example .env
```
Add your free Groq API Key in `.env`:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 3. Backend Setup
Create virtual environment and install dependencies:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

Seed the knowledge base with statutory texts (IPC, CrPC, BNS, etc.):
```bash
python kb_seed/seed_kb.py
```

Start backend development server:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend Setup
In a separate terminal window:
```bash
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Test Suite Verification

Run the full pytest suite covering chunking, vector retrieval, cross-lingual query mapping, citation grounding, and guardrail enforcement:

```bash
python -m pytest tests/ -v
```

### Test Results Summary (17/17 Passed)
- `tests/test_chunking.py`: Section header splitting & Indic text cleaning (PASSED)
- `tests/test_retrieval.py`: Cross-lingual retrieval in English, Hindi, & Kannada (PASSED)
- `tests/test_citation_grounding.py`: Verification of citations & anti-hallucination cutoff (PASSED)
- `tests/test_guardrails.py`: Safety block on illegal intent, perjury, & document forgery (PASSED)

---

## 🌐 Remote Production Deployment Guide

### Backend: Hugging Face Spaces (Remote Docker Build)
1. Create a new Space on [Hugging Face Spaces](https://huggingface.co/spaces).
2. Select **Docker** as the SDK.
3. Push code to the Hugging Face Space repository:
   ```bash
   git remote add hf https://huggingface.co/spaces/<YOUR-USERNAME>/vakeel-ai-backend
   git push hf main
   ```
4. Set the secret `GROQ_API_KEY` in HF Space Settings -> Repository Secrets.
5. Hugging Face builds the Docker container remotely using `Dockerfile`.

### Frontend: Vercel
1. Connect your GitHub repository to [Vercel](https://vercel.com).
2. Set Framework Preset to **Vite**.
3. Set Environment Variable `VITE_API_BASE_URL` to your Hugging Face Space URL.
4. Deploy! Vercel serves the static React application globally over CDN.

---

## 📄 License & Legal Disclaimer

This tool is designed for legal research and educational reference only. It does not constitute formal legal advice. Consult a qualified advocate for professional legal guidance.
