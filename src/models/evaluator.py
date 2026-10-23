"""
Top-Level Evaluator Interface.
Coordinates LLM judgement and applies results to EvaluationSession.
"""
from typing import Dict, List, Any
from src.models.schema import PedagogicalEvaluation, EvaluationSession, QualityTier
from src.models.llm_judge import evaluate_with_llm


def run_evaluation(
    telemetry: Dict[str, Any],
    transcript_snippets: List[Any],
    duration_str: str = "45:00",
) -> PedagogicalEvaluation:
    """Run pedagogical assessment using direct LLM or local rubric fallback."""
    return evaluate_with_llm(telemetry, transcript_snippets, duration_str)


def apply_evaluation_to_session(
    session: EvaluationSession,
    eval_res: PedagogicalEvaluation
) -> EvaluationSession:
    """Update EvaluationSession fields in-place with the latest pedagogical evaluation."""
    # Map tier string to QualityTier enum
    tier_mapping = {
        "poor": QualityTier.POOR,
        "average": QualityTier.AVERAGE,
        "good": QualityTier.GOOD,
        "excellent": QualityTier.EXCELLENT,
    }
    session.tier = tier_mapping.get(eval_res.overall_tier.lower(), QualityTier.GOOD)
    session.probabilities = eval_res.confidence_distribution
    session.confidence = eval_res.confidence_distribution.get(eval_res.overall_tier, 0.70)
    session.summary_headline = f"{eval_res.overall_tier} Pedagogical Quality ({eval_res.inference_source})"
    session.summary_rationale = eval_res.executive_summary
    session.coaching_tips = eval_res.coaching_recommendations
    
    # Compute composite overall score from dimension sub-scores
    if eval_res.dimension_scores:
        session.overall_score = sum(d.score for d in eval_res.dimension_scores) / len(eval_res.dimension_scores)
    
    # Store full evaluation structure on the session
    session.pedagogical_evaluation = eval_res
    return session
