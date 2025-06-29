# ────────────────  src/streamlit_app.py  ────────────────
"""
Granite Legal Risk Analyzer – Streamlit frontend
• Upload a PDF/DOCX contract
• Enter contract value ($) and optional impact-factor slider
• Display risk clauses in expandable cards sorted by severity
"""

import streamlit as st
import pandas as pd

from src.extract_text import extract_text
from src.risk_engine  import score_risk

# ── page config & tidy up ────────────────────────────────────────
st.set_page_config(
    page_title="AI Contract Risk Analyzer",
    layout="wide",
    initial_sidebar_state="expanded",
)
# hide the default Streamlit menu & footer
st.markdown("""
    <style>
      #MainMenu {visibility: hidden;}
      footer     {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ── header ───────────────────────────────────────────────────────
# Custom CSS to align the title
st.markdown(
    """
    <style>
    .title {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit app with custom CSS class for the title
st.markdown('<h1 class="title">Granite-Powered Contract Risk Analyzer</h1>', unsafe_allow_html=True)


# st.title("⚖️ Granite-Powered Contract Risk Analyzer")
st.markdown('<h6 class="title">Not legal advice – demo for IBM Hackathon 2025.', unsafe_allow_html=True)

# st.caption("Not legal advice – demo for IBM Hackathon 2025.")

# ── sidebar: impact factor slider ────────────────────────────────
impact_factor = st.sidebar.slider(
    "Risk ➜ $-impact factor",
    min_value=0.00005, max_value=0.00100,
    step=0.00005, value=0.00010,
    format="%.5f",
    help="Multiply each risk score by this to get $ impact"
)

# ── main inputs ─────────────────────────────────────────────────
col1, col2 = st.columns([3,1])
with col1:
    uploaded_file = st.file_uploader(
        "Upload contract (PDF or DOCX)",
        type=["pdf","docx"],
        help="Drag & drop or click to browse"
    )
with col2:
    contract_value = st.number_input(
        "Contract value (USD)",
        min_value=1_000, max_value=10_000_000,
        value=100_000, step=1_000,
        help="Approximate deal size → scales dollar impacts"
    )

analyze = st.button("🔎 Analyze", disabled=uploaded_file is None)

# ── badge styling helper ─────────────────────────────────────────
def badge_style(score:int):
    if score >= 9:
        return "#d7191c","white"
    if score >= 7:
        return "#fdae61","black"
    if score >= 4:
        return "#ffffbf","black"
    return "#a6d96a","black"

# ── run analysis ────────────────────────────────────────────────
if analyze and uploaded_file:
    with st.spinner("Extracting text…"):
        text = extract_text(uploaded_file)
    with st.spinner("Scoring risks with Granite…"):
        risks = score_risk(text, contract_value, impact_factor)

    if not risks:
        st.info("No risky clauses detected.")
        st.session_state.pop("df", None)
    else:
        df = pd.DataFrame(risks).drop(columns=["id"], errors="ignore")
        # … after df = pd.DataFrame(risks) …
        df = df.drop_duplicates("clause").sort_values("score", ascending=False)
        # clean mojibake
        for c in ["clause","reason","mitigation"]:
            df[c] = df[c].str.replace("â€™","’",regex=False)
        # title-case owner
        df["owner"] = df["owner"].str.title()
        st.session_state["df"] = df.reset_index(drop=True)

# ── render each clause as an expander “card” ─────────────────────
if "df" in st.session_state:
    df = st.session_state["df"]
    st.subheader("📄 Detected Risk Clauses")

    # … above, define ACRONYMS once …
    ACRONYMS = {"ip", "nda", "eula", "sla", "msa",
                "pii", "gdpr", "cisg", "exw", "fca", "d/p"}

    for idx, row in df.iterrows():

        # build badge …
        bg, fg = badge_style(int(row.score))
        badge = (
            f"<span style='background-color:{bg};"
            f"color:{fg};padding:4px 8px;"
            "border-radius:4px;font-weight:bold;'>"
            f"{row.score}</span>"
        )

        # acronym‐aware display of the risk type
        rt_raw      = row.risk_type.replace("_", " ")
        display_rt  = rt_raw.upper() if rt_raw.lower() in ACRONYMS else rt_raw.title()

        # NOW use display_rt in the expander title
        with st.expander(f"Clause {idx+1} — {display_rt}", expanded=False):
            # render badge inside body
            st.markdown(badge, unsafe_allow_html=True)

            st.markdown(f"**Clause Text:**  \n{row.clause}")
            st.markdown(f"**Impact (USD):**  ${row.impact_usd:,.2f}")

            cols = st.columns(2)
            with cols[0]:
                st.markdown(f"**Risk Type:** {display_rt}")
                st.markdown(f"**Owner:**     {row.owner}")
            with cols[1]:
                st.markdown(f"**Reason:**     {row.reason}")
                st.markdown(f"**Mitigation:** {row.mitigation}")


    # download CSV
    csv_data = df.to_csv(index=False).encode()
    st.download_button("Download CSV", csv_data,
                    file_name="risk_report.csv",
                    mime="text/csv")
else:
    st.info("Upload a contract and click **Analyze** to begin.")
