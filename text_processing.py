"""
text_processing.py
--------------------
Reusable text cleaning utilities used before TF-IDF vectorization and
skill extraction. Uses NLTK for stopword removal.
"""

import re
import string
from typing import List

import nltk
from nltk.corpus import stopwords


def ensure_nltk_data() -> None:
    """
    Make sure the required NLTK corpora are downloaded.
    Safe to call multiple times; it only downloads if missing.
    """
    required_packages = ["stopwords", "punkt"]
    for package in required_packages:
        try:
            nltk.data.find(
                f"corpora/{package}" if package == "stopwords" else f"tokenizers/{package}"
            )
        except LookupError:
            nltk.download(package, quiet=True)


def clean_text(raw_text: str) -> str:
    """
    Clean and normalize input text for NLP processing.

    Steps performed:
        1. Lowercase the text
        2. Remove punctuation
        3. Remove numbers
        4. Remove extra whitespace
        5. Remove English stopwords

    Args:
        raw_text: The original, unprocessed text.

    Returns:
        A cleaned, lowercase string with stopwords and punctuation removed.
    """
    if not raw_text or not raw_text.strip():
        return ""

    ensure_nltk_data()

    # 1. Lowercase
    text = raw_text.lower()

    # 2. Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # 3. Remove numbers
    text = re.sub(r"\d+", " ", text)

    # 4. Collapse extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # 5. Remove stopwords
    stop_words = set(stopwords.words("english"))
    tokens = text.split()
    filtered_tokens = [word for word in tokens if word not in stop_words and len(word) > 1]

    return " ".join(filtered_tokens)


def tokenize(text: str) -> List[str]:
    """
    Split cleaned text into a list of word tokens.

    Args:
        text: Cleaned text string.

    Returns:
        List of word tokens.
    """
    if not text:
        return []
    return text.split()


def count_words(raw_text: str) -> int:
    """Return the number of words in the raw (uncleaned) text."""
    if not raw_text:
        return 0
    return len(raw_text.split())


def estimate_reading_time(raw_text: str, words_per_minute: int = 200) -> int:
    """
    Estimate reading time in minutes for a block of text.

    Args:
        raw_text: The original text.
        words_per_minute: Average reading speed, defaults to 200 wpm.

    Returns:
        Estimated reading time in whole minutes (minimum 1).
    """
    word_count = count_words(raw_text)
    if word_count == 0:
        return 0
    minutes = max(1, round(word_count / words_per_minute))
    return minutes
