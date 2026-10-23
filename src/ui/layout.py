"""
Main Layout & Dual-Pane Orchestrator.
"""
import streamlit as st
from src.mock.telemetry_generator import EvaluationSession
from src.ui.styles import render_html
from src.ui.components.badge import render_evaluation_badge
from src.ui.components.kpi_cards import render_kpi_cards
from src.ui.components.charts import render_probability_chart
from src.ui.components.transcript_viewer import render_media_and_transcript_viewer
from src.ui.components.pedagogical_dimensions import render_pedagogical_dimensions
from src.models.evaluator import run_evaluation, apply_evaluation_to_session


def render_header():
    """Render top brand banner and system info."""
    render_html("""
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


def render_empty_dashboard_placeholder():
    """Render a clean placeholder card before user media input is provided."""
    render_html("""
    <div style="background: #ffffff; border: 1.5px dashed #cbd5e1; border-radius: 14px; padding: 2.75rem 1.75rem; text-align: center; margin-top: 0.5rem;">
        <div style="font-size: 2.75rem; margin-bottom: 0.75rem;">📊</div>
        <div style="font-size: 1.15rem; font-weight: 700; color: #1e293b; margin-bottom: 0.35rem;">
            Awaiting Classroom Media Input
        </div>
        <div style="font-size: 0.88rem; color: #64748b; max-width: 440px; margin: 0 auto 1.75rem auto; line-height: 1.5;">
            Ingest an 8x8 recording stream URL or upload classroom media on the left to generate the pedagogical assessment, telemetry metrics, and coaching insights.
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; text-align: left; max-width: 500px; margin: 0 auto;">
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem 0.9rem;">
                <div style="font-weight: 700; font-size: 0.82rem; color: #334155;">🛡️ Zero Biometric Retention</div>
                <div style="font-size: 0.74rem; color: #64748b; margin-top: 0.2rem;">Human faces discarded; content-only slide analytics.</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem 0.9rem;">
                <div style="font-weight: 700; font-size: 0.82rem; color: #334155;">🎧 Ephemeral Audio VAD</div>
                <div style="font-size: 0.74rem; color: #64748b; margin-top: 0.2rem;">Normalized audio evicted immediately post-Whisper.</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem 0.9rem;">
                <div style="font-weight: 700; font-size: 0.82rem; color: #334155;">🔒 PII-Scrubbed Transcripts</div>
                <div style="font-size: 0.74rem; color: #64748b; margin-top: 0.2rem;">Option A redaction for emails, phones, IDs, & names.</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem 0.9rem;">
                <div style="font-weight: 700; font-size: 0.82rem; color: #334155;">🧠 Pedagogical LLM Rationale</div>
                <div style="font-size: 0.74rem; color: #64748b; margin-top: 0.2rem;">4 dimension sub-scores & evidence-based coaching.</div>
            </div>
        </div>
    </div>
    """)


def render_dashboard_layout(session: EvaluationSession = None):
    """Render the dual-pane interface: Left for media/evidence, Right for grading dashboard."""
    render_header()
    
    col_left, col_right = st.columns([1, 1.3], gap="large")
    
    with col_left:
        render_media_and_transcript_viewer(session)
        
    with col_right:
        render_html('<div class="pane-header">📊 Pedagogical Assessment & Coaching Dashboard</div>')
        
        active_media = st.session_state.get("ingested_media")
        
        # Hide result elements until user has provided media input
        if active_media is None or session is None:
            render_empty_dashboard_placeholder()
        else:
            # Ensure pedagogical evaluation is computed for the active session
            if getattr(session, "pedagogical_evaluation", None) is None:
                telemetry = getattr(session, "telemetry", {})
                snippets = getattr(session, "transcript_snippets", [])
                duration_str = getattr(session, "duration_str", "45:00")
                eval_res = run_evaluation(telemetry, snippets, duration_str)
                apply_evaluation_to_session(session, eval_res)

            # 1. Executive Grade Badge & Diagnostic Synthesis
            render_evaluation_badge(session)
            
            # 2. Objective Telemetry KPI Grid
            render_kpi_cards(session.telemetry)
            
            # 3. Pedagogical Dimension Sub-Scores & Coaching
            render_pedagogical_dimensions(session.pedagogical_evaluation)
            
            # 4. Model Decision Confidence Distribution
            st.markdown("#### 🔬 Decision Confidence Distribution")
            render_probability_chart(session.probabilities, session.tier.value)
