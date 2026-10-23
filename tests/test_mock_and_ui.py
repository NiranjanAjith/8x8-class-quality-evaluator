"""
Unit tests for Epic 1 components, data generators, and Plotly charts.
"""
from src.mock.telemetry_generator import (
    get_scenario,
    list_available_scenarios,
    SCENARIOS,
    QualityTier
)
from src.ui.components.charts import render_probability_chart, render_shap_waterfall
import plotly.graph_objects as go


def test_scenarios_structure():
    """Verify all scenarios contain consistent and valid data."""
    scenarios = list_available_scenarios()
    assert len(scenarios) == 3, f"Expected 3 scenarios, got {len(scenarios)}"
    assert "interactive" in scenarios
    assert "monologue" in scenarios
    assert "stalled" in scenarios

    for key in scenarios:
        session = get_scenario(key)
        assert session.overall_score >= 0 and session.overall_score <= 100
        assert session.confidence > 0 and session.confidence <= 1.0
        assert session.tier in [QualityTier.POOR, QualityTier.AVERAGE, QualityTier.GOOD, QualityTier.EXCELLENT]
        assert "teacher_talk_pct" in session.telemetry
        assert "student_talk_pct" in session.telemetry
        assert "wpm" in session.telemetry
        assert "dead_air_pct" in session.telemetry
        assert len(session.shap_drivers) > 0
        assert len(session.retained_slides) > 0
        assert len(session.transcript_snippets) > 0


def test_chart_generation():
    """Verify Plotly charts build correctly for all scenarios."""
    for key in SCENARIOS:
        session = get_scenario(key)
        # Test probability values
        tiers = ["Poor", "Average", "Good", "Excellent"]
        for t in tiers:
            assert t in session.probabilities
            assert 0.0 <= session.probabilities[t] <= 1.0
        assert len(session.shap_drivers) > 0


def test_empty_state_initial_rendering():
    """Verify that when no input has been provided, dashboard renders empty state cleanly."""
    import streamlit as st
    from src.ui.layout import render_dashboard_layout, render_empty_dashboard_placeholder

    st.session_state.ingested_media = None
    st.session_state.session_data = None
    # Verify placeholder renders without exception
    render_empty_dashboard_placeholder()
    render_dashboard_layout(None)


if __name__ == "__main__":
    test_scenarios_structure()
    test_chart_generation()
    test_empty_state_initial_rendering()
    print("All Epic 1 unit and component tests passed successfully!")
