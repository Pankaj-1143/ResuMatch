"""
ui.py
-----
Presentation layer only. Every function here renders HTML/CSS via
st.markdown (or wraps an st.container) — none of them touch NLP logic,
session state used by the backend, or any of the imported backend
modules. app.py imports these helpers to build a "premium SaaS" look
on top of the untouched pipeline.

FIX NOTES (read this if you're diffing against an older version)
------------------------------------------------------------------
1. `_md()` now dedents *line by line* instead of relying on
   `textwrap.dedent()`. `textwrap.dedent()` only strips whitespace that
   is common to every line in the string — one line pasted in at a
   different indent level (easy to do when editing) silently breaks
   it, and Streamlit's Markdown parser then treats the leftover
   indentation as a fenced code block, printing the raw HTML/CSS as
   literal text on the page. Stripping per-line is immune to that.

2. `card_open()` / `card_close()` are GONE. That pattern opened a
   `<div class="card">` in one `st.markdown()` call and closed it with
   `</div>` in a separate, later `st.markdown()` call, with native
   Streamlit widgets (columns, buttons, charts, tabs) placed "in
   between" in the Python code. That does not work: every
   `st.markdown()` call renders its own independent HTML fragment in
   the DOM, so the widgets in between were never actually nested
   inside that div. The div from `card_open()` gets auto-closed
   immediately, the widgets render as unstyled siblings, and the lone
   `</div>` from `card_close()` is a dangling, unmatched fragment —
   the real source of stray markup/text showing up on the dashboard.

   Use `ui.card(...)` as a context manager instead:

       with ui.card("Title", "description"):
           st.columns(2)
           st.button("Click me")

   This uses a real `st.container(key=...)`, so anything placed inside
   the `with` block is an actual child of that container, and it's
   styled via Streamlit's supported `st-key-*` CSS hook (Streamlit
   >= 1.31) instead of hand-rolled unmatched tags.

Design tokens
-------------
Primary   #2563EB
Success   #22C55E
Warning   #F59E0B
Danger    #EF4444
Background#F5F7FB
Card      #FFFFFF
Radius    18px
Font      Inter
"""

import itertools

import streamlit as st


# ---------------------------------------------------------------------------
# Core markdown helper (hardened against indentation bugs)
# ---------------------------------------------------------------------------
def _md(html: str) -> None:
    """Render an HTML/CSS block safely.

    Streamlit's Markdown parser mishandles blank lines inside
    <style>/<script> blocks: a blank line ends "raw HTML mode" early,
    and everything after it gets treated as plain Markdown text
    instead of HTML/CSS -- which is exactly why the CSS was showing
    up as literal text on the page.

    Fix: use st.html() (Streamlit >= 1.29), which renders raw HTML
    with zero Markdown parsing involved, so this can't happen. Falls
    back to st.markdown(unsafe_allow_html=True) with all blank lines
    stripped out first, for older Streamlit versions.
    """
    lines = [line.strip() for line in html.strip("\n").split("\n")]
    lines = [line for line in lines if line]  # drop every blank line
    cleaned = "\n".join(lines)

    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# THEME / GLOBAL CSS
