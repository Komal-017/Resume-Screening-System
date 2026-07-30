# ============================================================
# RESUME SCREENING SYSTEM
# Machine Learning Project
# ============================================================

# ==========================
# IMPORTS
# ==========================
import streamlit as st
import pickle
import re
import os
import pandas as pd

import fitz
import pytesseract

from PIL import Image
from docx import Document

import plotly.graph_objects as go
import plotly.express as px

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


# ==========================
# TESSERACT CONFIG
# ==========================
if os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(
    page_title="Resume Screening System",
    page_icon="📄",
    layout="wide"
)


# ==========================
# CSS
# ==========================
st.markdown("""
<style>
/* Remove Streamlit Branding */
#MainMenu { display: none; }
footer { display: none; }
header { display: none; }

/* Main Background */
.stApp {
    background: #f8fafc;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #1E3A8A 0%,
        #1E40AF 50%,
        #1E3A8A 100%
    );
    border-right: 2px solid #2563EB;
}

section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

div[role="radiogroup"] label {
    background: rgba(255,255,255,0.08);
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 6px;
    transition: all 0.3s ease;
}

div[role="radiogroup"] label[data-selected="true"] {
    background: #2563EB !important;
    color: white !important;
    font-weight: bold;
}

/* Typography */
.title {
    font-size: 38px;
    font-weight: 800;
    color: #1E40AF;
}

.subtitle {
    font-size: 17px;
    color: #475569;
}

/* Cards */
.card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    border: 1px solid #e2e8f0;
}

[data-testid="stMetricValue"] {
    color: #2563eb;
    font-size: 28px;
    font-weight: bold;
}

[data-testid="stMetricLabel"] {
    color: #334155;
}

.stButton button {
    background: #2563eb;
    color: white;
    border-radius: 10px;
    height: 45px;
    font-weight: bold;
    width: 100%;
    border: none;
}

.stButton button:hover {
    background: #1d4ed8;
}

div[data-baseweb="input"] input, textarea {
    color: #000000 !important;
    background-color: #FFFFFF !important;
    caret-color: #000000 !important;
}

h1, h2, h3, h4, h5, h6, label, p {
    color: #111827 !important;
}
</style>
""", unsafe_allow_html=True)


# ==========================
# RESUME EXTRACTION FUNCTIONS
# ==========================
def extract_pdf(file):
    text = ""
    try:
        file.seek(0)
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        for page in pdf:
            page_text = page.get_text()
            if page_text and page_text.strip():
                text += page_text + "\n"
            else:
                try:
                    pix = page.get_pixmap(dpi=300)
                    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    ocr_text = pytesseract.image_to_string(image, lang="eng")
                    text += ocr_text + "\n"
                except Exception:
                    pass
        pdf.close()
    except Exception as e:
        st.error(f"Error extracting PDF: {e}")
    return text


def extract_docx(file):
    text = ""
    try:
        file.seek(0)
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        st.error(f"Error extracting DOCX: {e}")
    return text


def extract_txt(file):
    try:
        file.seek(0)
        return file.read().decode("utf-8")
    except Exception as e:
        st.error(f"Error extracting TXT: {e}")
        return ""


