# 📄 Resume Screening System

A Machine Learning-based Resume Screening System that automates the process of analyzing resumes and predicting the most suitable job role. The system extracts text from uploaded resumes, preprocesses the content, classifies the resume using a trained ML model, and highlights missing skills to assist recruiters in the hiring process.

---

## 🚀 Features

- Upload resumes in PDF format
- Automatic resume text extraction
- Resume text preprocessing
- Job role prediction using Machine Learning
- Missing skills identification
- ATS-friendly resume analysis
- Simple and interactive Streamlit interface

---

## 🛠️ Technologies Used

- Python
- Streamlit
- Scikit-learn
- Pandas
- NumPy
- NLTK
- Joblib
- PyMuPDF (fitz)
- Python-docx
- Pytesseract
- Pillow

---

## 📂 Project Structure

```
Resume_Screening_System/
│── app.py
│── requirements.txt
│── resume_model.pkl
│── tfidf_vectorizer.pkl
│── label_encoder.pkl
│── ats_resume_skillset.csv
│── README.md
```

---

## ⚙️ Installation

1. Clone the repository

```bash
git clone https://github.com/your-username/Resume-Screening-System.git
```

2. Navigate to the project folder

```bash
cd Resume-Screening-System
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Run the application

```bash
streamlit run app.py
```

---

## 📊 Workflow

1. Upload Resume
2. Extract Resume Text
3. Preprocess Text
4. Convert Text using TF-IDF
5. Predict Job Role
6. Analyze Resume Skills
7. Display Results

---

## 🎯 Advantages

- Reduces manual screening time
- Improves recruitment efficiency
- Consistent resume evaluation
- User-friendly interface
- Fast and accurate predictions

---

## 🔮 Future Scope

- Job Description Matching
- Resume Ranking
- AI-based Skill Recommendation
- Deep Learning Models
- Cloud Deployment
- Multi-language Resume Support

---

## 📜 License

This project is developed for educational and learning purposes.
