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