# ---------------------------------------------------------------------------
def load_css(dark: bool = False) -> None:
    """Inject fonts + global CSS. Call once, right after set_page_config().
    Pass dark=True to render the dark theme instead of light."""

    if dark:
        palette = """
            --primary:#3B82F6;
            --primary-dark:#2563EB;
            --success:#22C55E;
            --warning:#F59E0B;
            --danger:#F87171;
            --purple:#A78BFA;
            --bg:#0F172A;
            --card:#1E293B;
            --border:#334155;
            --text:#F1F5F9;
            --text-muted:#94A3B8;
            --radius:18px;
            --shadow:0 1px 2px rgba(0,0,0,.25), 0 8px 24px rgba(0,0,0,.35);
            --shadow-hover:0 4px 10px rgba(0,0,0,.30), 0 16px 32px rgba(0,0,0,.45);
        """
    else:
        palette = """
            --primary:#2563EB;
            --primary-dark:#1D4ED8;
            --success:#22C55E;
            --warning:#F59E0B;
            --danger:#EF4444;
            --purple:#8B5CF6;
            --bg:#F5F7FB;
            --card:#FFFFFF;
            --border:#E7EAF3;
            --text:#0F172A;
            --text-muted:#64748B;
            --radius:18px;
            --shadow:0 1px 2px rgba(15,23,42,.04), 0 8px 24px rgba(15,23,42,.06);
            --shadow-hover:0 4px 10px rgba(15,23,42,.06), 0 16px 32px rgba(15,23,42,.10);
        """

    _md(
        f"""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
        :root{{
        {palette}
        }}

        html, body, [class*="css"]{{
            font-family:'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }}

        .stApp{{ background:var(--bg); color:var(--text); }}

        #MainMenu{{visibility:hidden;}}
        footer{{visibility:hidden;}}
        header[data-testid="stHeader"]{{background:transparent;}}
        .block-container{{ padding-top:1.2rem; padding-bottom:2rem; max-width:1200px; }}

        section[data-testid="stSidebar"]{{
            background:var(--card);
            border-right:1px solid var(--border);
        }}
        section[data-testid="stSidebar"] .block-container{{ padding-top:1.5rem; }}
        section[data-testid="stSidebar"] *{{ color:var(--text) !important; }}
        section[data-testid="stSidebar"] .stCaption,
        section[data-testid="stSidebar"] small{{ color:var(--text-muted) !important; }}

        .stButton>button, .stDownloadButton>button{{
            background:linear-gradient(135deg, var(--primary) 0%, #7C3AED 100%);
            color:#fff; border:none; border-radius:12px;
            padding:0.7rem 1.4rem; font-weight:600; font-size:0.95rem;
            box-shadow:0 4px 14px rgba(37,99,235,.30);
            transition:transform .15s ease, box-shadow .15s ease;
        }}
        .stButton>button:hover, .stDownloadButton>button:hover{{
            transform:translateY(-1px);
            box-shadow:0 6px 20px rgba(37,99,235,.40);
            color:#fff;
        }}
        .stButton>button:active{{ transform:translateY(0); }}

        .stTextArea textarea, .stTextInput input{{
            border-radius:14px !important;
            border:1px solid var(--border) !important;
            background:var(--card) !important;
            color:var(--text) !important;
            box-shadow:var(--shadow);
            font-size:0.95rem !important;
        }}
        .stTextArea textarea:focus, .stTextInput input:focus{{
            border-color:var(--primary) !important;
            box-shadow:0 0 0 3px rgba(37,99,235,.15) !important;
        }}

        [data-testid="stFileUploaderDropzone"]{{
            background:var(--card);
            border:2px dashed var(--border);
            border-radius:var(--radius);
            transition:border-color .15s ease, background .15s ease;
        }}
        [data-testid="stFileUploaderDropzone"]:hover{{
            border-color:var(--primary);
        }}

        .stTabs [data-baseweb="tab-list"]{{ gap:6px; }}
        .stTabs [data-baseweb="tab"]{{
            border-radius:10px; padding:8px 16px; font-weight:600;
            color:var(--text-muted);
        }}
        .stTabs [aria-selected="true"]{{
            background:rgba(37,99,235,.15); color:var(--primary) !important;
        }}

        .streamlit-expanderHeader, [data-testid="stExpander"] summary{{
            border-radius:14px !important;
            font-weight:600;
        }}
        [data-testid="stExpander"]{{
            border:1px solid var(--border) !important;
            border-radius:14px !important;
            box-shadow:var(--shadow);
            background:var(--card);
        }}

        .stProgress > div > div{{
            background:linear-gradient(90deg, var(--primary), #7C3AED) !important;
            border-radius:8px;
        }}

        .topnav{{
            display:flex; align-items:center; justify-content:space-between;
            background:var(--card); border:1px solid var(--border);
            border-radius:var(--radius); padding:14px 22px;
            box-shadow:var(--shadow); margin-bottom:22px;
        }}
        .topnav-left{{ display:flex; align-items:center; gap:10px; font-weight:800; font-size:1.15rem; color:var(--text); }}
        .topnav-logo{{
            width:34px; height:34px; border-radius:9px;
            background:linear-gradient(135deg, var(--primary), #7C3AED);
            display:flex; align-items:center; justify-content:center;
            color:#fff; font-size:1.05rem;
        }}
        .topnav-right{{ display:flex; align-items:center; gap:16px; color:var(--text-muted); }}
        .avatar{{
            width:34px; height:34px; border-radius:50%;
            background:linear-gradient(135deg,#7C3AED,#2563EB);
            display:flex; align-items:center; justify-content:center;
            color:#fff; font-weight:700; font-size:.85rem;
        }}

        .hero{{
            position:relative; overflow:hidden;
            background:linear-gradient(135deg, #2563EB 0%, #4F46E5 55%, #7C3AED 100%);
            border-radius:var(--radius);
            padding:38px 42px; margin-bottom:24px;
            color:#fff; box-shadow:0 12px 34px rgba(37,99,235,.28);
        }}
        .hero::after{{
            content:""; position:absolute; right:-60px; top:-60px;
            width:260px; height:260px; border-radius:50%;
            background:rgba(255,255,255,.08);
        }}
        .hero-icon{{
            width:52px; height:52px; border-radius:14px;
            background:rgba(255,255,255,.15); backdrop-filter:blur(6px);
            display:flex; align-items:center; justify-content:center;
            font-size:1.6rem; margin-bottom:16px;
        }}
        .hero h1{{ margin:0 0 8px 0; font-size:2rem; font-weight:800; letter-spacing:-0.02em; }}
        .hero p{{ margin:0; opacity:.92; font-size:1.02rem; max-width:640px; }}
        .hero-stats{{ display:flex; gap:32px; margin-top:22px; }}
        .hero-stat-num{{ font-size:1.4rem; font-weight:800; }}
        .hero-stat-label{{ font-size:.8rem; opacity:.85; }}

        .section-title{{ margin:6px 0 4px 0; }}
        .section-title h3{{ margin:0; font-weight:800; font-size:1.15rem; color:var(--text); }}
        .section-title p{{ margin:2px 0 0 0; color:var(--text-muted); font-size:.9rem; }}

        .metric-card{{
            background:var(--card); border:1px solid var(--border);
            border-top:4px solid var(--accent, var(--primary));
            border-radius:var(--radius); padding:20px 20px 18px 20px;
            box-shadow:var(--shadow); transition:transform .15s ease, box-shadow .15s ease;
            height:100%;
        }}
        .metric-card:hover{{ transform:translateY(-3px); box-shadow:var(--shadow-hover); }}
        .metric-icon{{ font-size:1.3rem; margin-bottom:10px; }}
        .metric-title{{ color:var(--text-muted); font-size:.82rem; font-weight:600; margin:0 0 6px 0; }}
        .metric-value{{ font-size:1.9rem; font-weight:800; margin:0; line-height:1.1; color:var(--accent, var(--text)); }}
        .metric-desc{{ color:var(--text-muted); font-size:.8rem; margin-top:6px; }}

        .info-card{{
            display:flex; gap:14px; align-items:flex-start;
            background:var(--card); border:1px solid var(--border);
            border-radius:16px; padding:16px 18px; margin-bottom:10px;
            box-shadow:var(--shadow);
        }}
        .info-card .info-icon{{
            width:34px; height:34px; min-width:34px; border-radius:10px;
            background:rgba(34,197,94,.15); color:var(--success);
            display:flex; align-items:center; justify-content:center; font-size:1rem;
        }}
        .info-card h5{{ margin:0 0 4px 0; font-size:.95rem; font-weight:700; color:var(--text); }}
        .info-card p{{ margin:0; color:var(--text-muted); font-size:.87rem; }}

        .pill{{
            display:inline-flex; align-items:center; gap:6px;
            padding:6px 14px; border-radius:999px; font-size:.83rem;
            font-weight:600; margin:4px 6px 4px 0;
            transition:transform .1s ease;
        }}
        .pill:hover{{ transform:translateY(-1px); }}
        .pill-matched{{ background:rgba(34,197,94,.15); color:var(--success); border:1px solid var(--success); }}
        .pill-missing{{ background:rgba(239,68,68,.15); color:var(--danger); border:1px solid var(--danger); }}

        .ring-wrap{{ display:flex; align-items:center; gap:22px; }}
        .ring{{
            width:120px; height:120px; border-radius:50%;
            display:flex; align-items:center; justify-content:center;
            background:conic-gradient(var(--ring-color, var(--primary)) calc(var(--pct,0)*1%), var(--border) 0);
        }}
        .ring-inner{{
            width:92px; height:92px; border-radius:50%; background:var(--card);
            display:flex; flex-direction:column; align-items:center; justify-content:center;
        }}
        .ring-inner .num{{ font-size:1.3rem; font-weight:800; color:var(--text); }}
        .ring-inner .lbl{{ font-size:.68rem; color:var(--text-muted); }}

        .app-footer{{
            margin-top:36px; padding:18px 4px; text-align:center;
            color:var(--text-muted); font-size:.82rem;
            border-top:1px solid var(--border);
        }}

        .step-msg{{ font-size:.9rem; color:var(--text-muted); margin:2px 0 8px 2px; }}

        div[class*="st-key-card_"]{{
            background:var(--card);
            border:1px solid var(--border);
            border-radius:var(--radius);
            padding:22px;
            box-shadow:var(--shadow);
        }}
        </style>
        """
    )

