"""
charts.py
---------
Module 6: Matplotlib visualizations for the Resume vs Job Description
Matcher.

Responsibilities:
    - Bar chart comparing matched vs missing skill counts.
    - Pie chart showing match percentage vs gap percentage.
    - Bonus: keyword frequency chart from the resume text.

Every function here returns a matplotlib Figure object (it does NOT call
plt.show()). app.py is responsible for rendering it via
st.pyplot(fig).
"""

from collections import Counter
from typing import List

import matplotlib.pyplot as plt

# A calm, consistent palette used across all charts.
_MATCH_COLOR = "#2ecc71"    # green
_MISSING_COLOR = "#e74c3c"  # red
_BAR_COLOR = "#3498db"      # blue


def plot_skills_bar_chart(matched_count: int, missing_count: int) -> plt.Figure:
    """
    Create a bar chart comparing matched vs missing skill counts.

    Args:
        matched_count: Number of skills matched between resume and JD.
        missing_count: Number of skills required by JD but missing from resume.

    Returns:
        A matplotlib Figure ready to be passed to st.pyplot().
    """
    fig, ax = plt.subplots(figsize=(5, 4))

    categories = ["Matched", "Missing"]
    counts = [matched_count, missing_count]
    colors = [_MATCH_COLOR, _MISSING_COLOR]

    bars = ax.bar(categories, counts, color=colors, width=0.5)

    ax.set_ylabel("Number of Skills")
    ax.set_title("Matched vs Missing Skills")
    ax.set_ylim(0, max(counts + [1]) + 1)

    # Label each bar with its count for readability.
    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            str(count),
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    return fig


def plot_match_pie_chart(match_score: float) -> plt.Figure:
    """
    Create a pie chart showing match percentage vs remaining gap.

    Args:
        match_score: Match percentage between 0.0 and 100.0.

    Returns:
        A matplotlib Figure ready to be passed to st.pyplot().
    """
    match_score = max(0.0, min(match_score, 100.0))
    gap = round(100.0 - match_score, 2)

    fig, ax = plt.subplots(figsize=(4, 4))

    values = [match_score, gap]
    labels = ["Matched", "Gap"]
    colors = [_MATCH_COLOR, _MISSING_COLOR]

    # Avoid rendering a 0% wedge label, which matplotlib can render oddly.
    display_values = [v for v in values if v > 0]
    display_labels = [l for l, v in zip(labels, values) if v > 0]
    display_colors = [c for c, v in zip(colors, values) if v > 0]

    ax.pie(
        display_values,
        labels=display_labels,
        colors=display_colors,
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    ax.set_title("Overall Match Percentage")
    ax.axis("equal")  # Keeps the pie circular.

    fig.tight_layout()
    return fig


def plot_keyword_frequency_chart(
    tokens: List[str], top_n: int = 10
) -> plt.Figure:
    """
    Bonus: Create a horizontal bar chart of the most frequent keywords
    in the resume.

    Args:
        tokens: A list of cleaned word tokens (already lowercased, with
            stopwords/punctuation removed — see text_processing.tokenize()).
        top_n: How many top keywords to display. Defaults to 10.

    Returns:
        A matplotlib Figure ready to be passed to st.pyplot(). If tokens
        is empty, returns a figure with a placeholder "no data" message.
    """
    fig, ax = plt.subplots(figsize=(6, 4))

    if not tokens:
        ax.text(
            0.5, 0.5, "No keyword data available",
            ha="center", va="center", fontsize=11, color="gray",
        )
        ax.axis("off")
        return fig

    counts = Counter(tokens)
    most_common = counts.most_common(top_n)

    # Reverse so the highest-frequency word appears at the top of the chart.
    words = [w for w, _ in most_common][::-1]
    freqs = [f for _, f in most_common][::-1]

    ax.barh(words, freqs, color=_BAR_COLOR)
    ax.set_xlabel("Frequency")
    ax.set_title(f"Top {len(words)} Resume Keywords")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    return fig
