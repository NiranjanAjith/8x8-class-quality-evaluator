"""
Main Layout & Dual-Pane Orchestrator.
"""
import streamlit as st
from src.mock.telemetry_generator import EvaluationSession
from src.ui.components.badge import render_evaluation_badge
from src.ui.components.kpi_cards import render_kpi_cards
from src.ui.components.charts import render_probability_chart
from src.ui.components.transcript_viewer import render_media_and_transcript_viewer
from src.ui.components.pedagogical_dimensions import render_pedagogical_dimensions
from src.models.evaluator import run_evaluation, apply_evaluation_to_session


def render_header():
    """Render top brand banner and system info."""
    st.html("""
    <div class="main-title">
        <span>🎓 8x8 Class Quality Evaluator</span>
        <span style="font-size: 0.8rem; background: #e0e7ff; color: #4338ca; padding: 0.2rem 0.6rem; border-radius: 12px; font-weight: 700;">
            Production Edition &bull; Privacy-First
        </span>
    </div>
    <div class="sub-title">
        Air-gapped pedagogical analytics &bull; Content-only visual telemetry &bull; In-memory audio eviction &bull; LLM Judgement & Explanations
    </div>
    """)


def render_dashboard_layout(session: EvaluationSession):
    """Render the dual-pane interface: Left for media/evidence, Right for grading dashboard."""
    # Ensure pedagogical evaluation is computed for the active session
    if getattr(session, "pedagogical_evaluation", None) is None:
        eval_res = run_evaluation(session.telemetry, session.transcript_snippets, session.duration_str)
        apply_evaluation_to_session(session, eval_res)

    render_header()
    
    col_left, col_right = st.columns([1, 1.3], gap="large")
    
    with col_left:
        render_media_and_transcript_viewer(session)
        
    with col_right:
        st.html('<div class="pane-header">📊 Pedagogical Assessment & Coaching Dashboard</div>')
        
        # 1. Executive Grade Badge & Diagnostic Synthesis
        render_evaluation_badge(session)
        
        # 2. Objective Telemetry KPI Grid
        render_kpi_cards(session.telemetry)
        
        # 3. Pedagogical Dimension Sub-Scores & Coaching
        render_pedagogical_dimensions(session.pedagogical_evaluation)
        
        # 4. Model Decision Confidence Distribution
        st.markdown("#### 🔬 Decision Confidence Distribution")
        render_probability_chart(session.probabilities, session.tier.value)