# ---------------------------------------------------------------------------
# TOP NAV
# ---------------------------------------------------------------------------
def top_nav(app_name: str = "Resume Matcher", user_initials: str = "RM") -> None:
    _md(
        f"""
        <div class="topnav">
            <div class="topnav-left">
                <div class="topnav-logo">📄</div>
                {app_name}
            </div>
            <div class="topnav-right">
                <span>🔍</span>
                <span>🔔</span>
                <div class="avatar">{user_initials}</div>
            </div>
        </div>
        """
    )


# ---------------------------------------------------------------------------
# HERO BANNER
# ---------------------------------------------------------------------------
def hero_banner(title: str, subtitle: str, icon: str = "✨", stats: list | None = None) -> None:
    """stats: list of (value, label) tuples, e.g. [("10k+", "Resumes analyzed")]"""
    stats = stats or []
    stats_html = "".join(
        f'<div><div class="hero-stat-num">{v}</div><div class="hero-stat-label">{l}</div></div>'
        for v, l in stats
    )
    _md(
        f"""
        <div class="hero">
            <div class="hero-icon">{icon}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
            {'<div class="hero-stats">' + stats_html + '</div>' if stats else ''}
        </div>
        """
    )


# ---------------------------------------------------------------------------
# SECTION TITLE
# ---------------------------------------------------------------------------
def section_title(title: str, subtitle: str | None = None) -> None:
    _md(
        f"""
        <div class="section-title">
            <h3>{title}</h3>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
        """
    )


