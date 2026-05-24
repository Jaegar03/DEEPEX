# 🔭 Deep Research Agent — Deployment Guide

## Local Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create your .env file
cp .env.example .env
# Add your keys:
#   GEMINI_API_KEY=your_key_here
#   FIRECRAWL_API_KEY=your_key_here

# 3. Run
streamlit run deep_research_gemini.py
```

---

## 🚀 Deploy to Streamlit Community Cloud (Free, Recommended)

1. Push your code to a **public or private GitHub repo**
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo, branch, and `deep_research_gemini.py` as the main file
4. Under **Advanced settings → Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_gemini_key"
   FIRECRAWL_API_KEY = "your_firecrawl_key"
   ```
5. Click **Deploy** — live in ~2 minutes

> **Note:** In the deployed app, remove `load_dotenv()` calls or guard them with
> `if os.path.exists(".env"):` — Streamlit Cloud injects secrets as env vars directly.

---

## 🚂 Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli
railway login

# Deploy
railway init
railway up
```

Add env vars in Railway dashboard under **Variables**:
```
GEMINI_API_KEY=your_key
FIRECRAWL_API_KEY=your_key
```

Add a `Procfile`:
```
web: streamlit run deep_research_gemini.py --server.port $PORT --server.address 0.0.0.0
```

---

## 🤗 Deploy to Hugging Face Spaces

1. Create a new Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Choose **Streamlit** as the SDK
3. Upload your files or connect your GitHub repo
4. Add secrets in Space **Settings → Repository secrets**:
   - `GEMINI_API_KEY`
   - `FIRECRAWL_API_KEY`

---

## 🐳 Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "deep_research_gemini.py", \
     "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t deep-research-agent .
docker run -p 8501:8501 \
  -e GEMINI_API_KEY=your_key \
  -e FIRECRAWL_API_KEY=your_key \
  deep-research-agent
```

---

## ⚙️ Streamlit Config (optional)

Create `.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 50
enableCORS = false

[theme]
base = "dark"
primaryColor = "#00d4ff"
backgroundColor = "#07091a"
secondaryBackgroundColor = "#0d1230"
textColor = "#c8d8f0"
font = "serif"
```

This gives a dark baseline even before custom CSS loads.
