"""
8x8 Class Quality Evaluator - Streamlit Application Entrypoint
Target Platform: Hugging Face Spaces (Streamlit SDK)
"""
import streamlit as st
from src.ui.styles import CUSTOM_CSS
from src.ui.layout import render_dashboard_layout
from src.mock.telemetry_generator import get_scenario


# Set Streamlit page configuration for pure dual-pane presentation
st.set_page_config(
    page_title="8x8 Class Quality Evaluator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject custom design system CSS
st.html(CUSTOM_CSS)


def init_session_state():
    """Initialize persistent session state for evaluation data and ingested media."""
    if "session_data" not in st.session_state:
        st.session_state.session_data = get_scenario("interactive")
    if "ingested_media" not in st.session_state:
        st.session_state.ingested_media = None


def main():
    init_session_state()
    
    # Render strictly two-panel layout driven by session state
    render_dashboard_layout(st.session_state.session_data)


if __name__ == "__main__":
    main()
