"""
skill_extractor.py
-------------------
Module 3: Skill database and skill-matching logic for the
Resume vs Job Description Matcher.

Responsibilities:
    - Maintain a categorized database of 100+ technical skills.
    - Extract skills mentioned in a block of text using whole-phrase
      regex matching (so "Java" won't falsely match inside "JavaScript").
    - Compare resume skills against job description skills.
    - Group a set of skills by category for dashboard display.
"""

import re
from typing import Dict, List, Set, Tuple


# ---------------------------------------------------------------------------
# Skill Database (100+ skills across 9 categories)
# ---------------------------------------------------------------------------

SKILL_CATEGORIES: Dict[str, List[str]] = {
    "Programming Languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c",
        "go", "golang", "rust", "kotlin", "swift", "php", "ruby", "scala",
        "r", "matlab", "perl", "dart", "sql", "bash", "shell scripting",
    ],
    "Frontend": [
        "html", "css", "react", "react.js", "angular", "vue", "vue.js",
        "next.js", "tailwind", "tailwind css", "bootstrap", "sass",
        "jquery", "redux", "webpack", "vite", "svelte", "material ui",
    ],
    "Backend": [
        "node.js", "express", "express.js", "django", "flask", "fastapi",
        "spring", "spring boot", "asp.net", ".net", "laravel", "nestjs",
        "graphql", "rest api", "grpc", "ruby on rails",
    ],
    "Database": [
        "mongodb", "mysql", "postgresql", "postgres", "sqlite", "oracle",
        "redis", "cassandra", "dynamodb", "firebase", "elasticsearch",
        "mariadb", "neo4j", "database design", "nosql",
    ],
    "Cloud": [
        "aws", "azure", "gcp", "google cloud", "amazon web services",
        "cloudformation", "s3", "ec2", "lambda", "cloud deployment",
        "cloud computing", "heroku", "vercel", "netlify",
    ],
    "DevOps": [
        "docker", "kubernetes", "jenkins", "ci/cd", "terraform", "ansible",
        "linux", "nginx", "git", "github", "gitlab", "bitbucket",
        "prometheus", "grafana", "devops", "helm",
    ],
    "AI/ML": [
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "keras", "scikit-learn", "pandas", "numpy", "opencv", "nltk",
        "spacy", "data structures", "algorithms", "data analysis",
        "data visualization", "matplotlib", "seaborn", "hadoop", "spark",
        "airflow", "llm", "nlp", "computer vision", "generative ai",
        "langchain", "artificial intelligence", "neural networks",
    ],
    "Testing & Tools": [
        "pytest", "junit", "selenium", "unit testing", "postman",
        "jira", "figma", "vs code", "cypress", "jest", "mocha",
        "test automation", "agile", "scrum",
    ],
    "Other": [
        "microservices", "system design", "object oriented programming",
        "oop", "api development", "web sockets", "webrtc", "oauth",
        "jwt", "design patterns", "version control", "debugging",
    ],
}

# Flat, deduplicated list used for extraction, ordered longest-first so
# multi-word or longer phrases are checked before their shorter substrings
# (e.g. "spring boot" before "spring").
SKILL_DB: List[str] = sorted(
    dict.fromkeys(
        skill for skills in SKILL_CATEGORIES.values() for skill in skills
    ),
    key=len,
    reverse=True,
)

# Reverse lookup: skill (lowercase) -> category name.
_SKILL_TO_CATEGORY: Dict[str, str] = {
    skill: category
    for category, skills in SKILL_CATEGORIES.items()
    for skill in skills
}


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def extract_skills(text: str, skill_db: List[str] = None) -> Set[str]:
    """
    Extract known skills mentioned in a block of text using whole-phrase
    regex matching.

    Word-boundary matching prevents false positives such as "java"
    matching inside "javascript", or "c" matching inside "developer".

    Args:
        text: Raw or cleaned resume/job-description text.
        skill_db: Optional custom skill list. Defaults to SKILL_DB.

    Returns:
        A set of matched skills (lowercase, as stored in SKILL_DB).
    """
    if skill_db is None:
        skill_db = SKILL_DB

    if not text or not text.strip():
        return set()

    text_lower = text.lower()
    found: Set[str] = set()

    for skill in skill_db:
        # (?<![a-z0-9]) / (?![a-z0-9]) act as boundaries that also work for
        # skills containing symbols like "c++", "c#", ".net", "ci/cd",
        # which \b in standard regex handles inconsistently.
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            found.add(skill)

    return found


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def compare_skills(
    resume_text: str, jd_text: str, skill_db: List[str] = None
) -> Tuple[Set[str], Set[str], Set[str], Set[str]]:
    """
    Compare skills found in a resume against skills required by a
    job description.

    Args:
        resume_text: Raw or cleaned resume text.
        jd_text: Raw or cleaned job description text.
        skill_db: Optional custom skill list. Defaults to SKILL_DB.

    Returns:
        A tuple of (matched_skills, missing_skills, resume_skills, jd_skills):
            - matched_skills: skills present in both resume and JD.
            - missing_skills: skills required by JD but absent from resume.
            - resume_skills: full set of skills found in the resume.
            - jd_skills: full set of skills found in the job description.
    """
    resume_skills = extract_skills(resume_text, skill_db)
    jd_skills = extract_skills(jd_text, skill_db)

    matched_skills = resume_skills & jd_skills
    missing_skills = jd_skills - resume_skills

    return matched_skills, missing_skills, resume_skills, jd_skills


# ---------------------------------------------------------------------------
# Categorization
# ---------------------------------------------------------------------------

def categorize_skills(skills: Set[str]) -> Dict[str, List[str]]:
    """
    Group a set of skills by their category for dashboard display.

    Args:
        skills: A set (or list) of lowercase skill strings.

    Returns:
        A dict mapping category name -> sorted list of display-cased
        skills in that category. Categories with no matches are omitted.
        Skills not found in the database are grouped under "Other".
    """
    grouped: Dict[str, List[str]] = {}

    for skill in skills:
        category = _SKILL_TO_CATEGORY.get(skill, "Other")
        grouped.setdefault(category, []).append(skill.title())

    # Sort skills within each category, and keep category order consistent
    # with SKILL_CATEGORIES rather than dict insertion order.
    ordered: Dict[str, List[str]] = {}
    for category in list(SKILL_CATEGORIES.keys()) + ["Other"]:
        if category in grouped:
            ordered[category] = sorted(grouped[category])

    return ordered
