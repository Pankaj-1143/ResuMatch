"""
app.py
------
Module 7: Streamlit UI / orchestration layer for the Resume vs Job
Description Matcher.

UI REDESIGN NOTE
-----------------
This file's *presentation* has been rebuilt to look like a premium SaaS
dashboard (top nav, hero banner, metric cards, badges, charts-in-cards,
ATS score ring, animated loading sequence). All styling/markup lives in
ui.py.

Nothing below touches the backend contract:
    - Same imports, same module names (pdf_reader, text_processing,
      skill_extractor, matcher, suggestions, charts)
    - Same function calls, same argument order, same variable names
      (resume_text_raw, jd_clean, score, label, color, matched, missing,
      matched_categorized, missing_categorized, skill_suggestions,
      ats_result, resume_tokens, word_count, reading_time, etc.)
    - Same validation / error / st.stop() flow as the original app.py

Cards are now built with `ui.card(...)` used as a context manager
(`with ui.card(...): ...`) instead of the old card_open()/card_close()
pair — that pattern split an HTML <div> across two separate
st.markdown() calls, which doesn't actually nest the widgets in
between and was the source of stray HTML fragments leaking onto the
page. See ui.py for details.

Assumed function signatures from earlier modules (unchanged):
    pdf_reader.validate_pdf_file(uploaded_file) -> str | None
    pdf_reader.extract_text_from_pdf(uploaded_file) -> (str | None, str | None)
    text_processing.clean_text(text) -> str
    text_processing.tokenize(cleaned_text) -> list[str]
    text_processing.count_words(text) -> int
    text_processing.estimate_reading_time(text) -> int
"""

import streamlit as st

from pdf_reader import validate_pdf_file, extract_text_from_pdf
from text_processing import clean_text, tokenize, count_words, estimate_reading_time
from skill_extractor import compare_skills, categorize_skills
from matcher import get_score_details
from suggestions import get_skill_suggestions, check_ats_friendliness
from charts import plot_skills_bar_chart, plot_match_pie_chart, plot_keyword_frequency_chart

import ui


# ---------------------------------------------------------------------------
# Page config (must be the first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Resume Matcher",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

ui.load_css(dark=st.session_state.dark_mode)


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;margin-bottom:18px;">'
        '<div class="topnav-logo">📄</div>'
        '<span style="font-weight:800;font-size:1.05rem;">Resume Matcher</span>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.toggle("🌙 Dark Mode", key="dark_mode")

    st.radio(
        "Navigate",
        ["Dashboard", "Upload Resume", "Analysis", "Reports", "History", "Settings"],
        label_visibility="collapsed",
    )
    st.divider()
    with st.expander("ℹ️ About"):
        st.write(
            "Compares your resume against a job description using TF-IDF "
            "similarity and skill matching — no paid AI APIs involved. "
            "Everything runs locally with traditional NLP techniques."
        )
    with st.expander("❓ Help"):
        st.write("Upload a PDF resume, paste a job description, then click **Analyze Resume**.")
    st.caption("Version 1.0")


# ---------------------------------------------------------------------------
# Top nav + Hero
# ---------------------------------------------------------------------------
ui.top_nav(app_name="Resume Matcher")

ui.hero_banner(
    title="Resume vs Job Description Matcher",
    subtitle="Analyze your resume using NLP and compare it with any job description.",
    icon="📄",
    stats=[("100%", "Local NLP"), ("0", "External APIs used"), ("PDF", "Supported format")],
)


# ---------------------------------------------------------------------------
# Input card: Upload Resume + Job Description
# ---------------------------------------------------------------------------
ui.section_title("Get started", "Upload your resume and paste the job description below.")

with ui.card():
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**📤 Upload Resume**")
        uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

    with col_right:
        st.markdown("**📝 Paste Job Description**")
        jd_text_input = st.text_area(
            "Job description",
            height=220,
            placeholder="Paste the full job description here...",
            label_visibility="collapsed",
        )

    st.write("")
    analyze_clicked = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
