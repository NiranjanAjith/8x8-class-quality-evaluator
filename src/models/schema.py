"""
Production Domain Data Models & Schemas.
Air-gapped, zero-mock pedagogical evaluation structures.
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


class QualityTier(str, Enum):
    POOR = "Poor"
    AVERAGE = "Average"
    GOOD = "Good"
    EXCELLENT = "Excellent"


@dataclass
class DimensionScore:
    name: str  # "Instructional Clarity", "Student Engagement", "Pacing & Delivery", "Content & Visual Structure"
    score: int  # 0 to 100
    benchmark_status: str  # "Optimal", "Acceptable", "Needs Improvement"
    feedback: str  # Concrete diagnostic note


@dataclass
class TranscriptSnippet:
    timestamp: str
    speaker: str
    text: str
    keyframe_id: str
    pedagogical_tag: str
    explanation: str


@dataclass
class RetainedSlide:
    slide_id: str
    timestamp: str
    title: str
    content_type: str  # "Presentation Deck", "Code Editor", "Digital Whiteboard"
    clutter_index: float  # 0.0 to 1.0
    base64_jpeg: str = ""


@dataclass
class PedagogicalEvaluation:
    overall_tier: str  # "Poor" | "Average" | "Good" | "Excellent"
    confidence_distribution: Dict[str, float]  # {"Poor": 0.05, "Average": 0.12, "Good": 0.70, "Excellent": 0.13}
    executive_summary: str  # Diagnostic synthesis paragraph justifying the verdict
    dimension_scores: List[DimensionScore] = field(default_factory=list)
    observed_strengths: List[str] = field(default_factory=list)
    coaching_recommendations: List[str] = field(default_factory=list)
    inference_source: str = "Local Rubric Engine"  # "LLM (Direct)" or "Local Rubric Engine"


@dataclass
class EvaluationSession:
    scenario_id: str
    scenario_name: str
    duration_str: str
    tier: QualityTier
    overall_score: float  # 0 to 100
    confidence: float
    probabilities: Dict[str, float]
    summary_headline: str
    summary_rationale: str
    coaching_tips: List[str]
    telemetry: Dict[str, Any]
    transcript_snippets: List[TranscriptSnippet] = field(default_factory=list)
    retained_slides: List[RetainedSlide] = field(default_factory=list)
    pedagogical_evaluation: Optional[PedagogicalEvaluation] = None


def create_empty_evaluation_session(
    source_name: str = "Classroom Media",
    duration_str: str = "00:00",
) -> EvaluationSession:
    """Create a pristine EvaluationSession structure with zero mock data."""
    import time
    return EvaluationSession(
        scenario_id=f"session_{int(time.time())}",
        scenario_name=source_name,
        duration_str=duration_str,
        tier=QualityTier.AVERAGE,
        overall_score=0.0,
        confidence=0.0,
        probabilities={
            QualityTier.POOR.value: 0.0,
            QualityTier.AVERAGE.value: 0.0,
            QualityTier.GOOD.value: 0.0,
            QualityTier.EXCELLENT.value: 0.0,
        },
        summary_headline="Evaluation In Progress",
        summary_rationale="Awaiting pedagogical analysis.",
        coaching_tips=[],
        telemetry={
            "teacher_talk_pct": 100.0,
            "student_talk_pct": 0.0,
            "wpm": 0,
            "dead_air_pct": 0.0,
            "question_density": 0.0,
            "slide_velocity_min": 0.0,
            "slide_count": 0,
            "total_questions": 0,
        },
        transcript_snippets=[],
        retained_slides=[],
        pedagogical_evaluation=None,
    )
