import streamlit as st
import os
import docx2txt
import PyPDF2
from openai import AzureOpenAI

# =============================
# 1. SETUP AZURE OPENAI CLIENT
# =============================
client = AzureOpenAI(
    api_key="key",  # Replace with your actual API key
    api_version="2024-12-01-preview",
    azure_endpoint="key"  # Update endpoint as well
)

deployment_name = "dep"  # Update with your actual deployment name in Azure OpenAI


# =============================
# 2. TEXT EXTRACTION UTILS
# =============================

def extract_text_from_pdf(uploaded_file):
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception:
        return None

def extract_text_from_docx(uploaded_file):
    try:
        return docx2txt.process(uploaded_file)
    except Exception:
        return None

def extract_text(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    else:
        return None

# =============================
# 3. GPT-EVALUATION FUNCTION
# =============================

def evaluate_resume_with_gpt(job_desc, resume_text):
    prompt = f"""
Compare the following Resume with the given Job Description and:
- Give a score out of 10 (format: "Score: x/10")
- Briefly explain why (format: "Reason: ...")

---

Job Description:
{job_desc}

---

Resume:
{resume_text}

---

Give only score and reason.
"""

    response = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {"role": "system", "content": "You are an expert hiring assistant."},
        {"role": "user", "content": prompt}
    ]
)


    return response.choices[0].message.content

# =============================
# 4. STREAMLIT WEB APP
# =============================

st.set_page_config(page_title="AI Resume Evaluator", layout="centered")
st.title("🤖 AI Resume Evaluator (Azure OpenAI)")

job_description = st.text_area("📄 Paste the Job Description below:", height=200)
resumes = st.file_uploader("📎 Upload Resumes (PDF or DOCX):", type=["pdf", "docx"], accept_multiple_files=True)

if st.button("Evaluate") and job_description and resumes:
    with st.spinner("Evaluating resumes using Azure OpenAI..."):
        for resume_file in resumes:
            resume_text = extract_text(resume_file)
            if resume_text:
                result = evaluate_resume_with_gpt(job_description, resume_text)
                st.markdown(f"### 📑 {resume_file.name}")
                st.success(result)
                st.markdown("---")
            else:
                st.error(f"❌ Couldn't read file: {resume_file.name}")