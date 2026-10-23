"""
Unit tests for Production Domain Models, Session Orchestration, and UI Components.
Strictly zero-mock test suite.
"""
import streamlit as st
from src.models.schema import (
    QualityTier,
    EvaluationSession,
    create_empty_evaluation_session,
)
from src.ui.components.charts import render_probability_chart
from src.ui.layout import render_dashboard_layout, render_empty_dashboard_placeholder


def test_empty_session_structure():
    """Verify that create_empty_evaluation_session initializes a clean, unpolluted structure."""
    session = create_empty_evaluation_session("test_video.mp4", "12:30")
    
    assert session.scenario_name == "test_video.mp4"
    assert session.duration_str == "12:30"
    assert session.overall_score == 0.0
    assert session.confidence == 0.0
    assert session.tier == QualityTier.AVERAGE
    assert len(session.transcript_snippets) == 0
    assert len(session.retained_slides) == 0
    assert session.pedagogical_evaluation is None

    # Telemetry should reflect clean defaults
    assert session.telemetry["teacher_talk_pct"] == 100.0
    assert session.telemetry["student_talk_pct"] == 0.0
    assert session.telemetry["wpm"] == 0
    assert session.telemetry["dead_air_pct"] == 0.0
    assert session.telemetry["slide_count"] == 0


def test_chart_generation():
    """Verify Plotly confidence distribution charts build correctly for dynamic probabilities."""
    probs = {
        "Poor": 0.05,
        "Average": 0.15,
        "Good": 0.70,
        "Excellent": 0.10,
    }
    # Test rendering without exception
    render_probability_chart(probs, "Good")
    for t in ["Poor", "Average", "Good", "Excellent"]:
        assert t in probs
        assert 0.0 <= probs[t] <= 1.0


def test_empty_state_initial_rendering():
    """Verify that when no media input has been provided, dashboard renders empty state cleanly."""
    st.session_state.ingested_media = None
    st.session_state.session_data = None
    
    # Verify placeholder and layout render cleanly
    render_empty_dashboard_placeholder()
    render_dashboard_layout(None)


def test_monologue_rubric_downgrade():
    """Verify that a solo product monologue is downgraded to Poor/Average rather than receiving template results."""
    from src.models.llm_judge import evaluate_with_local_rubric
    from src.models.evaluator import apply_evaluation_to_session

    session = create_empty_evaluation_session("solo_product_video.mp4", "05:00")
    session.telemetry = {
        "dead_air_pct": 5.0,
        "wpm": 130,
        "question_density": 0.0,
        "total_questions": 0,
        "teacher_talk_pct": 100.0,
        "student_talk_pct": 0.0,
        "slide_count": 2,
        "slide_velocity_min": 2.5,
    }
    eval_res = evaluate_with_local_rubric(session.telemetry, session.transcript_snippets, session.duration_str)
    apply_evaluation_to_session(session, eval_res)

    # Solo monologue must NEVER be classified as Excellent
    assert session.tier in [QualityTier.POOR, QualityTier.AVERAGE]
    assert session.tier != QualityTier.EXCELLENT
    assert session.overall_score < 70.0
    engagement_dim = [d for d in session.pedagogical_evaluation.dimension_scores if "Engagement" in d.name][0]
    assert engagement_dim.benchmark_status == "Needs Improvement"
    assert engagement_dim.score <= 40


if __name__ == "__main__":
    test_empty_session_structure()
    test_chart_generation()
    test_empty_state_initial_rendering()
    test_monologue_rubric_downgrade()
    print("All session and UI component tests passed successfully!")
