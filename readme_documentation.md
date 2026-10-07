# 📚 AI Study Pack Generator

An AI-powered educational application built with **Streamlit** and **Groq LPU**, designed to instantly convert lecture notes and PDFs into structured revision summaries, high-yield flashcards, and self-assessment quizzes.

## 🚀 Features

- **PDF & Text Support:** Upload PDF documents or paste raw text notes directly.
- **Fast Generation:** Powered by Groq LLM infrastructure (`llama-3.3-70b-versatile`).
- **Targeted Learning:** Tailor outputs based on academic depth (High School, Undergraduate, Postgraduate).
- **Export Ready:** Download generated study materials directly as Markdown files.

## ⚙️ Deployment Instructions (Streamlit Cloud)

1. Push this repository to **GitHub**.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and connect your GitHub account.
3. Click **New app** and select:
   - **Repository:** `your-username/ai-study-pack-generator`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Expand **Advanced Settings** -> **Secrets** and add your Groq API key:
   ```toml
   GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
   ```
5. Click **Deploy**!

## 💻 Local Development Setup

```bash
# Clone repository
git clone https://github.com/your-username/ai-study-pack-generator.git
cd ai-study-pack-generator

# Install dependencies
pip install -r requirements.txt

# Run app locally
streamlit run app.py
```