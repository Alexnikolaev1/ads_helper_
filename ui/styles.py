CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

  :root {
    --green:   #10B981;
    --green2:  #059669;
    --green-glow: rgba(16,185,129,0.18);
    --bg:      #0A0D0F;
    --surface: #111418;
    --card:    #161B22;
    --border:  #1F2937;
    --text:    #E5E7EB;
    --muted:   #6B7280;
    --warn:    #F59E0B;
    --radius:  14px;
  }

  html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Manrope', sans-serif !important;
  }

  [data-testid="stHeader"] { background: transparent !important; }
  [data-testid="stToolbar"] { display: none !important; }
  .block-container { padding: 1.5rem 1rem 3rem !important; max-width: 860px !important; }

  [data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
  }
  [data-testid="stSidebar"] .block-container { max-width: 100% !important; padding-top: 1rem !important; }
  [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: var(--text) !important;
    font-size: 0.95rem !important;
  }

  .hero-wrap { text-align: center; padding: 2rem 1rem 1.2rem; }
  .hero-badge {
    display: inline-block;
    background: var(--green-glow);
    border: 1px solid var(--green);
    color: var(--green);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 999px;
    margin-bottom: 1rem;
  }
  .hero-title {
    font-size: clamp(1.6rem, 4.5vw, 2.5rem);
    font-weight: 800;
    line-height: 1.15;
    color: #fff;
    margin: 0 0 0.7rem;
  }
  .hero-title span { color: var(--green); }
  .hero-sub { color: var(--muted); font-size: 0.95rem; max-width: 520px; margin: 0 auto; line-height: 1.55; }

  .stats-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 0.5rem 0 1rem;
  }
  .stat-pill {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 6px 12px;
    font-size: 0.75rem;
    color: var(--muted);
  }
  .stat-pill strong { color: var(--text); }
  .stat-pill.warn { border-color: var(--warn); color: var(--warn); }

  .post-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.3rem;
    margin-bottom: 0.6rem;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .post-card:hover {
    border-color: var(--green);
    box-shadow: 0 0 24px rgba(16,185,129,0.08);
  }
  .post-badge {
    display: inline-block;
    background: var(--green-glow);
    border: 1px solid var(--green);
    color: var(--green);
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 3px 9px;
    border-radius: 999px;
    margin-bottom: 0.7rem;
  }
  .post-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.7;
    color: var(--text);
    white-space: pre-wrap;
    word-break: break-word;
  }

  .stTextArea textarea, .stTextInput input {
    background: var(--card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: 'Manrope', sans-serif !important;
  }
  .stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 3px var(--green-glow) !important;
  }
  label[data-testid="stWidgetLabel"] p {
    color: var(--text) !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
  }

  .stButton > button {
    background: linear-gradient(135deg, var(--green), var(--green2)) !important;
    color: #fff !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: var(--radius) !important;
    box-shadow: 0 4px 20px rgba(16,185,129,0.28) !important;
    transition: transform 0.15s, opacity 0.2s !important;
  }
  .stButton > button:hover { opacity: 0.92; transform: translateY(-1px); }
  div[data-testid="stButton"] button[kind="secondary"] {
    background: var(--card) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
  }

  .stSelectbox div[data-baseweb="select"] > div,
  .stMultiSelect div[data-baseweb="select"] > div {
    background: var(--card) !important;
    border-color: var(--border) !important;
    border-radius: var(--radius) !important;
  }

  .promo-banner {
    background: linear-gradient(135deg, #0F1F17 0%, #0A1A14 100%);
    border: 1px solid var(--green);
    border-radius: var(--radius);
    padding: 1.3rem 1.5rem;
    text-align: center;
    margin-top: 2rem;
  }
  .promo-banner h3 { color: var(--green); font-size: 1rem; margin: 0 0 0.4rem; }
  .promo-banner p { color: var(--muted); font-size: 0.85rem; margin: 0; line-height: 1.55; }

  .hint-box {
    background: var(--card);
    border: 1px dashed var(--border);
    border-radius: var(--radius);
    padding: 0.9rem 1rem;
    color: var(--muted);
    font-size: 0.82rem;
    line-height: 1.5;
    margin-bottom: 1rem;
  }

  .demo-showcase {
    margin: 2.2rem auto 0;
    max-width: 520px;
    padding: 0 0.5rem 1rem;
  }
  .demo-showcase-title {
    text-align: center;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 0 0 1rem;
  }
  .demo-brief-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    background: rgba(16,185,129,0.06);
    border: 1px solid rgba(16,185,129,0.22);
    border-radius: 12px;
    padding: 10px 12px;
    margin-bottom: 12px;
  }
  .demo-brief-icon { font-size: 1rem; line-height: 1.4; flex-shrink: 0; }
  .demo-brief-text {
    font-size: 0.8rem;
    line-height: 1.5;
    color: #9CA3AF;
    margin: 0;
  }
  .demo-brief-text strong { color: var(--green); font-weight: 600; }
  .demo-connector {
    text-align: center;
    color: var(--green);
    font-size: 1.1rem;
    margin: 4px 0 10px;
    opacity: 0.85;
  }
  .demo-post-shell {
    background: linear-gradient(165deg, #1a222c 0%, #141a22 100%);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 0;
    overflow: hidden;
    box-shadow: 0 12px 40px rgba(0,0,0,0.35), 0 0 0 1px rgba(16,185,129,0.06);
  }
  .demo-post-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 14px;
    border-bottom: 1px solid var(--border);
    background: rgba(0,0,0,0.15);
  }
  .demo-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--green), #047857);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
  }
  .demo-channel-name {
    font-size: 0.88rem;
    font-weight: 700;
    color: #fff;
    margin: 0;
    line-height: 1.2;
  }
  .demo-channel-meta {
    font-size: 0.7rem;
    color: var(--muted);
    margin: 2px 0 0;
  }
  .demo-post-body {
    padding: 16px 16px 18px;
    font-size: 0.92rem;
    line-height: 1.65;
    color: var(--text);
    white-space: pre-wrap;
    word-break: break-word;
  }
  .demo-footnote {
    text-align: center;
    font-size: 0.75rem;
    color: var(--muted);
    margin: 12px 0 0;
    line-height: 1.45;
  }

  hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }
  .stSpinner > div { border-top-color: var(--green) !important; }
  #MainMenu, footer { visibility: hidden !important; }
</style>
"""
