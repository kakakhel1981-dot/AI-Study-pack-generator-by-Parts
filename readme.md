
Gemini
New chat
Search chats
Images
Library
New notebook
AI Study Pack Generator Guide
L2 Support Knowledge Assistant Initialization
Build and Deploy AI Content Assistant
AI Presentation Ready for Review
Building a RAG App Step-by-Step
I have deployed this code successfully on hugging face but when i give youtube url https://www.youtube.com/watch?v=Dhl0KPWDeh4, gets error HTTPSConnectionPool(host='www.youtube.com', port=443): Max retries exceeded with url: /watch?v=Dhl0KPWDeh4 (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1032)')))
Building a RAG App Step-by-Step
YouTube RAG Code Debugging
Building a RAG App Step-by-Step
Building a RAG App Step-by-Step
Building Text-to-Image App
Conversation with Gemini
I want to make a AI study pack generator application in python using colab for developmemt , streamlit for user interface/frontend, streamlit for deployment ,will use groq api and use process flow , divide the structure in to parts

Here is a blueprint and codebase to build and deploy an AI Study Pack Generator using Python, Google Colab (for fast prototyping), Groq API (using models like llama-3.3-70b-versatile), and Streamlit (for UI and deployment via Streamlit Community Cloud).

1. System Architecture & Process Flow
                     ┌───────────────────────────────┐
                     │          USER INPUT           │
                     │  (Text Notes / PDF Upload)    │
                     └───────────────┬───────────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │       STREAMLIT UI (FE)       │
                     │ Collects Input & Configuration│
                     └───────────────┬───────────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │    STUDY PACK ENGINE (BE)     │
                     │   Formats Prompt & Extracts   │
                     └───────────────┬───────────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │           GROQ API            │
                     │  Llama 3.3 70B Generation     │
                     └───────────────┬───────────────┘
                                     │
                                     ▼
 ┌───────────────────────────────────┴───────────────────────────────────┐
 │                        GENERATED STUDY PACK                           │
 ├───────────────────────┬───────────────────────┬───────────────────────┤
 │   1. Summary Notes    │    2. Flashcards      │   3. Practice Quiz    │
 └───────────────────────┴───────────────────────┴───────────────────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │    EXPORT & INTERACT (UI)     │
                     │  Download PDF/MD / Test Quiz  │
                     └───────────────────────────────┘
2. Project File Structure
To clean up development and prepare for deployment on GitHub/Streamlit Cloud, structure your project directory as follows:

Plaintext
ai-study-pack-generator/
│
├── app.py                   # Main Streamlit application file
├── requirements.txt         # Dependencies for Streamlit Cloud deployment
├── README.md                # Documentation & instructions
│
└── .streamlit/
    └── secrets.toml         # Local secrets (API keys) — DO NOT push to Git
3. Implementation Code
Part A: requirements.txt
Plaintext
streamlit>=1.30.0
groq>=0.9.0
pypdf>=4.0.0
python-dotenv>=1.0.0
Part B: app.py
Python
import streamlit as st
import pypdf
import os
from groq import Groq

# -----------------------------------------------------------------------------
# 1. Page Configuration & UI Layout
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Study Pack Generator",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Study Pack Generator")
st.caption("Powered by Groq LPU & Llama-3.3-70B")

# -----------------------------------------------------------------------------
# 2. Authentication & API Setup
# -----------------------------------------------------------------------------
# Try reading key from Streamlit secrets, then environment variable
groq_api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))

with st.sidebar:
    st.header("⚙️ Configuration")
    if not groq_api_key:
        groq_api_key = st.text_input("Enter Groq API Key:", type="password")
    
    selected_model = st.selectbox(
        "Select Model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
        index=0
    )
    
    study_level = st.selectbox(
        "Target Level",
        ["High School", "Undergraduate", "Postgraduate / Professional"],
        index=1
    )

if not groq_api_key:
    st.info("💡 Please enter your Groq API key in the sidebar to get started.")
    st.stop()

