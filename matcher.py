"""
matcher.py
----------
Module 4: Resume <-> Job Description similarity scoring for the
Resume vs Job Description Matcher.

Responsibilities:
    - Convert cleaned resume + JD text into TF-IDF vectors.
    - Compute cosine similarity and convert it into a 0-100% match score.
    - Provide a human-readable label ("Excellent/Good/Fair/Weak Match")
      and a UI color for that score, for use in app.py.

This module expects text that has already been cleaned by
text_processing.clean_text() for the most reliable similarity signal,
but will still work on raw text.
"""

from typing import Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------------------------
# Score thresholds and display mapping
# ---------------------------------------------------------------------------
# (minimum_score_inclusive, label, color) — checked in descending order.
_SCORE_BANDS = (
    (75.0, "Excellent Match", "#2ecc71"),  # green
    (50.0, "Good Match", "#3498db"),       # blue
    (25.0, "Fair Match", "#f39c12"),       # orange
    (0.0, "Weak Match", "#e74c3c"),        # red
)


# ---------------------------------------------------------------------------
# Core matching
# ---------------------------------------------------------------------------

def calculate_match_score(resume_text: str, jd_text: str) -> float:
    """
    Calculate a similarity score between resume text and job description
    text using TF-IDF vectorization and cosine similarity.

    Args:
        resume_text: Cleaned resume text.
        jd_text: Cleaned job description text.

    Returns:
        A similarity percentage rounded to 2 decimal places (0.0 - 100.0).
        Returns 0.0 if either input is empty/whitespace, or if TF-IDF
        vectorization fails (e.g. vocabulary is empty after cleaning).
    """
    if not resume_text or not jd_text:
        return 0.0

    if not resume_text.strip() or not jd_text.strip():
        return 0.0

    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        score = round(float(similarity) * 100, 2)
        return max(0.0, min(score, 100.0))
    except ValueError:
        # Raised by scikit-learn when the vocabulary is empty — e.g. both
        # texts consisted entirely of stopwords/numbers that got stripped.
        return 0.0


# ---------------------------------------------------------------------------
# Score labeling
# ---------------------------------------------------------------------------

def get_score_label(score: float) -> str:
    """
    Map a match score to a human-readable label.

    Args:
        score: Match score between 0.0 and 100.0.

    Returns:
        One of "Excellent Match", "Good Match", "Fair Match", "Weak Match".
    """
    for minimum, label, _color in _SCORE_BANDS:
        if score >= minimum:
            return label
    return "Weak Match"  # Fallback, should be unreachable given 0.0 floor.


def get_score_color(score: float) -> str:
    """
    Map a match score to a hex color code for UI display (e.g. metric
    cards, progress bars in app.py).

    Args:
        score: Match score between 0.0 and 100.0.

    Returns:
        A hex color string, e.g. "#2ecc71".
    """
    for minimum, _label, color in _SCORE_BANDS:
        if score >= minimum:
            return color
    return "#e74c3c"  # Fallback, should be unreachable given 0.0 floor.


def get_score_details(resume_text: str, jd_text: str) -> Tuple[float, str, str]:
    """
    Convenience function that computes the score and its label/color in
    one call, for direct use in app.py.

    Args:
        resume_text: Cleaned resume text.
        jd_text: Cleaned job description text.

    Returns:
        A tuple of (score, label, color).
    """
    score = calculate_match_score(resume_text, jd_text)
    label = get_score_label(score)
    color = get_score_color(score)
    return score, label, color
