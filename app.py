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


def main():
    # Load primary evaluation session data
    session_data = get_scenario("interactive")
    
    # Render strictly two-panel layout (Left: Input & Evidence, Right: Assessment Dashboard)
    render_dashboard_layout(session_data)


if __name__ == "__main__":
    main()