# ==========================
# TEXT CLEANING
# ==========================
def clean_text(text):
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"www\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"[^A-Za-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()


# ==========================
# CANDIDATE DETAILS EXTRACTION
# ==========================
def extract_name(text):
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if (
            3 < len(line) < 35
            and len(line.split()) <= 4
            and not any(char.isdigit() for char in line)
            and "resume" not in line.lower()
            and "curriculum" not in line.lower()
        ):
            return line.title()
    return "Candidate"


def extract_email(text):
    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    match = re.search(pattern, text)
    return match.group(0) if match else "Not Found"


def extract_phone(text):
    pattern = r"(?:\+91[\-\s]?)?[6-9]\d{9}"
    match = re.search(pattern, text)
    return match.group(0) if match else "Not Found"


# ==========================
# MASTER SKILLS & ANALYSIS
# ==========================
MASTER_SKILLS = [
    "python", "java", "c++", "c#", "sql", "mysql", "postgresql", "mongodb",
    "html", "css", "javascript", "typescript", "react", "angular", "vue",
    "node", "express", "django", "flask", "fastapi", "bootstrap", "tailwind",
    "machine learning", "deep learning", "data science", "nlp", "computer vision",
    "pandas", "numpy", "tensorflow", "pytorch", "keras", "scikit learn", "scikit-learn",
    "git", "github", "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd",
    "communication", "problem solving", "teamwork", "agile", "scrum"
]


def extract_skills(text):
    text_lower = text.lower()
    matched_skills = [skill for skill in MASTER_SKILLS if skill.lower() in text_lower]
    missing_skills = [skill for skill in MASTER_SKILLS if skill not in matched_skills]
    return matched_skills, missing_skills


def extract_keywords(text):
    text_lower = text.lower()
    return [skill for skill in MASTER_SKILLS if skill in text_lower]


def calculate_ats_score(matched_skills):
    if len(MASTER_SKILLS) == 0:
        return 0
    score = (len(matched_skills) / len(MASTER_SKILLS)) * 100
    return round(score, 2)


ROLE_SKILLS = {
    "Software Engineer": ["python", "java", "c++", "sql", "git", "docker", "problem solving"],
    "Data Scientist": ["python", "machine learning", "pandas", "numpy", "sql", "data science", "tensorflow"],
    "ML Engineer": ["python", "machine learning", "deep learning", "tensorflow", "numpy", "docker", "pytorch"],
    "Python Developer": ["python", "sql", "git", "html", "css", "django", "flask", "problem solving"],
    "Web Developer": ["html", "css", "javascript", "react", "git", "node", "typescript"]
}


def role_skill_analysis(text, role):
    required = ROLE_SKILLS.get(role, [])
    text_lower = text.lower()
    found = [skill for skill in required if skill.lower() in text_lower]
    missing = [skill for skill in required if skill not in found]
    score = round(len(found) / len(required) * 100, 2) if len(required) > 0 else 0
    return found, missing, score


# ==========================
# LOAD MODEL & DATASET
# ==========================
@st.cache_resource
def load_model():
    model = pickle.load(open("resume_model.pkl", "rb"))
    tfidf = pickle.load(open("tfidf_vectorizer.pkl", "rb"))
    return model, tfidf


model, tfidf = load_model()


@st.cache_data
def load_dataset():
    if os.path.exists("ml_resume_dataset_4500.csv"):
        return pd.read_csv("ml_resume_dataset_4500.csv")
    return None


dataset_df = load_dataset()


# ==========================
# SIDEBAR
# ==========================
with st.sidebar:
    st.markdown("""
    <h1 style="text-align:center">📄</h1>
    <h2 style="text-align:center">Resume Screening</h2>
    """, unsafe_allow_html=True)

    st.divider()

    menu = st.radio(
        "Menu Navigation",
        [
            "Dashboard",
            "Resume Analysis",
            "Batch Screening",
            "Analytics",
            "Dataset Insights",
            "Role Skill Comparator"
        ]
    )

    st.divider()

    st.success("""
    Machine Learning Suite
    ✔ Logistic Regression
    ✔ TF-IDF Vectorizer
    ✔ PyMuPDF Text Engine
    ✔ Batch Leaderboard
    ✔ Interactive Analytics
    """)


# ==========================
# HEADER
# ==========================
st.markdown("""
<div class="title">📄  Resume Screening System</div>
<div class="subtitle">Machine Learning & NLP Based Candidate Screening & Analytics Platform</div>
""", unsafe_allow_html=True)

st.divider()


# ==========================
# SESSION STATE INITIALIZATION
# ==========================
if "ats_score" not in st.session_state:
    st.session_state.ats_score = 0.0
if "role_match" not in st.session_state:
    st.session_state.role_match = 0.0
if "confidence" not in st.session_state:
    st.session_state.confidence = 0.0
if "resume_score" not in st.session_state:
    st.session_state.resume_score = 0.0
if "has_analyzed" not in st.session_state:
    st.session_state.has_analyzed = False
if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""
if "candidate_email" not in st.session_state:
    st.session_state.candidate_email = ""
if "candidate_phone" not in st.session_state:
    st.session_state.candidate_phone = ""
if "target_role" not in st.session_state:
    st.session_state.target_role = ""
if "prediction" not in st.session_state:
    st.session_state.prediction = None
if "probability" not in st.session_state:
    st.session_state.probability = [0.0, 0.0]
if "prediction_text" not in st.session_state:
    st.session_state.prediction_text = ""
if "matched_skills" not in st.session_state:
    st.session_state.matched_skills = []
if "role_missing" not in st.session_state:
    st.session_state.role_missing = []
if "missing_skills" not in st.session_state:
    st.session_state.missing_skills = []


# ==========================
# TOP METRICS BANNER
# ==========================
metric1, metric2, metric3, metric4 = st.columns(4)
with metric1:
    st.metric("📊 ATS Score", f"{st.session_state.ats_score:.2f}%")
with metric2:
    st.metric("🎯 Role Match", f"{st.session_state.role_match:.2f}%")
with metric3:
    st.metric("✅ Confidence", f"{st.session_state.confidence:.2f}%")
with metric4:
    st.metric("⭐ Resume Score", f"{st.session_state.resume_score:.2f}%")

st.divider()


# ==========================
# PDF REPORT HELPER
# ==========================
def create_report(
    filename, name, email, phone, role, prediction,
    confidence, ats_score, role_match, resume_score,
    matched_skills, missing_skills
):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>Resume Screening Report</b>", styles["Title"]))
    story.append(Paragraph(f"Candidate : {name}", styles["Normal"]))
    story.append(Paragraph(f"Email : {email}", styles["Normal"]))
    story.append(Paragraph(f"Phone : {phone}", styles["Normal"]))
    story.append(Paragraph(f"Target Role : {role}", styles["Normal"]))
    story.append(Paragraph("<br/>", styles["Normal"]))
    story.append(Paragraph(f"Prediction : {prediction}", styles["Normal"]))
    story.append(Paragraph(f"Confidence : {confidence:.2f}%", styles["Normal"]))
    story.append(Paragraph(f"ATS Score : {ats_score:.2f}%", styles["Normal"]))
    story.append(Paragraph(f"Role Match : {role_match:.2f}%", styles["Normal"]))
    story.append(Paragraph(f"Resume Score : {resume_score:.2f}%", styles["Normal"]))
    story.append(Paragraph("<br/>", styles["Normal"]))
    story.append(Paragraph("<b>Matched Skills:</b><br/>" + (", ".join(matched_skills) if matched_skills else "None"), styles["Normal"]))
    story.append(Paragraph("<b>Missing Skills:</b><br/>" + (", ".join(missing_skills) if missing_skills else "None"), styles["Normal"]))

    doc.build(story)


# ==========================
# MULTI-SCREEN ROUTING
# ==========================

# ---------------------------------------------------------
# SCREEN 1: DASHBOARD
# ---------------------------------------------------------
if menu == "Dashboard":
    st.subheader("🏠 Platform Dashboard")

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.markdown("""
        <div class="card">
            <h4>📊 Dataset Records</h4>
            <h2 style="color:#2563EB;">4,500</h2>
            <p>Balanced candidate training profiles.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="card">
            <h4>🤖 ML Model</h4>
            <h2 style="color:#2563EB;">Logistic Reg.</h2>
            <p>TF-IDF Feature Extraction.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_c:
        st.markdown("""
        <div class="card">
            <h4>🎯 Target Domains</h4>
            <h2 style="color:#2563EB;">5 Roles</h2>
            <p>Software, ML, Data & Web Dev.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_d:
        st.markdown("""
        <div class="card">
            <h4>📄 Parsers</h4>
            <h2 style="color:#2563EB;">PDF/DOCX/TXT</h2>
            <p>Native & OCR text extraction.</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    if st.session_state.has_analyzed:
        st.subheader("📋 Session Candidate Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.write(f"**Candidate Name:** {st.session_state.candidate_name or 'N/A'}")
        c2.write(f"**Target Role:** {st.session_state.target_role or 'N/A'}")
        c3.write(f"**Status:** {st.session_state.prediction_text or 'N/A'}")
        c4.write(f"**Resume Score:** {st.session_state.resume_score:.2f}%")
        st.info("💡 Use the sidebar menu to navigate between **Resume Analysis**, **Batch Screening**, **Analytics**, **Dataset Insights**, and **Role Skill Comparator**.")
    else:
        st.info("ℹ️ No candidate screened in this session yet. Select **Resume Analysis** or **Batch Screening** from the sidebar to evaluate resumes.")

    st.divider()
    st.subheader("🛠️ Processing Pipeline Architecture")
    st.markdown("""
    1. **Document Ingestion Layer**: Robust text extraction from `.pdf`, `.docx`, and `.txt` files with OCR fallback.
    2. **NLP Preprocessing**: Lowercasing, regex cleaning, URL/Email pattern stripping, and tokenization.
    3. **Skill & Keyword Extraction Engine**: Contextual regex matching against master tech skills catalog.
    4. **TF-IDF & Logistic Regression**: High-precision classification vectorizing resume content to classify suitability.
    5. **Multi-screen Analytics & Reporting**: Interactive Plotly visualizations and automated PDF summary generation.
    """)


# ---------------------------------------------------------
# SCREEN 2: RESUME ANALYSIS
# ---------------------------------------------------------
elif menu == "Resume Analysis":
    st.subheader("📄 Single Resume Screening & Analysis")

    left, right = st.columns([2, 1])

    with left:
        st.subheader("📤 Upload Resume")
        uploaded_file = st.file_uploader("Upload Resume File", type=["pdf", "docx", "txt"], key="single_upload")

        st.subheader("📄 Extracted Preview")
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                resume_text = extract_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = extract_docx(uploaded_file)
            elif uploaded_file.type == "text/plain":
                resume_text = extract_txt(uploaded_file)
            else:
                resume_text = ""

            if resume_text.strip():
                st.success("✅ Text extracted successfully")
                st.text_area("Resume Text Content", resume_text, height=220)
            else:
                st.error("❌ Could not extract text content")
        else:
            resume_text = ""
            st.info("Upload a resume file to inspect extracted content.")

    with right:
        st.subheader("👤 Candidate Info")
        if uploaded_file and resume_text.strip():
            candidate_name = extract_name(resume_text)
            candidate_email = extract_email(resume_text)
            candidate_phone = extract_phone(resume_text)
        else:
            candidate_name = ""
            candidate_email = ""
            candidate_phone = ""

        st.text_input("Name", value=candidate_name, disabled=True)
        st.text_input("Email", value=candidate_email, disabled=True)
        st.text_input("Phone", value=candidate_phone, disabled=True)
        role = st.selectbox("Target Role", ["Software Engineer", "Data Scientist", "ML Engineer", "Python Developer", "Web Developer"], key="single_role")

    st.divider()
    st.subheader("📋 Job Description Context (Optional)")
    job_description = st.text_area("Paste Job Description for custom keyword matching", height=120, placeholder="Python, SQL, Git, Machine Learning, Data Science...")

    analyze = st.button("🚀 Analyze Candidate Resume")

    if analyze:
        if not resume_text.strip():
            st.warning("⚠️ Please upload a resume first.")
        else:
            cleaned_resume = clean_text(resume_text)
            vector = tfidf.transform([cleaned_resume])
            prediction = model.predict(vector)[0]
            probability = model.predict_proba(vector)[0]
            confidence = round(max(probability) * 100, 2)

            matched_skills, missing_skills = extract_skills(cleaned_resume)
            ats_score = calculate_ats_score(matched_skills)

            if job_description.strip():
                jd_skills = extract_keywords(job_description)
                role_found = [skill for skill in jd_skills if skill in matched_skills]
                role_missing = [skill for skill in jd_skills if skill not in matched_skills]
                role_match = round(len(role_found) / len(jd_skills) * 100, 2) if jd_skills else 0.0
            else:
                role_found, role_missing, role_match = role_skill_analysis(cleaned_resume, role)

            resume_score = round((confidence + ats_score + role_match) / 3, 2)
            prediction_text = "Suitable Candidate" if prediction == 1 else "Not Suitable Candidate"

            st.session_state.ats_score = ats_score
            st.session_state.role_match = role_match
            st.session_state.confidence = confidence
            st.session_state.resume_score = resume_score
            st.session_state.has_analyzed = True
            st.session_state.candidate_name = candidate_name
            st.session_state.candidate_email = candidate_email
            st.session_state.candidate_phone = candidate_phone
            st.session_state.target_role = role
            st.session_state.prediction = prediction
            st.session_state.probability = list(probability)
            st.session_state.prediction_text = prediction_text
            st.session_state.matched_skills = matched_skills
            st.session_state.role_missing = role_missing
            st.session_state.missing_skills = missing_skills

    if st.session_state.has_analyzed:
        st.divider()
        st.subheader("📌 Screening Result")

        if st.session_state.prediction == 1:
            st.success("✅ Suitable Candidate")
        else:
            st.error("❌ Not Suitable Candidate")

        st.info(f"Model Prediction Confidence: {st.session_state.confidence:.2f}%")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Suitable Probability", f"{st.session_state.probability[1] * 100:.2f}%")
            st.progress(float(st.session_state.probability[1]))
        with col2:
            st.metric("Unsuitable Probability", f"{st.session_state.probability[0] * 100:.2f}%")
            st.progress(float(st.session_state.probability[0]))

        st.divider()
        l_col, r_col = st.columns(2)
        with l_col:
            st.subheader("✅ Matched Technical Skills")
            if st.session_state.matched_skills:
                for skill in st.session_state.matched_skills:
                    st.success(skill.title())
            else:
                st.info("No matching skills found.")

        with r_col:
            st.subheader("❌ Missing Role Skills")
            if st.session_state.role_missing:
                for skill in st.session_state.role_missing:
                    st.error(skill.title())
            else:
                st.success("No missing skills for targeted role.")

        st.divider()
        st.subheader("💡 Improvement Recommendations")
        if st.session_state.role_missing:
            st.warning("Recommended skills to add:")
            for skill in st.session_state.role_missing:
                st.write(f"• {skill.title()}")

        create_report(
            "Resume_Report.pdf",
            st.session_state.candidate_name,
            st.session_state.candidate_email,
            st.session_state.candidate_phone,
            st.session_state.target_role,
            st.session_state.prediction_text,
            st.session_state.confidence,
            st.session_state.ats_score,
            st.session_state.role_match,
            st.session_state.resume_score,
            st.session_state.matched_skills,
            st.session_state.role_missing
        )

        with open("Resume_Report.pdf", "rb") as pdf_file:
            st.download_button("📥 Download Resume Summary (PDF)", pdf_file, "Resume_Report.pdf", "application/pdf")


# ---------------------------------------------------------
# SCREEN 3: BATCH SCREENING (LEADERBOARD)
# ---------------------------------------------------------
elif menu == "Batch Screening":
    st.subheader("📁 Batch Resume Screening & Leaderboard")
    st.markdown("Upload multiple candidate resumes to automatically screen, score, and rank candidates.")

    b_files = st.file_uploader("Upload Resumes (Multiple files supported)", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    b_role = st.selectbox("Target Role for Batch Evaluation", ["Software Engineer", "Data Scientist", "ML Engineer", "Python Developer", "Web Developer"], key="batch_role")
    b_jd = st.text_area("Optional Batch Job Description", height=100, placeholder="Paste job description to customize batch evaluation criteria...")

    run_batch = st.button("🚀 Process & Rank Batch Resumes")

    if run_batch:
        if not b_files:
            st.warning("⚠️ Please select at least one resume file to run batch screening.")
        else:
            results = []
            progress_bar = st.progress(0)

            for idx, file_obj in enumerate(b_files):
                fname = file_obj.name
                ftype = file_obj.type

                if ftype == "application/pdf" or fname.endswith(".pdf"):
                    text = extract_pdf(file_obj)
                elif ftype == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or fname.endswith(".docx"):
                    text = extract_docx(file_obj)
                else:
                    text = extract_txt(file_obj)

                if text.strip():
                    name = extract_name(text)
                    email = extract_email(text)
                    phone = extract_phone(text)
                    cleaned = clean_text(text)

                    vec = tfidf.transform([cleaned])
                    pred = model.predict(vec)[0]
                    prob = model.predict_proba(vec)[0]
                    conf = round(max(prob) * 100, 2)

                    matched, missing = extract_skills(cleaned)
                    ats = calculate_ats_score(matched)

                    if b_jd.strip():
                        jd_k = extract_keywords(b_jd)
                        found_k = [s for s in jd_k if s in matched]
                        r_match = round(len(found_k) / len(jd_k) * 100, 2) if jd_k else 0.0
                    else:
                        found_k, missing_k, r_match = role_skill_analysis(cleaned, b_role)

                    res_score = round((conf + ats + r_match) / 3, 2)
                    status_text = "Suitable" if pred == 1 else "Not Suitable"

                    results.append({
                        "File Name": fname,
                        "Candidate Name": name,
                        "Email": email,
                        "Phone": phone,
                        "Target Role": b_role,
                        "ATS Score (%)": ats,
                        "Role Match (%)": r_match,
                        "Model Confidence (%)": conf,
                        "Resume Score (%)": res_score,
                        "Status": status_text
                    })

                progress_bar.progress((idx + 1) / len(b_files))

            if results:
                df_results = pd.DataFrame(results)
                df_results = df_results.sort_values(by="Resume Score (%)", ascending=False).reset_index(drop=True)
                df_results.index += 1
                df_results.index.name = "Rank"

                st.session_state.batch_results = df_results
                st.success(f"🎉 Processed and ranked {len(results)} resumes successfully!")

    if "batch_results" in st.session_state and st.session_state.batch_results is not None:
        st.divider()
        st.subheader("🏆 Candidate Leaderboard")

        df_res = st.session_state.batch_results
        st.dataframe(df_res, use_container_width=True)

        st.divider()
        st.subheader("🥇 Top Candidate Highlights")
        top_cols = st.columns(min(3, len(df_res)))
        for i, col in enumerate(top_cols):
            row = df_res.iloc[i]
            with col:
                st.markdown(f"""
                <div class="card">
                    <h3>Rank #{i+1} : {row['Candidate Name']}</h3>
                    <p><b>Role:</b> {row['Target Role']}</p>
                    <p><b>Status:</b> {row['Status']}</p>
                    <h2 style="color:#2563EB;">Score: {row['Resume Score (%)']:.2f}%</h2>
                </div>
                """, unsafe_allow_html=True)

        csv_data = df_res.to_csv().encode('utf-8')
        st.download_button("📥 Download Leaderboard as CSV", csv_data, "batch_screening_leaderboard.csv", "text/csv")


# ---------------------------------------------------------
# SCREEN 4: ANALYTICS
# ---------------------------------------------------------
elif menu == "Analytics":
    st.subheader("📈 Interactive Candidate Analytics")

    ats_score = st.session_state.ats_score
    role_match = st.session_state.role_match
    confidence = st.session_state.confidence
    resume_score = st.session_state.resume_score
    matched_skills = st.session_state.matched_skills
    missing_skills = st.session_state.missing_skills

    if not st.session_state.has_analyzed:
        st.info("ℹ️ Displaying sample analytics. Screen a candidate under **Resume Analysis** to load live candidate data.")

    chart1, chart2 = st.columns(2)

    with chart1:
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=ats_score if st.session_state.has_analyzed else 78.5,
                title={"text": "ATS Compatibility Score (%)"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#2563EB"},
                    "steps": [
                        {"range": [0, 40], "color": "#FCA5A5"},
                        {"range": [40, 70], "color": "#FDE68A"},
                        {"range": [70, 100], "color": "#86EFAC"}
                    ]
                }
            )
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with chart2:
        m_len = len(matched_skills) if st.session_state.has_analyzed else 8
        m_miss = len(missing_skills) if st.session_state.has_analyzed else 4
        fig = px.pie(
            values=[m_len, m_miss],
            names=["Matched Skills", "Missing Skills"],
            hole=0.60,
            title="Skill Matching Distribution",
            color_discrete_sequence=["#2563EB", "#EF4444"]
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("🎯 Performance Radar Matrix")
    categories = ["ATS", "Role Match", "Confidence", "Resume Score"]
    values = [ats_score, role_match, confidence, resume_score] if st.session_state.has_analyzed else [78, 85, 92, 85]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill="toself", name="Candidate Profile"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=450)
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------
# SCREEN 5: DATASET INSIGHTS
# ---------------------------------------------------------
elif menu == "Dataset Insights":
    st.subheader("🗃️ Dataset Insights & ML Model Metrics")

    if dataset_df is not None:
        d_col1, d_col2, d_col3 = st.columns(3)
        with d_col1:
            st.metric("Total Resumes in Dataset", f"{len(dataset_df):,}")
        with d_col2:
            suitable_cnt = len(dataset_df[dataset_df['label'] == 1])
            st.metric("Suitable Resumes (Label=1)", f"{suitable_cnt:,} ({suitable_cnt/len(dataset_df)*100:.1f}%)")
        with d_col3:
            unsuitable_cnt = len(dataset_df[dataset_df['label'] == 0])
            st.metric("Unsuitable Resumes (Label=0)", f"{unsuitable_cnt:,} ({unsuitable_cnt/len(dataset_df)*100:.1f}%)")

        st.divider()
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("📊 Class Distribution")
            fig = px.pie(
                dataset_df,
                names="label",
                title="Class Label Balance (1=Suitable, 0=Unsuitable)",
                color_discrete_sequence=["#EF4444", "#2563EB"]
            )
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("🎓 Highest Degree Distribution")
            if "highest_degree" in dataset_df.columns:
                degree_counts = dataset_df['highest_degree'].value_counts().reset_index()
                degree_counts.columns = ["Degree", "Count"]
                fig = px.bar(degree_counts, x="Degree", y="Count", color="Count", color_continuous_scale="Blues")
                st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("📋 Dataset Preview Table")
        st.dataframe(dataset_df.head(100), use_container_width=True)
    else:
        st.info("Dataset file `ml_resume_dataset_4500.csv` not found in workspace.")


# ---------------------------------------------------------
# SCREEN 6: ROLE SKILL COMPARATOR
# ---------------------------------------------------------
elif menu == "Role Skill Comparator":
    st.subheader("⚔️ Role Requirements & Skill Gap Comparator")
    st.markdown("Compare skill requirements across all target roles or test custom candidate skills.")

    comp_data = []
    for r_name, r_skills in ROLE_SKILLS.items():
        comp_data.append({
            "Target Role": r_name,
            "Total Core Skills": len(r_skills),
            "Key Required Stack": ", ".join([s.title() for s in r_skills])
        })
    st.table(pd.DataFrame(comp_data))

    st.divider()
    st.subheader("🔍 Interactive Skill Gap Analyzer")
    sample_text = st.text_area("Paste Candidate Resume Bio or Skill List", height=130, placeholder="Python, SQL, Machine Learning, Pandas, NumPy, Git, Docker...")

    if st.button("⚡ Compare Across All 5 Roles"):
        if not sample_text.strip():
            st.warning("Please paste skill text first.")
        else:
            cleaned = clean_text(sample_text)
            c_scores = {}
            for r_name in ROLE_SKILLS.keys():
                found, missing, score = role_skill_analysis(cleaned, r_name)
                c_scores[r_name] = score

            df_scores = pd.DataFrame(list(c_scores.items()), columns=["Target Role", "Match Percentage (%)"])
            fig = px.bar(df_scores, x="Target Role", y="Match Percentage (%)", color="Match Percentage (%)", color_continuous_scale="Blues", text="Match Percentage (%)")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)


st.divider()
st.markdown("""
<div style="text-align:center; color:gray; padding:15px; font-size:14px;">
    Resume Screening Platform • Machine Learning • Python • Streamlit
</div>
""", unsafe_allow_html=True)