client = Groq(api_key=groq_api_key)

# -----------------------------------------------------------------------------
# 3. Helper Functions
# -----------------------------------------------------------------------------
def extract_text_from_pdf(pdf_file):
    reader = pypdf.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def generate_study_material(prompt_type, input_text, level):
    prompts = {
        "summary": f"Act as an expert tutor. Create concise, well-formatted structured revision notes with bullet points for a {level} student based on this text:\n\n{input_text}",
        "flashcards": f"Generate 5 to 8 high-yield flashcards from this text for a {level} student. Format strictly as:\nQ: [Question]\nA: [Answer]\n---\nText:\n{input_text}",
        "quiz": f"Generate a 5-question multiple choice quiz with answers and explanations for a {level} student based on this text:\n\n{input_text}"
    }
    
    response = client.chat.completions.create(
        model=selected_model,
        messages=[
            {"role": "system", "content": "You are a helpful study aid assistant that produces clear, structured educational materials in Markdown format."},
            {"role": "user", "content": prompts[prompt_type]}
        ],
        temperature=0.3,
        max_tokens=2048
    )
    return response.choices[0].message.content

# -----------------------------------------------------------------------------
# 4. User Input Handling
# -----------------------------------------------------------------------------
input_option = st.radio("Choose Input Method:", ["Upload PDF", "Paste Raw Text"], horizontal=True)
source_text = ""

if input_option == "Upload PDF":
    uploaded_file = st.file_uploader("Upload course PDF/notes", type=["pdf"])
    if uploaded_file:
        with st.spinner("Extracting text from PDF..."):
            source_text = extract_text_from_pdf(uploaded_file)
            st.success(f"PDF loaded successfully ({len(source_text.split())} words).")
else:
    source_text = st.text_area("Paste your study notes here:", height=200)

# -----------------------------------------------------------------------------
# 5. Core Execution Pipeline
# -----------------------------------------------------------------------------
if st.button("🚀 Generate Full Study Pack", type="primary", use_container_width=True):
    if not source_text.strip():
        st.error("Please provide text input or upload a PDF first.")
    else:
        tab_summary, tab_flashcards, tab_quiz = st.tabs(["📑 Summary Notes", "🃏 Flashcards", "❓ Quiz"])
        
        with tab_summary:
            with st.spinner("Generating summary notes..."):
                summary = generate_study_material("summary", source_text, study_level)
                st.markdown(summary)
                
        with tab_flashcards:
            with st.spinner("Generating flashcards..."):
                flashcards = generate_study_material("flashcards", source_text, study_level)
                st.markdown(flashcards)
                
        with tab_quiz:
            with st.spinner("Generating practice quiz..."):
                quiz = generate_study_material("quiz", source_text, study_level)
                st.markdown(quiz)
4. Development & Deployment Walkthrough
1
Develop and Test in Google Colab
Quick execution & fast debugging loop
Open Google Colab and create a new notebook.

Install the required dependencies:

Bash
!pip install streamlit groq pypdf localtunnel
Save the app.py script locally inside Colab using Python file-writing tools or line magic %%writefile app.py.

Test-run Streamlit directly from Colab using localtunnel or ngrok to preview your frontend without setting up a local machine:

Bash
!streamlit run app.py & npx localtunnel --port 8501
2
Set Up Repository on GitHub
Source control for production code
Create a public repository on GitHub (e.g., ai-study-pack-generator).

Push the files:

app.py

requirements.txt

.gitignore (ensure secrets or tokens are ignored)

3
Deploy to Streamlit Community Cloud
Free & permanent hosting
Navigate to share.streamlit.io and log in with your GitHub account.

Click New app, then select your repository, branch (main), and set the main file path to app.py.

Click Advanced Settings before clicking Deploy.

In the Secrets text box, add your Groq API key:

Ini, TOML
GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
Hit Deploy. Streamlit Cloud will automatically build your environment and give you a live web app URL.

provide me app.py, requirements.txt and other relevant files which are required to upload on github and to be deployed on streamlit

