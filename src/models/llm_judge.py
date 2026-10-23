"""
LLM Pedagogical Judgement & Rubric Evaluation Engine.
Provides direct LLM evaluation with resilient, deterministic local rubric fallback.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
from src.models.schema import PedagogicalEvaluation, DimensionScore
from src.models.prompt_builder import build_pedagogical_prompt

logger = logging.getLogger(__name__)


def evaluate_with_local_rubric(
    telemetry: Dict[str, Any],
    transcript_snippets: List[Any],
    duration_str: str = "45:00",
) -> PedagogicalEvaluation:
    """
    Deterministic, zero-dependency pedagogical rubric evaluator.
    Computes dimension sub-scores, overall quality tier, calibrated confidence,
    executive diagnostic summary, strengths, and actionable coaching tips.
    """
    dead_air = float(telemetry.get("dead_air_pct", 10.0))
    wpm = int(telemetry.get("wpm", 135))
    q_density = float(telemetry.get("question_density", 12.0))
    q_total = int(telemetry.get("total_questions", 8))
    teacher_talk = float(telemetry.get("teacher_talk_pct", 75.0))
    student_talk = float(telemetry.get("student_talk_pct", 25.0))
    slide_count = int(telemetry.get("slide_count", 3))
    slide_vel = float(telemetry.get("slide_velocity_min", 0.3))

    # 1. Pacing & Delivery Score (0-100)
    pacing_score = 65
    if 125 <= wpm <= 160:
        pacing_score += 20
        pacing_fb = f"Optimal rolling cadence at {wpm} WPM allows clear comprehension."
    elif 110 <= wpm < 125 or 160 < wpm <= 175:
        pacing_score += 5
        pacing_fb = f"Cadence at {wpm} WPM is acceptable but fluctuates near threshold."
    else:
        pacing_score -= 25
        pacing_fb = f"Speech rate ({wpm} WPM) is off-tempo, risking cognitive overload or disengagement."

    if dead_air <= 12.0:
        pacing_score += 15
        pacing_fb += f" Dead-air pauses are well-governed ({dead_air:.1f}%)."
    elif dead_air <= 20.0:
        pacing_score += 0
        pacing_fb += f" Dead-air voids ({dead_air:.1f}%) are within acceptable limits."
    else:
        pacing_score -= 20
        pacing_fb += f" Excessive dead-air gaps ({dead_air:.1f}%) interrupt conversational continuity."

    pacing_score = max(20, min(96, pacing_score))
    pacing_status = "Optimal" if pacing_score >= 80 else "Acceptable" if pacing_score >= 65 else "Needs Improvement"

    # 2. Student Engagement Score (0-100)
    engagement_score = 45
    if student_talk >= 30.0:
        engagement_score += 25
    elif student_talk >= 18.0:
        engagement_score += 12
    else:
        engagement_score -= 15

    if q_density >= 14.0:
        engagement_score += 25
    elif q_density >= 7.0:
        engagement_score += 12
    else:
        engagement_score -= 15

    engagement_score = max(20, min(96, engagement_score))
    engagement_status = "Optimal" if engagement_score >= 80 else "Acceptable" if engagement_score >= 65 else "Needs Improvement"
    engagement_fb = (
        f"Cohort participation reached {student_talk:.0f}% talk share with {q_density:.1f} questions/hr "
        f"({q_total} total interrogatives)."
    )

    # 3. Content & Visual Structure Score (0-100)
    if slide_count > 0:
        if 0.1 <= slide_vel <= 1.2:
            structure_score = 88
            structure_status = "Optimal"
            structure_fb = f"Instructional slide pacing ({slide_vel:.2f} slides/min, {slide_count} slides) supports comprehension without rushing."
        elif slide_vel > 2.0:
            structure_score = 64
            structure_status = "Acceptable"
            structure_fb = f"Rapid slide progression ({slide_vel:.2f} slides/min) may cause visual skimming."
        else:
            structure_score = 72
            structure_status = "Acceptable"
            structure_fb = f"Static slide presentation ({slide_count} slides) provides baseline visual anchor."
    else:
        structure_score = 68 if q_density >= 10 else 52
        structure_status = "Acceptable" if structure_score >= 65 else "Needs Improvement"
        structure_fb = "Discussion-based session with minimal non-face visual slide aids."

    # 4. Instructional Clarity Score (0-100)
    clarity_score = int(0.4 * pacing_score + 0.3 * engagement_score + 0.3 * structure_score)
    clarity_status = "Optimal" if clarity_score >= 80 else "Acceptable" if clarity_score >= 65 else "Needs Improvement"
    clarity_fb = f"Pedagogical articulation index scored {clarity_score}/100 across verbal pacing and cohort checks."

    dimension_scores = [
        DimensionScore(name="Instructional Clarity", score=clarity_score, benchmark_status=clarity_status, feedback=clarity_fb),
        DimensionScore(name="Student Engagement", score=engagement_score, benchmark_status=engagement_status, feedback=engagement_fb),
        DimensionScore(name="Pacing & Delivery", score=pacing_score, benchmark_status=pacing_status, feedback=pacing_fb),
        DimensionScore(name="Content & Visual Structure", score=structure_score, benchmark_status=structure_status, feedback=structure_fb),
    ]

    # Weighted composite score
    overall_score = (
        0.30 * clarity_score +
        0.30 * engagement_score +
        0.25 * pacing_score +
        0.15 * structure_score
    )

    if overall_score >= 82.0:
        overall_tier = "Excellent"
        conf = {"Poor": 0.02, "Average": 0.08, "Good": 0.18, "Excellent": 0.72}
    elif overall_score >= 68.0:
        overall_tier = "Good"
        conf = {"Poor": 0.04, "Average": 0.16, "Good": 0.68, "Excellent": 0.12}
    elif overall_score >= 50.0:
        overall_tier = "Average"
        conf = {"Poor": 0.14, "Average": 0.64, "Good": 0.18, "Excellent": 0.04}
    else:
        overall_tier = "Poor"
        conf = {"Poor": 0.74, "Average": 0.18, "Good": 0.06, "Excellent": 0.02}

    # Diagnostic executive summary
    if overall_tier in ["Excellent", "Good"]:
        executive_summary = (
            f"The instructional session achieved a strong quality rating ({overall_tier}) with an overall pedagogical "
            f"index of {overall_score:.0f}/100. Pacing was maintained at a steady {wpm} WPM with governed silence "
            f"({dead_air:.1f}% dead air). Student participation contributed {student_talk:.0f}% of total dialogue "
            f"across {q_total} inquiry checkpoints."
        )
    else:
        executive_summary = (
            f"The session exhibited pedagogical areas for growth ({overall_tier} tier, {overall_score:.0f}/100). "
            f"Instruction was characterized by teacher monologue ({teacher_talk:.0f}% talk share) and {dead_air:.1f}% unguided "
            f"dead air. Pacing ({wpm} WPM) and infrequent checks for understanding ({q_density:.1f}/hr) indicate "
            f"opportunities to integrate structured interactive dialogue."
        )

    # Observed Strengths
    strengths = []
    if 125 <= wpm <= 160:
        strengths.append(f"Deliberate, cognitive-friendly speech tempo ({wpm} WPM) within the optimal 125-160 WPM benchmark.")
    if dead_air <= 12.0:
        strengths.append(f"Fluid instructional transitions with controlled dead-air voids ({dead_air:.1f}%).")
    if student_talk >= 25.0:
        strengths.append(f"Substantial student voice share ({student_talk:.0f}%), promoting collaborative dialogue.")
    if q_density >= 12.0:
        strengths.append(f"Frequent formative checks for understanding ({q_density:.1f} questions/hr).")
    if slide_count > 0 and 0.1 <= slide_vel <= 1.2:
        strengths.append(f"Structured visual anchor pacing with {slide_count} retained non-face instructional slides.")
    if not strengths:
        strengths.append("Clear audio signal capture enabling end-to-end pedagogical telemetry extraction.")

    # Coaching Recommendations
    coaching = []
    if student_talk < 25.0:
        coaching.append("Increase student voice: Incorporate 'Think-Pair-Share' or open-ended prompts to boost student talk share beyond 30%.")
    if q_density < 10.0:
        coaching.append(f"Elevate inquiry density from current {q_density:.1f}/hr to at least 12/hr via periodic understanding checkpoints.")
    if dead_air > 18.0:
        coaching.append(f"Mitigate unguided dead air ({dead_air:.1f}%): Use intentional thinking prompts during pause voids.")
    if wpm > 165:
        coaching.append(f"Moderate delivery tempo ({wpm} WPM): Build deliberate 3-second pauses after introducing complex formulas or definitions.")
    elif wpm < 115:
        coaching.append(f"Energize delivery cadence ({wpm} WPM): Maintain momentum to sustain cohort attention during extended explanations.")
    if slide_count == 0:
        coaching.append("Introduce visual framing: Leverage digital whiteboards or key concept slides to anchor abstract verbal instruction.")
    if not coaching:
        coaching.append("Continue current pedagogical cadence and maintain interactive checks for understanding throughout class sessions.")

    return PedagogicalEvaluation(
        overall_tier=overall_tier,
        confidence_distribution=conf,
        executive_summary=executive_summary,
        dimension_scores=dimension_scores,
        observed_strengths=strengths,
        coaching_recommendations=coaching,
        inference_source="Local Rubric Engine",
    )


def evaluate_with_llm(
    telemetry: Dict[str, Any],
    transcript_snippets: List[Any],
    duration_str: str = "45:00",
) -> PedagogicalEvaluation:
    """
    Attempt evaluation via LLM API if credentials exist; otherwise fallback smoothly to local rubric.
    Supports Google Gemini, OpenAI, or Hugging Face Inference API.
    """
    api_key_gemini = os.environ.get("GEMINI_API_KEY")
    api_key_openai = os.environ.get("OPENAI_API_KEY")

    if not api_key_gemini and not api_key_openai:
        # No external API keys configured: return deterministic, zero-dependency local rubric
        return evaluate_with_local_rubric(telemetry, transcript_snippets, duration_str)

    prompt = build_pedagogical_prompt(telemetry, transcript_snippets, duration_str)

    # Try Gemini if API key is present
    if api_key_gemini:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key_gemini)
            model = genai.GenerativeModel("gemini-1.5-flash", generation_config={"response_mime_type": "application/json"})
            response = model.generate_content(prompt)
            data = json.loads(response.text)
            return _parse_json_evaluation(data, source="LLM (Gemini 1.5 Flash)")
        except Exception as e:
            logger.warning(f"Gemini API evaluation failed: {e}. Falling back to local rubric engine.")

    # Try OpenAI if API key is present
    if api_key_openai:
        try:
            import openai
            client = openai.OpenAI(api_key=api_key_openai)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            data = json.loads(response.choices[0].message.content)
            return _parse_json_evaluation(data, source="LLM (GPT-4o Mini)")
        except Exception as e:
            logger.warning(f"OpenAI API evaluation failed: {e}. Falling back to local rubric engine.")

    # Fallback to local rubric engine
    return evaluate_with_local_rubric(telemetry, transcript_snippets, duration_str)


def _parse_json_evaluation(data: Dict[str, Any], source: str) -> PedagogicalEvaluation:
    """Parse and validate JSON payload from LLM into typed PedagogicalEvaluation dataclass."""
    dim_scores = []
    for d in data.get("dimension_scores", []):
        dim_scores.append(
            DimensionScore(
                name=d.get("name", "Dimension"),
                score=int(d.get("score", 70)),
                benchmark_status=d.get("benchmark_status", "Acceptable"),
                feedback=d.get("feedback", ""),
            )
        )

    return PedagogicalEvaluation(
        overall_tier=data.get("overall_tier", "Good"),
        confidence_distribution=data.get("confidence_distribution", {"Poor": 0.05, "Average": 0.15, "Good": 0.70, "Excellent": 0.10}),
        executive_summary=data.get("executive_summary", "Classroom evaluation completed."),
        dimension_scores=dim_scores,
        observed_strengths=data.get("observed_strengths", []),
        coaching_recommendations=data.get("coaching_recommendations", []),
        inference_source=source,
    )
