# 📄 Resume vs Job Description Matcher

A Streamlit web app that analyzes how well a resume matches a job description — using traditional NLP techniques only (TF-IDF, cosine similarity, and regex-based skill matching). No paid AI APIs involved.

## Project Description

Upload a PDF resume and paste a job description, and the app will:
- Calculate an overall match score using TF-IDF + cosine similarity
- Extract and compare technical skills from both texts
- Highlight matched and missing skills, grouped by category
- Suggest specific, actionable improvements based on skill gaps
- Run a basic ATS (Applicant Tracking System) friendliness check
- Visualize results with bar charts, pie charts, and keyword frequency charts

Everything runs locally using classical NLP — no OpenAI, Gemini, Claude, or Groq API calls.

## Features

- **PDF resume upload** with validation for empty, corrupted, or password-protected files
- **Text cleaning pipeline** (lowercase, punctuation/number removal, stopword removal via NLTK)
- **TF-IDF match scoring** with a labeled score band (Excellent / Good / Fair / Weak Match)
- **Skill extraction & comparison** against a 100+ skill database across 9 categories
- **Actionable suggestions** for each missing skill
- **ATS friendliness checker** — flags missing sections, contact info, and quantified achievements
- **Interactive charts** — matched vs missing bar chart, match percentage pie chart, resume keyword frequency chart
- **Light/Dark mode toggle** built into the sidebar
- Clean, modular codebase — no logic inside the UI layer

## Libraries Used

| Library | Purpose |
|---|---|
| `streamlit` | Web app UI framework |
| `pdfplumber` | PDF text extraction |
| `scikit-learn` | TF-IDF vectorization + cosine similarity |
| `nltk` | Stopword removal, text preprocessing |
| `pandas` | Data handling |
| `matplotlib` | Bar, pie, and frequency charts |

## Installation

```bash
# 1. Clone or download this project
cd Resume_Matcher

# 2. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download required NLTK data (one-time)
python -c "import nltk; nltk.download('stopwords')"
```

## How to Run

```bash
streamlit run app.py
```

This opens the app in your browser, usually at `http://localhost:8501`.

1. Upload your resume (PDF only) in the left panel
2. Paste the job description in the right panel
3. Click **Analyze Resume**
4. Review your match score, matched/missing skills, suggestions, and charts

## Folder Structure

```
Resume_Matcher/
│
├── app.py               # Streamlit UI — layout only, calls other modules
├── pdf_reader.py         # PDF upload + text extraction
├── text_processing.py    # Text cleaning (lowercase, stopwords, etc.)
├── skill_extractor.py    # Skill database + skill matching (100+ skills, 9 categories)
├── matcher.py             # TF-IDF + Cosine Similarity scoring
├── suggestions.py        # Missing-skill suggestions + ATS friendliness checker
├── charts.py              # Matplotlib bar/pie/frequency charts
├── requirements.txt
├── README.md
└── sample_resume.pdf
```

## Screenshots

_Add screenshots of the app here once you've run it locally._

```
[ Screenshot: Upload & Job Description input screen ]
[ Screenshot: Dashboard with match score and metric cards ]
[ Screenshot: Matched/Missing skills and charts ]
[ Screenshot: Dark mode view ]
```

## Future Improvements

- Support for `.docx` resume uploads, not just PDF
- Download the full analysis report as a PDF
- Word cloud visualization of resume content
- Support comparing a resume against multiple job descriptions at once
- Resume section detection using layout/formatting cues, not just keyword search
- Configurable/expandable skill database (e.g. load from an external JSON file)

## License

This project is open-source and available under the [MIT License](https://opensource.org/licenses/MIT).
