"""
suggestions.py
---------------
Module 5: Actionable suggestions for the Resume vs Job Description Matcher.

Responsibilities:
    - Map missing skills to specific, actionable improvement advice.
    - Bonus: run basic ATS (Applicant Tracking System) friendliness
      checks on the raw resume text (missing sections, no email, no
      phone number, no quantified achievements, etc.).
"""

import re
from typing import Dict, List


# ---------------------------------------------------------------------------
# Missing-skill -> advice mapping
# ---------------------------------------------------------------------------
# Specific, tailored advice for the most common skills. Anything not in
# this dict falls back to a generic template (see get_skill_suggestions).

_SKILL_ADVICE: Dict[str, str] = {
    "docker": "Add a Docker project — containerize one of your existing apps and mention it.",
    "kubernetes": "Mention any experience orchestrating containers, or deploy a small project on Kubernetes/Minikube.",
    "aws": "Mention cloud deployment experience — even a personal project hosted on AWS (S3, EC2, Lambda) counts.",
    "azure": "Highlight any experience deploying to Azure, or take a small project through Azure App Service.",
    "gcp": "Highlight any experience with Google Cloud Platform, or deploy a project on GCP's free tier.",
    "sql": "Include database-related projects — even a simple CRUD app with SQL queries strengthens this.",
    "react": "Add frontend project experience — a React app in your portfolio would directly address this.",
    "node.js": "Add a backend project built with Node.js/Express to show server-side JavaScript experience.",
    "git": "Make sure your resume mentions Git/GitHub — link to your repositories if you have them.",
    "machine learning": "Include a machine learning project, even a small Kaggle-style one, with the models/libraries used.",
    "ci/cd": "Mention any experience setting up automated pipelines (GitHub Actions, Jenkins, GitLab CI).",
    "linux": "Mention comfort with the Linux command line — most backend/DevOps roles expect this.",
    "rest api": "Explicitly mention building or consuming REST APIs in your project descriptions.",
    "graphql": "If you've used GraphQL anywhere, call it out explicitly — it's a differentiator many candidates miss.",
    "mongodb": "Add a project using MongoDB or another NoSQL database to demonstrate this.",
    "django": "Build or highlight a project using Django to show Python backend framework experience.",
    "flask": "Build or highlight a project using Flask to show Python backend framework experience.",
    "tensorflow": "Include a project using TensorFlow, even a small model training/inference example.",
    "pytorch": "Include a project using PyTorch, even a small model training/inference example.",
    "typescript": "Mention or add TypeScript to an existing JavaScript project to show typed-code experience.",
}

_GENERIC_TEMPLATE = "Consider adding a project or coursework that demonstrates {skill} experience."


def get_skill_suggestions(missing_skills: List[str]) -> List[str]:
    """
    Generate improvement suggestions for a list of missing skills.

    Args:
        missing_skills: Skills required by the JD but absent from the resume.

    Returns:
        A list of suggestion strings, one per missing skill, in the same
        order as the input list.
    """
    suggestions: List[str] = []

    for skill in missing_skills:
        key = skill.lower().strip()
        if key in _SKILL_ADVICE:
            suggestions.append(f"Missing {skill.title()} → {_SKILL_ADVICE[key]}")
        else:
            suggestions.append(
                f"Missing {skill.title()} → {_GENERIC_TEMPLATE.format(skill=skill.title())}"
            )

    return suggestions


# ---------------------------------------------------------------------------
# Bonus: ATS-friendliness checker
# ---------------------------------------------------------------------------

_EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
# Matches a run of digits with common phone separators (spaces, dashes,
# dots, parentheses) that contains at least 7 actual digits overall.
# This is intentionally loose — the follow-up digit-count check is what
# actually validates it, rather than trying to enforce a rigid format.
_PHONE_CANDIDATE_PATTERN = re.compile(r"(\+?\d[\d\-.\s()]{6,}\d)")
_QUANTIFIED_PATTERN = re.compile(r"\b\d+(\.\d+)?\s?(%|percent|x|users|projects|hours|days|weeks|months|years)\b", re.IGNORECASE)

_EXPECTED_SECTIONS = [
    "experience", "education", "skills", "projects",
]


def _has_phone_number(text: str) -> bool:
    """
    Return True if the text contains something that looks like a phone
    number: a run of digits (allowing spaces/dashes/dots/parentheses as
    separators) with at least 7 and at most 15 actual digits.
    """
    for candidate in _PHONE_CANDIDATE_PATTERN.findall(text):
        digit_count = sum(ch.isdigit() for ch in candidate)
        if 7 <= digit_count <= 15:
            return True
    return False


def check_ats_friendliness(resume_text: str) -> Dict[str, object]:
    """
    Run basic ATS (Applicant Tracking System) friendliness checks on raw
    resume text. These are heuristic, traditional-NLP checks — not a
    replacement for a real ATS, but useful directional feedback.

    Args:
        resume_text: Raw (uncleaned) resume text, so punctuation like
            "@" and "%" is still present for pattern matching.

    Returns:
        A dict with:
            - "score": int, 0-100 ATS-friendliness score.
            - "issues": List[str], human-readable problems found.
            - "passed": List[str], checks that passed.
    """
    issues: List[str] = []
    passed: List[str] = []

    if not resume_text or not resume_text.strip():
        return {"score": 0, "issues": ["Resume text is empty."], "passed": []}

    text_lower = resume_text.lower()
    total_checks = 0
    checks_passed = 0

    # Check 1: contact email present
    total_checks += 1
    if _EMAIL_PATTERN.search(resume_text):
        checks_passed += 1
        passed.append("Email address found.")
    else:
        issues.append("No email address detected — recruiters and ATS systems look for this.")

    # Check 2: phone number present
    total_checks += 1
    if _has_phone_number(resume_text):
        checks_passed += 1
        passed.append("Phone number found.")
    else:
        issues.append("No phone number detected.")

    # Check 3: quantified achievements (numbers, %, metrics)
    total_checks += 1
    if _QUANTIFIED_PATTERN.search(resume_text):
        checks_passed += 1
        passed.append("Quantified achievements found (numbers/metrics).")
    else:
        issues.append("No quantified results found — try adding metrics (e.g. 'improved performance by 30%').")

    # Check 4: expected sections present
    for section in _EXPECTED_SECTIONS:
        total_checks += 1
        if section in text_lower:
            checks_passed += 1
            passed.append(f"'{section.title()}' section detected.")
        else:
            issues.append(f"No clear '{section.title()}' section detected.")

    # Check 5: reasonable length (too short = likely incomplete, too long = may not parse well)
    total_checks += 1
    word_count = len(resume_text.split())
    if 150 <= word_count <= 1200:
        checks_passed += 1
        passed.append(f"Resume length looks reasonable ({word_count} words).")
    else:
        issues.append(
            f"Resume length ({word_count} words) may be too short or too long for ideal ATS parsing."
        )

    score = round((checks_passed / total_checks) * 100)

    return {"score": score, "issues": issues, "passed": passed}