Here is a complete, production-ready project setup containing all the files you need to upload to GitHub and deploy directly to Streamlit Community Cloud.

Project File Structure
Ensure your GitHub repository contains these 3 core files:

Plaintext
ai-study-pack-generator/
│
├── app.py              # Main Streamlit application file
├── requirements.txt    # Python dependencies for deployment
└── README.md           # Project documentation and setup guide
File 1: requirements.txt
This file tells Streamlit Cloud which libraries to install when building your app.

Plaintext
streamlit>=1.30.0
groq>=0.9.0
pypdf>=4.0.0
python-dotenv>=1.0.0
File 2: app.py
This is the main application containing the UI, PDF processor, Groq API integration, and tabbed output viewer.

Python
import streamlit as st
import pypdf
import os
from groq import Groq

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Study Pack Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📚 AI Study Pack Generator")
st.caption("Transform your study materials into revision notes, flashcards, and practice quizzes in seconds.")

# -----------------------------------------------------------------------------
# 2. Authentication & API Key Setup
# -----------------------------------------------------------------------------
# Reads from Streamlit Secrets or Environment Variable, with a fallback UI input
groq_api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))

with st.sidebar:
    st.header("⚙️ Settings")
    
    if not groq_api_key:
        groq_api_key = st.text_input("Enter Groq API Key:", type="password", help="Get your key at console.groq.com")
    else:
        st.success("API Key configured", icon="✅")

    selected_model = st.selectbox(
        "Select Model",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768"
        ],
        index=0
    )
    
    study_level = st.selectbox(
        "Target Academic Level",
        ["High School", "Undergraduate", "Postgraduate / Professional"],
        index=1
    )

if not groq_api_key:
    st.info("👈 Please configure your Groq API key in the sidebar or via Streamlit Secrets to begin.")
    st.stop()

# Initialize Groq client
client = Groq(api_key=groq_api_key)

# -----------------------------------------------------------------------------
# 3. Helper Functions
# -----------------------------------------------------------------------------
def extract_text_from_pdf(pdf_file):
    """Extracts clean text from an uploaded PDF file."""
    reader = pypdf.PdfReader(pdf_file)
    extracted_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
    return extracted_text.strip()

def generate_study_material(prompt_type, input_text, level):
    """Calls Groq LLM API to generate targeted study material."""
    prompts = {
        "summary": (
            f"Act as an expert tutor. Create structured, comprehensive revision notes "
            f"tailored for a {level} student based on the text below. "
            f"Use headings, clear bullet points, key terms in bold, and a quick concept summary.\n\n"
            f"Text:\n{input_text}"
        ),
        "flashcards": (
            f"Generate 6 to 10 high-yield flashcards from this text for a {level} student. "
            f"Format clearly as:\n\n"
            f"**Front:** [Question / Concept]\n"
            f"**Back:** [Detailed Explanation / Answer]\n"
            f"---\n\n"
            f"Text:\n{input_text}"
        ),
        "quiz": (
            f"Generate a 5-question multiple choice quiz for a {level} student based on this text. "
            f"For each question, provide 4 options (A, B, C, D), indicate the correct answer, "
            f"and give a brief explanation for why it is correct.\n\n"
            f"Text:\n{input_text}"
        )
    }

    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an elite AI educational assistant. Output clean, well-structured Markdown."
                },
                {
                    "role": "user",
                    "content": prompts[prompt_type]
                }
            ],
            temperature=0.3,
            max_tokens=2500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error generating content: {str(e)}"

# -----------------------------------------------------------------------------
# 4. User Input Interface
# -----------------------------------------------------------------------------
input_option = st.radio("Select Input Method:", ["Upload PDF", "Paste Notes / Text"], horizontal=True)
source_text = ""

