"""
Main Layout & Dual-Pane Orchestrator.
"""
import streamlit as st
from src.mock.telemetry_generator import EvaluationSession
from src.ui.components.badge import render_evaluation_badge
from src.ui.components.kpi_cards import render_kpi_cards
from src.ui.components.charts import render_probability_chart, render_shap_waterfall
from src.ui.components.transcript_viewer import render_media_and_transcript_viewer


def render_header():
    """Render top brand banner and system info."""
    st.html("""
    <div class="main-title">
        <span>🎓 8x8 Class Quality Evaluator</span>
        <span style="font-size: 0.8rem; background: #e0e7ff; color: #4338ca; padding: 0.2rem 0.6rem; border-radius: 12px; font-weight: 700;">
            Hugging Face Spaces &bull; CPU Edition
        </span>
    </div>
    <div class="sub-title">
        Air-gapped pedagogical analytics &bull; Content-only visual telemetry &bull; In-memory audio eviction &bull; Explainable SHAP attributions
    </div>
    """)


def render_dashboard_layout(session: EvaluationSession):
    """Render the dual-pane interface: Left for media/evidence, Right for grading dashboard."""
    render_header()
    
    col_left, col_right = st.columns([1, 1.3], gap="large")
    
    with col_left:
        render_media_and_transcript_viewer(session)
        
    with col_right:
        st.html('<div class="pane-header">📊 Pedagogical Assessment & Coaching Dashboard</div>')
        
        # 1. Executive Grade Badge & Coaching Tips
        render_evaluation_badge(session)
        
        # 2. Telemetry KPI Grid
        render_kpi_cards(session.telemetry)
        
        # 3. Model Probabilities & Explainability Section
        st.markdown("#### 🔬 Decision Confidence & Feature Attributions")
        render_probability_chart(session.probabilities, session.tier.value)
        render_shap_waterfall(session.shap_drivers)
