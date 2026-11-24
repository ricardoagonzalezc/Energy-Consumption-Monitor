"""Blueprint theme shared with https://ricardoagonzalezc.github.io

Call `apply_theme()` once, right after `st.set_page_config(...)`.
It (1) injects the site's fonts + CSS into Streamlit and
(2) registers a matching Plotly template so every chart is styled
automatically - no per-figure colour code needed.
"""
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ── Palette (from the site's style.css) ──────────────────────────
BG          = "#122A45"
PANEL       = "#17324F"
PANEL_HOVER = "#1B3A5C"
INK         = "#EAF2FA"
INK_DIM     = "#9FB7CE"
ACCENT      = "#FFB020"                      # amber
LINE        = "rgba(234, 242, 250, 0.14)"
LINE_STRONG = "rgba(234, 242, 250, 0.28)"

# Categorical series colours, always used in this fixed order.
# (validated on PANEL: contrast >= 3:1, normal-vision separation >= 15 dE.
#  Coral/mint are close under deuteranopia, so charts also use labels and
#  dash styles rather than colour alone.)
AMBER, SKY, MINT, CORAL, LAVENDER = "#FFB020", "#4FC3F7", "#66D9A0", "#FF7A7A", "#B79CFF"
SERIES = [AMBER, SKY, MINT, CORAL, LAVENDER]

FONT_DISPLAY = "Space Grotesk, sans-serif"
FONT_MONO    = "IBM Plex Mono, monospace"
FONT_BODY    = "IBM Plex Sans, sans-serif"

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

html, body, .stApp, [data-testid="stAppViewContainer"] {{
  background: {BG};
  color: {INK};
  font-family: {FONT_BODY};
}}
/* faint graph-paper grid behind the page header, like the site's hero.
   (Lives on our own .bp-hero element - never put position:relative on Streamlit's containers.) */
.bp-hero {{ position: relative; padding: 4px 0 18px; }}
.bp-hero::before {{
  content: ""; position: absolute; z-index: -1; inset: -48px -3rem 0 -3rem;
  background-image:
    linear-gradient({LINE} 1px, transparent 1px),
    linear-gradient(90deg, {LINE} 1px, transparent 1px);
  background-size: 40px 40px; opacity: .35; pointer-events: none;
  -webkit-mask-image: linear-gradient(to bottom, black, transparent 90%);
          mask-image: linear-gradient(to bottom, black, transparent 90%);
}}
.bp-hero h1 {{ margin: 0; padding: 0; }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2.5rem; max-width: 1180px; }}

h1, h2, h3, h4 {{ font-family: {FONT_DISPLAY}; font-weight: 600; letter-spacing: -0.01em; color: {INK}; }}
h1 {{ font-size: clamp(2rem, 4.5vw, 3rem); line-height: 1.05; }}
h2, h3 {{ font-size: 1.35rem; }}
p, li, label, .stMarkdown {{ font-family: {FONT_BODY}; }}
a {{ color: {ACCENT}; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
code {{ font-family: {FONT_MONO}; color: {ACCENT}; background: rgba(255,176,32,.12); }}

/* site eyebrow + back link */
.bp-eyebrow {{ font-family: {FONT_MONO}; font-size: .8rem; letter-spacing: .14em;
  text-transform: uppercase; color: {ACCENT}; margin-bottom: 14px; }}
.bp-sub {{ color: {INK_DIM}; max-width: 70ch; margin: 10px 0 6px; }}
.bp-back {{ font-family: {FONT_MONO}; font-size: .8rem; color: {INK_DIM} !important; }}
.bp-back:hover {{ color: {ACCENT} !important; text-decoration: none; }}
.bp-label {{ font-family: {FONT_MONO}; font-size: .72rem; letter-spacing: .1em;
  text-transform: uppercase; color: {INK_DIM}; }}

/* sidebar */
[data-testid="stSidebar"] {{ background: {PANEL}; border-right: 1px solid {LINE}; }}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
  font-family: {FONT_MONO}; font-size: .8rem; letter-spacing: .12em;
  text-transform: uppercase; color: {ACCENT}; font-weight: 500; }}

/* metric tiles = the site's title-block cells */
[data-testid="stMetric"] {{ background: {PANEL}; border: 1px solid {LINE_STRONG};
  padding: 14px 18px; border-radius: 0; }}
[data-testid="stMetricLabel"] p {{ font-family: {FONT_MONO}; font-size: .7rem;
  letter-spacing: .1em; text-transform: uppercase; color: {INK_DIM}; }}
[data-testid="stMetricValue"] {{ font-family: {FONT_MONO}; font-size: 1.5rem; color: {INK}; }}
[data-testid="stMetricDelta"] {{ font-family: {FONT_MONO}; font-size: .72rem; }}

