"""
8x8 Class Quality Evaluator - Streamlit Application Entrypoint
Target Platform: Streamlit Community Cloud / Modern Container
"""
import streamlit as st
from src.ui.styles import CUSTOM_CSS
from src.ui.layout import render_dashboard_layout


# Set Streamlit page configuration for pure dual-pane presentation
st.set_page_config(
    page_title="8x8 Class Quality Evaluator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject custom design system CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_session_state():
    """Initialize persistent session state for evaluation data and ingested media."""
    # Force eviction of any legacy mock session state retained in browser memory
    if "session_data" in st.session_state and st.session_state.session_data is not None:
        if getattr(st.session_state.session_data, "scenario_id", "") in ["interactive", "lecture", "disengaged", "chaotic"]:
            st.session_state.session_data = None
            st.session_state.ingested_media = None

    if "session_data" not in st.session_state:
        st.session_state.session_data = None
    if "ingested_media" not in st.session_state:
        st.session_state.ingested_media = None


def main():
    init_session_state()
    
    # Render strictly two-panel layout driven by session state
    render_dashboard_layout(st.session_state.session_data)


if __name__ == "__main__":
    main()
