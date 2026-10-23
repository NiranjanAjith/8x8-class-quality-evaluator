"""
Unit & Integration Tests for Epic 5: LLM Pedagogical Judgement & Explanations.
"""
from src.models.schema import DimensionScore, PedagogicalEvaluation
from src.models.prompt_builder import build_pedagogical_prompt
from src.models.llm_judge import evaluate_with_local_rubric, _parse_json_evaluation, evaluate_with_llm
from src.models.evaluator import run_evaluation, apply_evaluation_to_session
from src.mock.telemetry_generator import get_scenario, QualityTier, TranscriptSnippet


def test_pedagogical_prompt_builder():
    """Verify prompt builder formats telemetry metrics and sanitized transcripts properly."""
    telemetry = {
        "dead_air_pct": 14.5,
        "wpm": 142,
        "question_density": 16.0,
        "total_questions": 12,
        "teacher_talk_pct": 65.0,
        "student_talk_pct": 35.0,
        "slide_count": 4,
        "slide_velocity_min": 0.35,
    }
    snippets = [
        TranscriptSnippet(
            timestamp="00:15",
            speaker="[Teacher]",
            text="Can anyone explain the main concept?",
            keyframe_id="frame_01",
            pedagogical_tag="Interrogative Prompt",
            explanation="Encouraging participation"
        )
    ]
    prompt = build_pedagogical_prompt(telemetry, snippets, "45:00")
    assert "14.5%" in prompt
    assert "142 WPM" in prompt
    assert "16.0/hr" in prompt
    assert "[Teacher]" in prompt
    assert "Can anyone explain the main concept?" in prompt
    assert "PEDAGOGICAL ASSESSMENT RUBRIC" in prompt


def test_deterministic_rubric_evaluator_high_engagement():
    """Verify local rubric evaluator assigns high score to an interactive session."""
    interactive_telemetry = {
        "dead_air_pct": 8.5,
        "wpm": 140,
        "question_density": 18.0,
        "total_questions": 14,
        "teacher_talk_pct": 60.0,
        "student_talk_pct": 40.0,
        "slide_count": 5,
        "slide_velocity_min": 0.4,
    }
    eval_res = evaluate_with_local_rubric(interactive_telemetry, [], "42:00")
    assert eval_res.overall_tier in ["Good", "Excellent"]
    assert len(eval_res.dimension_scores) == 4
    assert sum(eval_res.confidence_distribution.values()) == 1.0
    assert len(eval_res.observed_strengths) >= 2
    assert len(eval_res.coaching_recommendations) >= 1
    assert "140 WPM" in eval_res.observed_strengths[0] or "speech tempo" in eval_res.observed_strengths[0]


def test_deterministic_rubric_evaluator_poor_monologue():
    """Verify local rubric evaluator penalizes excessive dead air and low interaction."""
    poor_telemetry = {
        "dead_air_pct": 28.0,
        "wpm": 185,
        "question_density": 2.0,
        "total_questions": 1,
        "teacher_talk_pct": 96.0,
        "student_talk_pct": 4.0,
        "slide_count": 0,
        "slide_velocity_min": 0.0,
    }
    eval_res = evaluate_with_local_rubric(poor_telemetry, [], "30:00")
    assert eval_res.overall_tier in ["Poor", "Average"]
    assert eval_res.confidence_distribution["Poor"] > 0.5
    # Pacing and engagement sub-scores should reflect the issue
    dim_dict = {d.name: d.score for d in eval_res.dimension_scores}
    assert dim_dict["Student Engagement"] <= 50
    assert dim_dict["Pacing & Delivery"] <= 50


def test_parse_json_evaluation():
    """Verify parser deserializes LLM JSON output to PedagogicalEvaluation."""
    raw_json = {
        "overall_tier": "Good",
        "confidence_distribution": {"Poor": 0.05, "Average": 0.15, "Good": 0.70, "Excellent": 0.10},
        "executive_summary": "Session exhibited steady pacing and structured inquiry.",
        "dimension_scores": [
            {"name": "Instructional Clarity", "score": 85, "benchmark_status": "Optimal", "feedback": "Clear progression"},
            {"name": "Student Engagement", "score": 75, "benchmark_status": "Acceptable", "feedback": "Good response rate"}
        ],
        "observed_strengths": ["Clear articulation", "Active checks"],
        "coaching_recommendations": ["Expand open inquiry"]
    }
    eval_res = _parse_json_evaluation(raw_json, source="Test LLM")
    assert eval_res.overall_tier == "Good"
    assert eval_res.inference_source == "Test LLM"
    assert len(eval_res.dimension_scores) == 2
    assert eval_res.dimension_scores[0].score == 85


def test_apply_evaluation_to_session():
    """Verify session is mutated properly by apply_evaluation_to_session."""
    session = get_scenario("interactive")
    eval_res = evaluate_with_local_rubric(session.telemetry, session.transcript_snippets, session.duration_str)
    session = apply_evaluation_to_session(session, eval_res)

    assert session.tier.value.lower() == eval_res.overall_tier.lower()
    assert session.summary_rationale == eval_res.executive_summary
    assert session.coaching_tips == eval_res.coaching_recommendations
    assert session.pedagogical_evaluation is not None
    assert len(session.pedagogical_evaluation.dimension_scores) == 4


if __name__ == "__main__":
    test_pedagogical_prompt_builder()
    test_deterministic_rubric_evaluator_high_engagement()
    test_deterministic_rubric_evaluator_poor_monologue()
    test_parse_json_evaluation()
    test_apply_evaluation_to_session()
    print("All Epic 5 pedagogical evaluation & LLM tests passed successfully!")