if analyze_clicked:
    # --- Validation (unchanged) ---
    if uploaded_file is None:
        st.error("Please upload a resume PDF before analyzing.")
        st.stop()

    if not jd_text_input or not jd_text_input.strip():
        st.error("Please paste a job description before analyzing.")
        st.stop()

    validation_error = validate_pdf_file(uploaded_file)
    if validation_error:
        st.error(validation_error)
        st.stop()

    # --- Loading experience: step messages + progress bar ---
    loading_placeholder = st.empty()
    loading_steps = [
        "Extracting resume...",
        "Cleaning text...",
        "Finding skills...",
        "Calculating similarity...",
        "Generating suggestions...",
        "Preparing dashboard...",
    ]

    # Step 1: extraction happens for real, mid-sequence
    results_holder = {}

    def _run_step(i: int, label: str) -> None:
        if i == 0:
            resume_text_raw, extraction_error = extract_text_from_pdf(uploaded_file)
            results_holder["resume_text_raw"] = resume_text_raw
            results_holder["extraction_error"] = extraction_error

    ui.run_loading_sequence(loading_placeholder, loading_steps, step_fn=_run_step)

    resume_text_raw = results_holder.get("resume_text_raw")
    extraction_error = results_holder.get("extraction_error")

    if extraction_error:
        st.error(extraction_error)
        st.stop()

    if not resume_text_raw or not resume_text_raw.strip():
        st.error("No readable text could be extracted from this PDF. Try a different file.")
        st.stop()

    resume_clean = clean_text(resume_text_raw)
    jd_clean = clean_text(jd_text_input)

    resume_tokens = tokenize(resume_clean)
    word_count = count_words(resume_text_raw)
    reading_time = estimate_reading_time(resume_text_raw)

    score, label, color = get_score_details(resume_clean, jd_clean)

    matched, missing, resume_skills, jd_skills = compare_skills(resume_text_raw, jd_text_input)
    matched_categorized = categorize_skills(matched)
    missing_categorized = categorize_skills(missing)

    skill_suggestions = get_skill_suggestions(sorted(missing))
    ats_result = check_ats_friendliness(resume_text_raw)

    st.success("Analysis complete!")
    st.write("")

    # --- Metric cards -------------------------------------------------
    ui.section_title("📊 Dashboard", f"Resume: ~{word_count} words · ~{reading_time} min read")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        ui.metric_card("🎯", "Resume Match", f"{score}%", label, color="#22C55E")
    with m2:
        ui.metric_card("✅", "Matched Skills", str(len(matched)), "Skills found in your resume", color="#2563EB")
    with m3:
        ui.metric_card("⚠️", "Missing Skills", str(len(missing)), "Skills to add or highlight", color="#F59E0B")
    with m4:
        ui.metric_card("🛡️", "ATS Score", f"{ats_result['score']}%", "Applicant tracking friendliness", color="#8B5CF6")

    st.write("")
    st.progress(min(int(score), 100) / 100)
    st.write("")

    # --- Charts ---------------------------------------------------------
    ui.section_title("📈 Visual Breakdown")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        with ui.card("Matched vs Missing", "How your resume's skills stack up against the JD."):
            chart_tab1, chart_tab2 = st.tabs(["Bar Chart", "Keyword Frequency"])
            with chart_tab1:
                st.pyplot(plot_skills_bar_chart(len(matched), len(missing)))
            with chart_tab2:
                st.pyplot(plot_keyword_frequency_chart(resume_tokens, top_n=10))

    with chart_col2:
        with ui.card("Skill Distribution", "Overall match score as a proportion."):
            st.pyplot(plot_match_pie_chart(score))

    st.write("")

    # --- Skills section ---------------------------------------------------
    ui.section_title("🧩 Skills")
    skills_col1, skills_col2 = st.columns(2)

    with skills_col1:
        with ui.card("✅ Matched Skills"):
            ui.skill_badges(matched, matched=True)

    with skills_col2:
        with ui.card("❌ Missing Skills"):
            ui.skill_badges(missing, matched=False)

    with st.expander("View skills by category"):
        st.markdown("**Matched, by category:**")
        if matched_categorized:
            for category, skills in matched_categorized.items():
                st.write(f"- **{category}**: {', '.join(skills)}")
        else:
            st.write("None")

        st.markdown("**Missing, by category:**")
        if missing_categorized:
            for category, skills in missing_categorized.items():
                st.write(f"- **{category}**: {', '.join(skills)}")
        else:
            st.write("None")

    st.write("")

    # --- Suggestions ------------------------------------------------------
    ui.section_title("💡 Suggestions to Improve Your Resume")
    if skill_suggestions:
        for suggestion in skill_suggestions:
            ui.info_card("Suggestion", suggestion, icon="💡")
    else:
        st.success("Your resume already covers all the skills mentioned in this job description!")

    st.write("")

    # --- ATS report ---------------------------------------------------------
    ui.section_title("🔎 ATS Friendliness Report")
    with ui.card():
        ring_col, detail_col = st.columns([1, 2])
        with ring_col:
            ui.score_ring(ats_result["score"], label="ATS Score")
        with detail_col:
            if ats_result["issues"]:
                st.markdown("**Issues to fix:**")
                for issue in ats_result["issues"]:
                    st.warning(issue)
            if ats_result["passed"]:
                st.markdown("**Checks passed:**")
                for check in ats_result["passed"]:
                    st.write(f"✔️ {check}")

else:
    st.info("Upload a resume and paste a job description, then click **Analyze Resume** to get started.")


ui.footer(version="1.0")