if input_option == "Upload PDF":
    uploaded_file = st.file_uploader("Upload course PDF or reading material", type=["pdf"])
    if uploaded_file:
        with st.spinner("Processing PDF content..."):
            source_text = extract_text_from_pdf(uploaded_file)
            if source_text:
                st.success(f"Successfully extracted ~{len(source_text.split())} words from '{uploaded_file.name}'")
            else:
                st.error("Could not extract readable text from this PDF. Please check if it contains selectable text.")
else:
    source_text = st.text_area("Paste your study notes or article text here:", height=200, placeholder="Paste material here...")

# -----------------------------------------------------------------------------
# 5. Core Generation Pipeline
# -----------------------------------------------------------------------------
st.markdown("---")

if st.button("🚀 Generate Complete Study Pack", type="primary", use_container_width=True):
    if not source_text.strip():
        st.warning("Please upload a PDF or enter study text before generating.")
    else:
        # Create tabs for organized viewing
        tab1, tab2, tab3 = st.tabs(["📑 Revision Notes", "🃏 Flashcards", "❓ Practice Quiz"])

        with tab1:
            with st.spinner("Drafting structured summary notes..."):
                summary_output = generate_study_material("summary", source_text, study_level)
                st.markdown(summary_output)
                st.download_button(
                    label="📥 Download Notes (.md)",
                    data=summary_output,
                    file_name="study_notes.md",
                    mime="text/markdown"
                )

        with tab2:
            with st.spinner("Creating high-yield flashcards..."):
                flashcards_output = generate_study_material("flashcards", source_text, study_level)
                st.markdown(flashcards_output)
                st.download_button(
                    label="📥 Download Flashcards (.md)",
                    data=flashcards_output,
                    file_name="flashcards.md",
                    mime="text/markdown"
                )

        with tab3:
            with st.spinner("Building practice quiz & answer key..."):
                quiz_output = generate_study_material("quiz", source_text, study_level)
                st.markdown(quiz_output)
                st.download_button(
                    label="📥 Download Quiz (.md)",
                    data=quiz_output,
                    file_name="practice_quiz.md",
                    mime="text/markdown"
                )
File 3: README.md
This provides clear instructions for anyone visiting your GitHub repository or attempting to run/deploy your app.

Markdown
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
Click Deploy!

