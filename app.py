from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Set

import streamlit as st
import yaml


# -----------------------------
# Page config
# - Compass only in browser tab name + icon
# - No emojis in page content (except Favorites section header)
# -----------------------------
st.set_page_config(
    page_title="Streamlit Hub",
    page_icon="🧭",
    layout="centered",
)

# -----------------------------
# Paths
# -----------------------------
APPS_FILE = Path("data/apps.yaml")

# -----------------------------
# Styling (same language as your sample)
# + fixed-size hub cards
# + inline tags row
# -----------------------------
st.markdown(
    """
    <style>
      /* Hide Streamlit chrome */
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
      header {visibility: hidden;}

      /* App background */
      [data-testid="stAppViewContainer"] {
        background:
          radial-gradient(1200px 600px at 20% -10%, rgba(31,79,216,0.10), rgba(255,255,255,0) 60%),
          radial-gradient(1000px 700px at 90% 10%, rgba(34,197,94,0.08), rgba(255,255,255,0) 55%),
          linear-gradient(180deg, rgba(250,250,252,1), rgba(255,255,255,1));
      }

      /* Page container */
      .block-container {
        padding-top: 2.0rem;
        padding-bottom: 2.0rem;
        max-width: 980px;
      }

      /* Normalize spacing */
      .stMarkdown {margin: 0 !important;}
      .stMarkdown p {margin: 0.25rem 0 0 0 !important;}

      /* Title */
      h1 {
        font-size: 2.05rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        margin: 0 0 0.2rem 0;
      }

      .muted { color: rgba(49, 51, 63, 0.72); }
      .tiny  { font-size: 0.82rem; color: rgba(49, 51, 63, 0.65); }

      /* Card containers (Streamlit bordered containers) */
      div[data-testid="stVerticalBlockBorderWrapper"]{
        border: 1px solid rgba(49, 51, 63, 0.14) !important;
        border-radius: 18px !important;
        background: rgba(255,255,255,0.86) !important;
        box-shadow: 0 6px 22px rgba(0,0,0,0.04) !important;
        padding: 14px 16px !important;
      }

      /* Consistent section label */
      .label {
        font-size: 0.96rem;
        font-weight: 850;
        line-height: 1.15;
        margin: 0 0 0.35rem 0;
      }

      .desc {
        color: rgba(49, 51, 63, 0.72);
        font-size: 0.95rem;
        margin: 0 0 0.9rem 0;
      }

      /* Chip */
      .chip {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid rgba(49,51,63,0.16);
        background: rgba(255,255,255,0.70);
        font-size: 0.85rem;
        font-weight: 750;
        margin-right: 6px;
        margin-top: 6px;
        white-space: nowrap;
      }

      /* Tags row container */
      .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 6px;
        margin-bottom: 10px;
      }

      /* Fixed-size hub card */
      .hub-card {
        min-height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      }

      .hub-card h3 {
        margin-top: 0.15rem !important;
        margin-bottom: 0.15rem !important;
      }

      .hub-desc {
        color: rgba(49, 51, 63, 0.72);
        font-size: 0.95rem;
        margin: 0.25rem 0 0.75rem 0;
      }

      /* Gradient primary link button */
      .primary-link {
        background: linear-gradient(180deg, #1f4fd8, #1a3fa8);
        color: #fff !important;
        border: none;
        border-radius: 14px;
        padding: 0.66rem 1rem;
        font-weight: 800;
        text-decoration: none !important;
        display: block;
        width: 100%;
        text-align: center;
      }
      .primary-link:hover{
        background: linear-gradient(180deg, #245ef5, #1f4fd8);
        color: #fff !important;
      }

      /* Footer trademark */
      .keshet-footer {
        position: fixed;
        bottom: 8px;
        left: 0;
        right: 0;
        text-align: center;
        font-size: 0.72rem;
        color: rgba(49, 51, 63, 0.35);
        pointer-events: none;
        letter-spacing: 0.02em;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Helpers
# -----------------------------
def load_apps() -> List[Dict[str, Any]]:
    if not APPS_FILE.exists():
        return []
    data = yaml.safe_load(APPS_FILE.read_text(encoding="utf-8")) or {}
    apps = data.get("apps", []) or []

    for a in apps:
        a.setdefault("name", "Untitled App")
        a.setdefault("url", "")
        a.setdefault("description", "")
        a.setdefault("tags", [])
        a.setdefault("category", "Other")
        a.setdefault("favorite", False)

    # favorites first, then category, then name
    apps.sort(key=lambda x: (not bool(x.get("favorite")), str(x.get("category")), str(x.get("name"))))
    return apps


def matches(app: Dict[str, Any], q: str) -> bool:
    if not q:
        return True
    q = q.lower().strip()
    hay = " ".join(
        [
            str(app.get("name", "")),
            str(app.get("description", "")),
            str(app.get("category", "")),
            " ".join(app.get("tags") or []),
            str(app.get("url", "")),
        ]
    ).lower()
    return q in hay


def collect_categories(apps: List[Dict[str, Any]]) -> List[str]:
    cats: Set[str] = {str(a.get("category", "Other")) for a in apps}
    return sorted(cats)


def collect_tags(apps: List[Dict[str, Any]]) -> List[str]:
    tags: Set[str] = set()
    for a in apps:
        for t in (a.get("tags") or []):
            tags.add(str(t))
    return sorted(tags)


def render_app_card(app: Dict[str, Any]) -> None:
    name = app.get("name", "Untitled App")
    desc = app.get("description", "")
    cat = app.get("category", "Other")
    tags = app.get("tags") or []
    url = app.get("url", "")

    chips_html = f"<span class='chip'>{cat}</span>" + "".join(
        [f"<span class='chip'>{t}</span>" for t in tags]
    )

    # Full card HTML so we can keep tags in one row + fixed height
    card_html = f"""
      <div class="hub-card">
        <div>
          <h3>{name}</h3>
          <div class="hub-desc">{desc}</div>
          <div class="chip-row">{chips_html}</div>
        </div>
        <div>
          {"<a class='primary-link' href='" + url + "' target='_blank' rel='noopener noreferrer'>Open app →</a>" if url else "<div class='hub-desc'>Missing URL in apps.yaml</div>"}
        </div>
      </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


# -----------------------------
# Header (no emoji)
# -----------------------------
st.title("Streamlit Hub")
st.markdown(
    "<div class='muted'>Open one place, see all your Streamlit Cloud apps, and jump to what you need.</div>",
    unsafe_allow_html=True,
)
st.write("")

apps = load_apps()
if not apps:
    st.error("No apps found. Add your apps to `data/apps.yaml` and redeploy.")
    st.stop()

# -----------------------------
# Controls
# -----------------------------
with st.container(border=True):
    st.markdown("<div class='label'>Find an app</div>", unsafe_allow_html=True)
    st.markdown("<div class='desc'>Search by name, tag, category, or description.</div>", unsafe_allow_html=True)

    q = st.text_input("Search", placeholder="Type to search…", label_visibility="collapsed")

    c1, c2, c3 = st.columns([1.05, 1.05, 0.9], vertical_alignment="center")
    with c1:
        categories = collect_categories(apps)
        selected_categories = st.multiselect("Categories", options=categories, default=categories)
    with c2:
        tags = collect_tags(apps)
        selected_tags = st.multiselect("Tags", options=tags, default=[])
    with c3:
        favorites_only = st.toggle("Favorites only", value=False)

# -----------------------------
# Filter
# -----------------------------
filtered: List[Dict[str, Any]] = []
for a in apps:
    if selected_categories and a.get("category") not in selected_categories:
        continue
    if selected_tags and not set(selected_tags).intersection(set(a.get("tags") or [])):
        continue
    if favorites_only and not a.get("favorite", False):
        continue
    if not matches(a, q):
        continue
    filtered.append(a)

favorites = [a for a in filtered if a.get("favorite", False)]
others = [a for a in filtered if not a.get("favorite", False)]


def render_section(title_html: str, items: List[Dict[str, Any]]) -> None:
    if not items:
        return
    st.markdown(f"<div class='label'>{title_html}</div>", unsafe_allow_html=True)
    st.write("")

    cols = st.columns(2, gap="large")
    for i, app in enumerate(items):
        with cols[i % 2]:
            with st.container(border=True):
                render_app_card(app)


# -----------------------------
# Render
# -----------------------------
if not filtered:
    st.info("No apps match your filters.")
else:
    if favorites:
        # Emoji allowed here (per your request)
        render_section("⭐ Favorites", favorites)
        st.write("")
        render_section("All apps", others)
    else:
        render_section("All apps", filtered)

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    """
    <div class="keshet-footer">
      © Keshet Digital Data Team
    </div>
    """,
    unsafe_allow_html=True,
)
