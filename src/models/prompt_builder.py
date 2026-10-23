"""
Pedagogical Rubric Prompt Builder for LLM Classroom Judgement.
"""
from typing import Dict, List, Any


def build_pedagogical_prompt(
    telemetry: Dict[str, Any],
    transcript_snippets: List[Any],
    duration_str: str = "45:00",
) -> str:
    """Construct structured evaluation prompt for LLM pedagogical judgement."""
    dead_air = telemetry.get("dead_air_pct", 0.0)
    wpm = telemetry.get("wpm", 0)
    q_density = telemetry.get("question_density", 0.0)
    q_total = telemetry.get("total_questions", 0)
    teacher_talk = telemetry.get("teacher_talk_pct", 80.0)
    student_talk = telemetry.get("student_talk_pct", 20.0)
    slide_count = telemetry.get("slide_count", 0)
    slide_vel = telemetry.get("slide_velocity_min", 0.0)

    # Format transcript excerpts
    transcript_lines = []
    for s in transcript_snippets[:12]:
        speaker = getattr(s, "speaker", "[Speaker]")
        time_tag = getattr(s, "timestamp", "")
        text = getattr(s, "text", "")
        tag = getattr(s, "pedagogical_tag", "")
        transcript_lines.append(f"[{time_tag}] {speaker} ({tag}): \"{text}\"")
    
    transcript_block = "\n".join(transcript_lines) if transcript_lines else "(No transcript lines available)"

    prompt = f"""You are an elite instructional coach and pedagogical evaluator.
Evaluate the instructional quality of this classroom recording based on objective telemetry and sanitized dialogue.

=== MEASURED CLASSROOM TELEMETRY ===
- Session Duration: {duration_str}
- Dead-Air / Silence Percentage: {dead_air:.1f}% (Benchmark: <12% fluid, >20% excessive pause voids)
- Speech Pacing: {wpm} WPM (Benchmark: 125-160 WPM optimal, <110 sluggish, >170 hurried)
- Inquiry & Question Density: {q_density:.1f}/hr ({q_total} total questions) (Benchmark: >=15/hr high, <8/hr low)
- Talk-to-Listen Ratio: {teacher_talk:.0f}% Teacher / {student_talk:.0f}% Student (Benchmark: 30-50% student voice)
- Visual Slides Detected: {slide_count} slides ({slide_vel:.2f} slides/min)

=== SCRUBBED TRANSCRIPT EXCERPTS (PII-REDACTED) ===
{transcript_block}

=== PEDAGOGICAL ASSESSMENT RUBRIC ===
- Excellent: Highly engaging inquiry, optimal pacing, interactive checks for understanding, balanced visual support.
- Good: Solid delivery, clear explanations, moderate student interaction, controlled silence/pacing.
- Average: Instructor monologue, infrequent checks for understanding, marginal pacing or dead-air gaps.
- Poor: Disorganized flow, excessive dead air (>25%) or hurried cadence (>175 WPM), passive cohort (<10% student participation).

Respond ONLY with valid JSON conforming to this exact structure:
{{
  "overall_tier": "Poor" | "Average" | "Good" | "Excellent",
  "confidence_distribution": {{
    "Poor": float,
    "Average": float,
    "Good": float,
    "Excellent": float
  }},
  "executive_summary": "Diagnostic synthesis explaining why this tier was assigned.",
  "dimension_scores": [
    {{
      "name": "Instructional Clarity",
      "score": int (0-100),
      "benchmark_status": "Optimal" | "Acceptable" | "Needs Improvement",
      "feedback": "Specific diagnostic observation."
    }},
    {{
      "name": "Student Engagement",
      "score": int (0-100),
      "benchmark_status": "Optimal" | "Acceptable" | "Needs Improvement",
      "feedback": "Specific diagnostic observation."
    }},
    {{
      "name": "Pacing & Delivery",
      "score": int (0-100),
      "benchmark_status": "Optimal" | "Acceptable" | "Needs Improvement",
      "feedback": "Specific diagnostic observation."
    }},
    {{
      "name": "Content & Visual Structure",
      "score": int (0-100),
      "benchmark_status": "Optimal" | "Acceptable" | "Needs Improvement",
      "feedback": "Specific diagnostic observation."
    }}
  ],
  "observed_strengths": [
    "High-leverage pedagogical practice 1 with evidence",
    "High-leverage pedagogical practice 2 with evidence"
  ],
  "coaching_recommendations": [
    "Actionable coaching recommendation 1",
    "Actionable coaching recommendation 2"
  ]
}}
"""
    return prompt