# ---------------------------------------------------------------------------
# METRIC CARD
# ---------------------------------------------------------------------------
def metric_card(icon: str, title: str, value: str, description: str = "", color: str = "#2563EB") -> None:
    _md(
        f"""
        <div class="metric-card" style="--accent:{color};">
            <div class="metric-icon">{icon}</div>
            <p class="metric-title">{title}</p>
            <p class="metric-value">{value}</p>
            <p class="metric-desc">{description}</p>
        </div>
        """
    )


# ---------------------------------------------------------------------------
# CARD CONTAINER (context manager) — replaces the old card_open()/card_close()
# ---------------------------------------------------------------------------
_card_counter = itertools.count()


def card(title: str | None = None, description: str | None = None):
    """A styled card. Use as a context manager:

        with ui.card("Title", "description"):
            st.columns(2)
            st.button("Click me")

    Anything placed inside the `with` block is a real child of the
    underlying st.container, so it's actually wrapped by the card's
    background/border/shadow — unlike the old open/close-tag pattern.
    """
    key = f"card_{next(_card_counter)}"
    container = st.container(key=key)
    with container:
        if title:
            st.markdown(
                f'<h4 style="margin:0 0 4px 0;font-weight:700;font-size:1rem;">{title}</h4>',
                unsafe_allow_html=True,
            )
        if description:
            st.markdown(
                f'<p style="margin:0 0 14px 0;color:#64748B;font-size:.85rem;">{description}</p>',
                unsafe_allow_html=True,
            )
    return container