💻 Local Development Setup
Bash
# Clone repository
git clone [https://github.com/your-username/ai-study-pack-generator.git](https://github.com/your-username/ai-study-pack-generator.git)
cd ai-study-pack-generator

# Install dependencies
pip install -r requirements.txt

# Run app locally
streamlit run app.py

---

### Deployment Checklist for Streamlit Cloud

1. Create a public repository on GitHub and commit `app.py`, `requirements.txt`, and `README.md`.
2. Log in to [Streamlit Cloud](https://share.streamlit.io/).
3. Connect the repository and set the main file path to `app.py`.
4. In **Advanced Settings > Secrets**, paste your API key as:
   ```toml
   GROQ_API_KEY = "gsk_..."
Click Deploy. Your live app URL will be ready in under 2 minutes without asking users to enter API keys manually.

provide me downloadable files

I will now generate the files for your AI Study Pack Generator repository so you can download and upload them directly to GitHub or Streamlit Cloud.

Requirements
streamlit>=1.30.0
groq>=0.9.0
pypdf>=4.0.0
python-dotenv>=1.0.0

Edit directly or with Gemini
 Click anywhere to type and edit directly, or select text to prompt Gemini for changes. 
Streamlit App Code
import streamlit as st
import pypdf
import os
from groq import Groq

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Study Pack Generator",

Readme Documentation
📚 AI Study Pack Generator
An AI-powered educational application built with Streamlit and Groq LPU, designed to instantly convert lecture notes and PDFs into structured revision summaries, high-yield flashcards, and self-assessment quizzes.

🚀 Features
PDF & Text Support: Upload PDF documents or paste raw text notes directly.

Fast Generation: Powered by Groq LLM infrastructure (llama-3.3-70b-versatile).

Targeted Learning: Tailor outputs based on academic depth (High School, Undergraduate, Postgraduate).

Export Ready: Download generated study materials directly as Markdown files.

⚙️ Deployment Instructions (Streamlit Cloud)
Push this repository to GitHub.

Go to share.streamlit.io and connect your GitHub account.

Click New app and select:

Repository: your-username/ai-study-pack-generator

Branch: main

Main file path: app.py

Expand Advanced Settings -> Secrets and add your Groq API key:

GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"

Click Deploy!

💻 Local Development Setup
# Clone repository
git clone https://github.com/your-username/ai-study-pack-generator.git
cd ai-study-pack-generator

# Install dependencies
pip install -r requirements.txt

# Run app locally
streamlit run app.py

Edit directly or with Gemini
 Click anywhere to type and edit directly, or select text to prompt Gemini for changes. 
I have generated all three essential files (app.py, requirements.txt, and README.md) in the panel. You can now download them directly to your machine and commit them to your GitHub repository for deployment on Streamlit Cloud.

now make this project according to AI workflow and design a multi-stage AI workflow that decomposes personalized study-pack generation further and deployed it through Streamlit."

[PDF / Text Input]
│
▼
[Stage 1: Text Ingestion & Noise Removal]
│
▼
[Stage 2: Knowledge Graph & Concept Map Extraction]
│
▼
[Stage 3: Pedagogical Synthesis (Summary Notes)]
│
▼
[Stage 4: Active Recall Artifacts (Flashcards & Quiz)]
│
▼
[Stage 5: Final Refinement & Streamlit UI Rendering]


## 🚀 Deployment

1. Push this project to GitHub.
2. Deploy on Streamlit Cloud (share.streamlit.io).
3. Set `GROQ_API_KEY` in Advanced Settings -> Secrets.
"""

with open(f"{project_dir}/README.md", "w") as f:
    f.write(readme_content)

# Zip files into downloadable package
zip_filename = "ai_study_pack_generator_multistage.zip"
with zipfile.ZipFile(zip_filename, "w") as zipf:
    for file in ["app.py", "requirements.txt", "README.md"]:
        zipf.write(os.path.join(project_dir, file), arcname=file)

print(f"Zip created successfully: {zip_filename}")

Your complete multi-stage AI workflow project package is ready:

ZIP icon
ai_study_pack_generator_multistage
 ZIP 
Multi-Stage AI Workflow Architecture
Instead of generating everything in a single LLM prompt—which often leads to generic summaries or shallow quizzes—this architecture decomposes study pack generation into a 5-Stage Sequential Pipeline. Each stage has a single, specialized responsibility and feeds its structured output into the next.

┌─────────────────────────────────────────────────────────────┐
│                    Stage 1: Ingestion & Noise Removal      │
│  • Normalizes raw text & strips headers/footers/OCR noise   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Stage 2: Concept Architecture Mapping           │
│  • Extracts key terms, prerequisites & curriculum schema    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Stage 3: Pedagogical Synthesis              │
│  • Builds structured revision notes grounded on concepts    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Stage 4: Active Recall Artifact Generation       │
│  • Creates high-yield flashcards & multiple-choice quiz     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Stage 5: UI & Export Rendering            │
│  • Renders tabbed interface & generates download buttons    │
└─────────────────────────────────────────────────────────────┘
🛠️ Complete Project Codebase
You can also view or download the individual files below:

1. app.py
PY icon
ai_study_pack_generator/app
 PY 
Python
import streamlit as st
import pypdf
import os
import json
from groq import Groq

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Study Pack Generator - Multi-Stage Workflow",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎓 Multi-Stage AI Study Pack Engine")
st.caption("Decomposed Agentic Pipeline Powered by Groq LPU & Llama 3.3 70B")

# -----------------------------------------------------------------------------
# 2. API Key Configuration
# -----------------------------------------------------------------------------
groq_api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))

with st.sidebar:
    st.header("⚙️ System Pipeline Settings")
    if not groq_api_key:
        groq_api_key = st.text_input("Enter Groq API Key:", type="password")
    else:
        st.success("API Key Active", icon="✅")

    selected_model = st.selectbox(
        "LLM Engine",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
        index=0
    )
    
    study_level = st.selectbox(
        "Target Level",
        ["High School", "Undergraduate", "Postgraduate / Professional"],
        index=1
    )

if not groq_api_key:
    st.info("👈 Please enter your Groq API key in the sidebar to run the multi-stage workflow.")
    st.stop()

client = Groq(api_key=groq_api_key)

# -----------------------------------------------------------------------------
# 3. Helper Functions
# -----------------------------------------------------------------------------
def extract_text_from_pdf(pdf_file):
    reader = pypdf.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()

def run_llm_stage(system_prompt, user_prompt, temperature=0.2):
    response = client.chat.completions.create(
        model=selected_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=2500
    )
    return response.choices[0].message.content

# -----------------------------------------------------------------------------
# 4. Multi-Stage AI Workflow Implementation
# -----------------------------------------------------------------------------
def execute_workflow(raw_text, level):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # STAGE 1: Text Ingestion & Cleaning
    status_text.markdown("🔄 **Stage 1/5:** Ingesting & Cleaning Input Data...")
    progress_bar.progress(10)
    sys_stage1 = "You are an expert text preprocessor. Clean up the following extracted text, remove noise (page numbers, headers, formatting artifacts), and produce coherent, clean source text."
    cleaned_text = run_llm_stage(sys_stage1, f"Clean this text:\n{raw_text[:8000]}")
    
    # STAGE 2: Curriculum Analysis & Concept Extraction
    status_text.markdown("🔍 **Stage 2/5:** Analyzing Knowledge Structure & Core Concepts...")
    progress_bar.progress(35)
    sys_stage2 = f"You are a Curriculum Architect for {level} students. Extract key concepts, core principles, and technical vocabulary. Output a structured JSON list of key concepts and learning objectives."
    concepts_json = run_llm_stage(sys_stage2, f"Extract core concepts from cleaned source:\n{cleaned_text}")
    
    # STAGE 3: Structured Summary Generation
    status_text.markdown("📑 **Stage 3/5:** Synthesizing Comprehensive Revision Notes...")
    progress_bar.progress(60)
    sys_stage3 = f"You are an Elite Academic Tutor. Using the provided concepts and clean source, write a highly structured Markdown revision guide tailored to {level} level."
    user_stage3 = f"Concepts:\n{concepts_json}\n\nClean Source Text:\n{cleaned_text}"
    summary = run_llm_stage(sys_stage3, user_stage3)
    
    # STAGE 4: Active Recall Synthesis (Flashcards & Quiz)
    status_text.markdown("🧠 **Stage 4/5:** Generating Active Recall Artifacts (Flashcards & Quiz)...")
    progress_bar.progress(85)
    
    sys_stage4_cards = f"Generate 6-8 high-yield active recall flashcards for {level} level in bold **Front:** and **Back:** format."
    flashcards = run_llm_stage(sys_stage4_cards, f"Generate flashcards based on these key concepts:\n{concepts_json}")
    
    sys_stage4_quiz = f"Generate a 5-question multiple-choice quiz for {level} level with answer choices, correct keys, and explanations."
    quiz = run_llm_stage(sys_stage4_quiz, f"Generate quiz based on this summary:\n{summary}")
    
    # STAGE 5: Refinement & Formatting
    status_text.markdown("✨ **Stage 5/5:** Polishing Final Study Pack...")
    progress_bar.progress(100)
    status_text.empty()
    progress_bar.empty()
    
    return {
        "cleaned_text": cleaned_text,
        "concepts": concepts_json,
        "summary": summary,
        "flashcards": flashcards,
        "quiz": quiz
    }

# -----------------------------------------------------------------------------
# 5. UI Application Flow
# -----------------------------------------------------------------------------
input_option = st.radio("Choose Input Method:", ["Upload PDF Document", "Paste Raw Lecture Notes"], horizontal=True)
source_text = ""

if input_option == "Upload PDF Document":
    uploaded_file = st.file_uploader("Upload Course Reading / PDF", type=["pdf"])
    if uploaded_file:
        source_text = extract_text_from_pdf(uploaded_file)
        st.success(f"Extracted ~{len(source_text.split())} words.")
else:
    source_text = st.text_area("Paste lecture notes or study material:", height=200)

if st.button("🚀 Execute Multi-Stage Workflow", type="primary", use_container_width=True):
    if not source_text.strip():
        st.error("Please provide text input or upload a PDF first.")
    else:
        results = execute_workflow(source_text, study_level)
        
        st.subheader("🎉 Generated Multi-Stage Study Pack")
        
        tab_summary, tab_cards, tab_quiz, tab_pipeline = st.tabs([
            "📑 Structured Notes", 
            "🃏 Flashcards", 
            "❓ Practice Quiz", 
            "🔍 Pipeline Metadata"
        ])
        
        with tab_summary:
            st.markdown(results["summary"])
            st.download_button("📥 Download Notes (.md)", results["summary"], "study_notes.md")
            
        with tab_cards:
            st.markdown(results["flashcards"])
            st.download_button("📥 Download Flashcards (.md)", results["flashcards"], "flashcards.md")
            
        with tab_quiz:
            st.markdown(results["quiz"])
            st.download_button("📥 Download Quiz (.md)", results["quiz"], "quiz.md")
            
        with tab_pipeline:
            st.markdown("### Stage 1: Cleaned Source Output")
            st.text_area("Cleaned Text Output", results["cleaned_text"], height=150)
            st.markdown("### Stage 2: Extracted Concept Map")
            st.text_area("Extracted Concepts", results["concepts"], height=150)
2. requirements.txt
TXT icon
ai_study_pack_generator/requirements
 TXT 
Plaintext
streamlit>=1.30.0
groq>=0.9.0
pypdf>=4.0.0
python-dotenv>=1.0.0
3. README.md
MD icon
ai_study_pack_generator/README
 MD 
⚡ Deployment Quick-Start
1
Extract Package
Unzip codebase locally
Extract ai_study_pack_generator_multistage.zip or save app.py, requirements.txt, and README.md into a folder on your computer.

2
Push to GitHub
Create repository
Create a new repository on GitHub (e.g., ai-study-pack-multistage) and push your project files to the main branch.

3
Deploy to Streamlit Cloud
Connect repository and configure secrets
Go to share.streamlit.io.

Click New app, select your repository, branch (main), and set the main file path to app.py.

Click Advanced Settings -> Secrets and enter:

Ini, TOML
GROQ_API_KEY = "gsk_your_groq_key_here"
Click Deploy. Your multi-stage workflow engine will be live in less than 2 minutes.

Want to add interactive quiz radio buttons or Anki flashcard export to this multi-stage workflow?

Yes




Gemini is AI and can make mistakes.

# 🎓 Multi-Stage AI Study Pack Generator

An advanced AI application that decomposes personalized study pack generation into a multi-stage LLM workflow (Ingestion -> Concept Extraction -> Synthesized Summarization -> Active Recall Generation -> Output Formatting).

## 🏗️ Architecture & AI Workflow

```
[PDF / Text Input]
       │
       ▼
[Stage 1: Text Ingestion & Noise Removal]
       │
       ▼
[Stage 2: Knowledge Graph & Concept Map Extraction]
       │
       ▼
[Stage 3: Pedagogical Synthesis (Summary Notes)]
       │
       ▼
[Stage 4: Active Recall Artifacts (Flashcards & Quiz)]
       │
       ▼
[Stage 5: Final Refinement & Streamlit UI Rendering]
```

## 🚀 Deployment

1. Push this project to GitHub.
2. Deploy on Streamlit Cloud (share.streamlit.io).
3. Set `GROQ_API_KEY` in Advanced Settings -> Secrets.
ai_study_pack_generator/README.md
Displaying ai_study_pack_generator/README.md.