/* custom stat tiles (title-block cells) */
.bp-tile {{ background: {PANEL}; border: 1px solid {LINE_STRONG}; padding: 14px 18px; height: 100%; }}
.bp-tile .k {{ font-family: {FONT_MONO}; font-size: .68rem; letter-spacing: .1em;
  text-transform: uppercase; color: {INK_DIM}; margin-bottom: 6px; }}
.bp-tile .v {{ font-family: {FONT_MONO}; font-size: 1.55rem; color: {INK}; line-height: 1.2; }}
.bp-tile .s {{ font-family: {FONT_MONO}; font-size: .64rem; color: {INK_DIM}; margin-top: 4px; white-space: nowrap; }}
.bp-tile.ok .v {{ color: {MINT}; }} .bp-tile.warn .v {{ color: {ACCENT}; }} .bp-tile.bad .v {{ color: {CORAL}; }}

/* tabs */
button[role="tab"] {{ font-family: {FONT_MONO}; font-size: .85rem; color: {INK_DIM}; }}
button[role="tab"][aria-selected="true"] {{ color: {ACCENT}; }}
[data-baseweb="tab-highlight"] {{ background-color: {ACCENT} !important; }}
[data-baseweb="tab-border"] {{ background-color: {LINE} !important; }}

/* square corners everywhere, like the site */
.stButton > button, .stDownloadButton > button, [data-baseweb="input"], [data-baseweb="select"] > div,
[data-baseweb="base-input"], [data-testid="stFileUploaderDropzone"], [data-testid="stAlert"],
[data-testid="stExpander"], [data-testid="stDataFrame"] {{ border-radius: 0 !important; }}
.stButton > button, .stDownloadButton > button {{ font-family: {FONT_MONO}; font-size: .85rem;
  border: 1px solid {LINE_STRONG}; background: transparent; color: {INK}; }}
.stButton > button:hover, .stDownloadButton > button:hover {{ border-color: {ACCENT}; color: {ACCENT}; }}

[data-testid="stAlert"] {{ border: 1px solid {LINE_STRONG}; border-left-width: 3px; background: {PANEL}; }}
[data-testid="stExpander"] {{ border: 1px solid {LINE_STRONG}; background: {PANEL}; }}
[data-testid="stExpander"] summary {{ font-family: {FONT_MONO}; font-size: .85rem; }}
hr {{ border-color: {LINE}; }}
</style>
"""


def _register_plotly_template():
    axis = dict(gridcolor=LINE, linecolor=LINE_STRONG, zeroline=False,
                tickfont=dict(family=FONT_MONO, size=11, color=INK_DIM),
                title=dict(font=dict(family=FONT_MONO, size=12, color=INK_DIM)),
                ticks="outside", tickcolor=LINE_STRONG)
    pio.templates["blueprint"] = go.layout.Template(layout=go.Layout(
        colorway=SERIES,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_BODY, color=INK, size=13),
        title=dict(font=dict(family=FONT_DISPLAY, size=17, color=INK), x=0, xanchor="left"),
        xaxis=axis, yaxis=axis,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(family=FONT_MONO, size=11, color=INK_DIM), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=PANEL, bordercolor=ACCENT,
                        font=dict(family=FONT_MONO, size=12, color=INK)),
        margin=dict(l=56, r=24, t=64, b=48),
        bargap=0.08,
    ))
    pio.templates.default = "blueprint"


def apply_theme():
    """Inject site CSS + fonts and make 'blueprint' the default Plotly template."""
    st.markdown(_CSS, unsafe_allow_html=True)
    _register_plotly_template()


def header(title, subtitle="", eyebrow="Project"):
    """Page header in the site's style (back link, mono eyebrow, display title, dim subtitle)."""
    sub = f'<p class="bp-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<div class="bp-hero">'
        f'<a class="bp-back" href="https://ricardoagonzalezc.github.io" target="_blank">'
        f'← ricardoagonzalezc.github.io</a>'
        f'<div class="bp-eyebrow" style="margin-top:18px">{eyebrow}</div>'
        f'<h1>{title}</h1>{sub}</div>',
        unsafe_allow_html=True)


def label(text):
    """Small mono caps label (like the site's section labels)."""
    st.markdown(f'<div class="bp-label">{text}</div>', unsafe_allow_html=True)


def tile(label, value, sub="", status=""):
    """HTML stat tile. status: '', 'ok', 'warn' or 'bad' (colours the value; text label always present)."""
    return (f'<div class="bp-tile {status}"><div class="k">{label}</div>'
            f'<div class="v">{value}</div><div class="s">{sub}&nbsp;</div></div>')
