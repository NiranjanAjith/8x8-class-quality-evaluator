"""
Synthetic Telemetry & Mock Evaluation Generator for Epic 1.
Provides realistic, multi-scenario classroom assessment datasets.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any


class QualityTier(str, Enum):
    POOR = "Poor"
    AVERAGE = "Average"
    GOOD = "Good"
    EXCELLENT = "Excellent"


@dataclass
class ShapDriver:
    feature: str
    impact: float  # Percentage shift or raw SHAP value
    direction: str  # "positive" or "negative"
    description: str


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
    shap_drivers: List[ShapDriver]
    transcript_snippets: List[TranscriptSnippet]
    retained_slides: List[RetainedSlide]


SCENARIOS: Dict[str, EvaluationSession] = {
    "interactive": EvaluationSession(
        scenario_id="interactive",
        scenario_name="Interactive High-Engagement Workshop",
        duration_str="42m 18s",
        tier=QualityTier.EXCELLENT,
        overall_score=91.4,
        confidence=0.89,
        probabilities={
            "Poor": 0.02,
            "Average": 0.06,
            "Good": 0.18,
            "Excellent": 0.74,
        },
        summary_headline="Exemplary Socratic interaction with well-paced visual reinforcement.",
        summary_rationale="The session demonstrated outstanding student-to-teacher talk distribution, continuous check-for-understanding questions, and consistent slide transitions that matched verbal pacing.",
        coaching_tips=[
            "Maintain current 60/40 conversational balance in future collaborative modules.",
            "Consider giving slightly more pause time after complex student responses to encourage peer-to-peer rejoinders.",
        ],
        telemetry={
            "teacher_talk_pct": 58.2,
            "student_talk_pct": 41.8,
            "wpm": 138,
            "dead_air_pct": 8.4,
            "question_density": 22.5,  # per hour
            "slide_velocity_min": 2.1,  # min per slide
            "slide_count": 19,
            "total_questions": 16,
        },
        shap_drivers=[
            ShapDriver(
                feature="Student Talk Share (41.8%)",
                impact=0.31,
                direction="positive",
                description="High student verbal contribution strongly elevated engagement score."
            ),
            ShapDriver(
                feature="Question Density (22.5/hr)",
                impact=0.24,
                direction="positive",
                description="Frequent interrogatives maintained attentive focus."
            ),
            ShapDriver(
                feature="Optimal Speech Pacing (138 WPM)",
                impact=0.15,
                direction="positive",
                description="Clear, steady cadence within the optimal 130-150 WPM comprehension window."
            ),
            ShapDriver(
                feature="Slide Transition Pace (2.1 min)",
                impact=0.11,
                direction="positive",
                description="Regular visual updates prevented cognitive stagnation."
            ),
            ShapDriver(
                feature="Mid-Lecture Dead Air Gap (38s)",
                impact=-0.06,
                direction="negative",
                description="Minor unguided silence during transition to code example."
            ),
        ],
        transcript_snippets=[
            TranscriptSnippet(
                timestamp="03:15",
                speaker="[Teacher]",
                text="Before we inspect the matrix decomposition, who can remind us what condition causes a zero determinant?",
                keyframe_id="slide_02",
                pedagogical_tag="Interrogative Prompt",
                explanation="Socratic Activation: The instructor prompts recall of prerequisite algebraic concepts before introducing new material, checking baseline understanding."
            ),
            TranscriptSnippet(
                timestamp="03:24",
                speaker="[Student_A]",
                text="When two row vectors are linearly dependent, so one is a scalar multiple of the other.",
                keyframe_id="slide_02",
                pedagogical_tag="Active Participation",
                explanation="Target Student Articulation: Student volunteered a mathematically rigorous definition without hesitation, indicating high conceptual internalization."
            ),
            TranscriptSnippet(
                timestamp="03:32",
                speaker="[Teacher]",
                text="Spot on. Now let's see how that looks visually when the span collapses.",
                keyframe_id="slide_03",
                pedagogical_tag="Affirmation & Pacing",
                explanation="Affirmation & Multimodal Transition: Teacher validates student reasoning and immediately aligns verbal discussion with a dynamic whiteboard visualization."
            ),
            TranscriptSnippet(
                timestamp="14:02",
                speaker="[Teacher]",
                text="Take a look at line 42 on the shared terminal. Why would this recursion breach stack depth?",
                keyframe_id="slide_07",
                pedagogical_tag="Code Inspection",
                explanation="Guided Problem-Solving: Focuses cohort attention on specific code lines, prompting inductive debugging rather than passively lecturing the solution."
            ),
            TranscriptSnippet(
                timestamp="14:18",
                speaker="[Student_B]",
                text="The base case never decrements n when n is negative.",
                keyframe_id="slide_07",
                pedagogical_tag="Student Discovery",
                explanation="Peer Analytical Discovery: Demonstrates active cognitive engagement and distributed vocal contribution across multiple students."
            ),
        ],
        retained_slides=[
            RetainedSlide("slide_01", "00:30", "Module 4: Linear Transformations", "Presentation Deck", 0.22),
            RetainedSlide("slide_02", "02:45", "Determinants & Geometric Collapse", "Presentation Deck", 0.35),
            RetainedSlide("slide_03", "05:10", "Matrix Rank & Vector Spans", "Digital Whiteboard", 0.41),
            RetainedSlide("slide_07", "13:50", "Recursive Stack Memory Trace", "Code Editor", 0.58),
            RetainedSlide("slide_11", "24:15", "Student Practice Challenge", "Presentation Deck", 0.28),
        ]
    ),

    "monologue": EvaluationSession(
        scenario_id="monologue",
        scenario_name="Monologue-Heavy Didactic Lecture",
        duration_str="48m 10s",
        tier=QualityTier.AVERAGE,
        overall_score=62.8,
        confidence=0.84,
        probabilities={
            "Poor": 0.12,
            "Average": 0.61,
            "Good": 0.23,
            "Excellent": 0.04,
        },
        summary_headline="Solid conceptual delivery hindered by one-way transmission and low student voice.",
        summary_rationale="The instructor delivered clear technical content, but the student verbal participation accounted for under 9% of the session. Extended continuous speaking blocks reduced opportunities for checks-for-understanding.",
        coaching_tips=[
            "Introduce mandatory 'turn-and-talk' or Socratic checks every 7-10 minutes.",
            "Moderate speaking pace: current cadence (176 WPM) approaches the upper limit for complex technical explanations.",
            "Insert interactive polls or quick verbal prompts during slide-heavy sections.",
        ],
        telemetry={
            "teacher_talk_pct": 91.5,
            "student_talk_pct": 8.5,
            "wpm": 176,
            "dead_air_pct": 14.8,
            "question_density": 5.2,  # per hour
            "slide_velocity_min": 6.8,  # min per slide
            "slide_count": 7,
            "total_questions": 4,
        },
        shap_drivers=[
            ShapDriver(
                feature="Student Talk Share (8.5%)",
                impact=-0.38,
                direction="negative",
                description="Severely restricted student verbal contributions lowered quality rating."
            ),
            ShapDriver(
                feature="Question Density (5.2/hr)",
                impact=-0.26,
                direction="negative",
                description="Infrequent inquiry left students in passive listening mode."
            ),
            ShapDriver(
                feature="High Speech Pacing (176 WPM)",
                impact=-0.16,
                direction="negative",
                description="Rapid speech delivery risks cognitive overload."
            ),
            ShapDriver(
                feature="Slide Staticness (6.8 min/slide)",
                impact=-0.12,
                direction="negative",
                description="Long visual dwell times contributed to audience disengagement."
            ),
            ShapDriver(
                feature="Controlled Dead Air (14.8%)",
                impact=0.10,
                direction="positive",
                description="Consistent lecture flow avoided awkward extended voids."
            ),
        ],
        transcript_snippets=[
            TranscriptSnippet(
                timestamp="02:10",
                speaker="[Teacher]",
                text="Today we have 40 slides to cover on database indexing and B-Tree node balancing, so please hold all questions until the end.",
                keyframe_id="slide_01",
                pedagogical_tag="Didactic Framing",
                explanation="Passive Framing Penalty: Explicitly deferring all questions inhibits spontaneous inquiry and discourages real-time comprehension monitoring."
            ),
            TranscriptSnippet(
                timestamp="18:40",
                speaker="[Teacher]",
                text="...as you can see the leaf node splitting algorithm propagates upwards to root in O(log N) operations without any disk page reallocation...",
                keyframe_id="slide_03",
                pedagogical_tag="Extended Monologue",
                explanation="Continuous Information Delivery: 16+ minutes of unbroken instructor monologue with zero verbal checks for understanding; significant risk of cognitive fatigue."
            ),
            TranscriptSnippet(
                timestamp="36:15",
                speaker="[Teacher]",
                text="Any quick questions? No? Great, moving to write-ahead logging.",
                keyframe_id="slide_05",
                pedagogical_tag="Rushed Check",
                explanation="Insufficient Wait Time: Allowed only 1.5 seconds of pause before resuming lecture, failing to give students adequate processing time to articulate questions."
            ),
        ],
        retained_slides=[
            RetainedSlide("slide_01", "00:45", "B-Tree Internals & Storage Engines", "Presentation Deck", 0.48),
            RetainedSlide("slide_03", "12:30", "Page Allocation Architecture", "Presentation Deck", 0.72),
            RetainedSlide("slide_05", "31:10", "Write-Ahead Logging Mechanics", "Presentation Deck", 0.64),
        ]
    ),

    "stalled": EvaluationSession(
        scenario_id="stalled",
        scenario_name="Hesitant & Stalled Discussion",
        duration_str="36m 40s",
        tier=QualityTier.POOR,
        overall_score=41.2,
        confidence=0.91,
        probabilities={
            "Poor": 0.72,
            "Average": 0.21,
            "Good": 0.06,
            "Excellent": 0.01,
        },
        summary_headline="High dead-air void percentage and sluggish pacing stalled instructional momentum.",
        summary_rationale="Over a third of the session was lost to unguided silence, setup pauses, and unresolved prompts. Speech pacing fell below conversational thresholds, and slides remained static for extended periods.",
        coaching_tips=[
            "Structure silence: when providing thinking time, state clear prompts and specific time allocations (e.g., 'Take 90 seconds to solve this').",
            "Prepare instructional transitions in advance to eliminate technical downtime.",
            "Establish proactive follow-up prompts to break awkward silence when questions receive no answer.",
        ],
        telemetry={
            "teacher_talk_pct": 52.0,
            "student_talk_pct": 14.2,
            "wpm": 94,
            "dead_air_pct": 33.8,
            "question_density": 4.1,
            "slide_velocity_min": 11.2,
            "slide_count": 3,
            "total_questions": 2,
        },
        shap_drivers=[
            ShapDriver(
                feature="Excessive Dead Air (33.8%)",
                impact=-0.44,
                direction="negative",
                description="Over 12 minutes of dead-air gaps severely degraded session momentum."
            ),
            ShapDriver(
                feature="Sluggish Speech Pacing (94 WPM)",
                impact=-0.28,
                direction="negative",
                description="Delivery lacked energy and verbal continuity."
            ),
            ShapDriver(
                feature="Slide Staticness (11.2 min/slide)",
                impact=-0.21,
                direction="negative",
                description="Long visual freezes without dynamic changes."
            ),
            ShapDriver(
                feature="Low Total Speech Share (66.2%)",
                impact=-0.14,
                direction="negative",
                description="Significant session portion devoid of any instructional speech."
            ),
        ],
        transcript_snippets=[
            TranscriptSnippet(
                timestamp="04:20",
                speaker="[Teacher]",
                text="Hold on, let me figure out how to switch the screen share... can everyone see this? Wait, that's the wrong tab...",
                keyframe_id="slide_01",
                pedagogical_tag="Technical Disruption",
                explanation="Instructional Stagnation: Screen-share confusion caused a 2-minute technical void, eroding early session momentum."
            ),
            TranscriptSnippet(
                timestamp="11:45",
                speaker="[Teacher]",
                text="So... does anyone have any thoughts? Anyone?",
                keyframe_id="slide_02",
                pedagogical_tag="Unguided Silence",
                explanation="Unscaffolded Prompt: Broad, open-ended question without clear guardrails produced an awkward 45-second silence."
            ),
            TranscriptSnippet(
                timestamp="12:35",
                speaker="[Teacher]",
                text="...still nothing? Okay, let me just move forward then.",
                keyframe_id="slide_02",
                pedagogical_tag="Abandoned Inquiry",
                explanation="Missed Scaffolding Opportunity: Rather than rephrasing or offering a hint to re-engage students, the teacher abandoned the inquiry entirely."
            ),
        ],
        retained_slides=[
            RetainedSlide("slide_01", "01:10", "Discussion Prompts", "Presentation Deck", 0.15),
            RetainedSlide("slide_02", "11:20", "Case Study Question", "Presentation Deck", 0.18),
        ]
    ),
}


def get_scenario(scenario_key: str = "interactive") -> EvaluationSession:
    """Retrieve an evaluation session by scenario key, default to interactive."""
    return SCENARIOS.get(scenario_key, SCENARIOS["interactive"])


def list_available_scenarios() -> Dict[str, str]:
    """Return dictionary of scenario IDs to display titles."""
    return {k: v.scenario_name for k, v in SCENARIOS.items()}
