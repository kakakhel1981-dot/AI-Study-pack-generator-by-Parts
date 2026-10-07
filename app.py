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
        ["llama-3.3-70b-versatile",
         "openai/gpt-oss-120b"
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768"],
     
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
