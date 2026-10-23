"""
Data models for LLM Pedagogical Judgement & Explanations.
"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DimensionScore:
    name: str  # "Instructional Clarity", "Student Engagement", "Pacing & Delivery", "Content & Visual Structure"
    score: int  # 0 to 100
    benchmark_status: str  # "Optimal", "Acceptable", "Needs Improvement"
    feedback: str  # Concrete diagnostic note


@dataclass
class PedagogicalEvaluation:
    overall_tier: str  # "Poor" | "Average" | "Good" | "Excellent"
    confidence_distribution: Dict[str, float]  # {"Poor": 0.05, "Average": 0.12, "Good": 0.70, "Excellent": 0.13}
    executive_summary: str  # Diagnostic synthesis paragraph justifying the verdict
    dimension_scores: List[DimensionScore] = field(default_factory=list)
    observed_strengths: List[str] = field(default_factory=list)
    coaching_recommendations: List[str] = field(default_factory=list)
    inference_source: str = "Local Rubric Engine"  # "LLM (Direct)" or "Local Rubric Engine"