# ---------------------------------------------------------------------------
# INFO / SUGGESTION CARD
# ---------------------------------------------------------------------------
def info_card(title: str, description: str, icon: str = "💡") -> None:
    _md(
        f"""
        <div class="info-card">
            <div class="info-icon">{icon}</div>
            <div>
                <h5>{title}</h5>
                <p>{description}</p>
            </div>
        </div>
        """
    )


# ---------------------------------------------------------------------------
# SKILL BADGES
# ---------------------------------------------------------------------------
def skill_badge(text: str, matched: bool = True) -> str:
    """Returns HTML for a single pill — combine several and pass to _md."""
    cls = "pill-matched" if matched else "pill-missing"
    mark = "✓" if matched else "✕"
    return f'<span class="pill {cls}">{mark} {text}</span>'


def skill_badges(items: list[str], matched: bool = True) -> None:
    if not items:
        st.info("No matched skills found." if matched else "No missing skills — great coverage!")
        return
    html = "".join(skill_badge(s.title(), matched) for s in sorted(items))
    _md(html)


# ---------------------------------------------------------------------------
# CIRCULAR "ATS SCORE" RING (pure CSS, no extra deps)
# ---------------------------------------------------------------------------
def score_ring(score: int, label: str = "ATS Score") -> None:
    pct = max(0, min(100, int(score)))
    color = "#22C55E" if pct >= 75 else ("#F59E0B" if pct >= 50 else "#EF4444")
    _md(
        f"""
        <div class="ring-wrap">
            <div class="ring" style="--pct:{pct}; --ring-color:{color};">
                <div class="ring-inner">
                    <div class="num">{pct}%</div>
                    <div class="lbl">{label}</div>
                </div>
            </div>
        </div>
        """
    )


# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------
def footer(version: str = "1.0") -> None:
    _md(
        f"""
        <div class="app-footer">
            Resume Matcher · v{version} · Built with local NLP — no external AI APIs
        </div>
        """
    )


# ---------------------------------------------------------------------------
# LOADING SEQUENCE
# ---------------------------------------------------------------------------
def run_loading_sequence(placeholder, steps: list[str], step_fn=None):
    """
    Renders a progress bar + step captions inside `placeholder`
    (an st.empty()). Optionally calls step_fn(i, step_label) after
    each step is displayed, so callers can run real work between steps.
    Purely cosmetic — does not alter any backend computation.
    """
    import time

    n = len(steps)
    for i, step in enumerate(steps, start=1):
        with placeholder.container():
            st.progress(i / n)
            _md(f'<div class="step-msg">{step}</div>')
        if step_fn:
            step_fn(i - 1, step)
        else:
            time.sleep(0.25)
    placeholder.empty()