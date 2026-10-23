"""
Executive Evaluation Badge & Coaching Summary Component.
"""
import streamlit as st
from src.ui.styles import render_html
from src.models.schema import EvaluationSession, QualityTier


def render_evaluation_badge(session: EvaluationSession):
    """Render the primary quality tier badge and contextual rationale."""
    tier_class_map = {
        QualityTier.EXCELLENT: ("badge-excellent", "🟢", "#10b981"),
        QualityTier.GOOD: ("badge-good", "🔵", "#3b82f6"),
        QualityTier.AVERAGE: ("badge-average", "🟡", "#f59e0b"),
        QualityTier.POOR: ("badge-poor", "🔴", "#ef4444"),
    }
    
    css_class, icon, color = tier_class_map.get(
        session.tier, ("badge-good", "🔵", "#3b82f6")
    )
    
    badge_html = f"""
    <div class="badge-container {css_class}">
        <div class="badge-tier-title">
            <span>{icon} {session.tier.value.upper()} CLASS QUALITY</span>
            <span class="badge-score-pill" style="color: {color};">
                {session.overall_score:.1f} / 100
            </span>
        </div>
        <div class="badge-headline">{session.summary_headline}</div>
        <div class="badge-rationale">{session.summary_rationale}</div>
        <div style="font-size: 0.78rem; color: #64748b; margin-top: 0.4rem;">
            Decision Confidence: <strong>{session.confidence * 100:.0f}%</strong> &bull; Duration Analyzed: <strong>{session.duration_str}</strong>
        </div>
    </div>
    """
    render_html(badge_html)
    
    # Coaching Recommendations
    with st.expander("💡 Pedagogical Coaching & Action Items", expanded=True):
        for idx, tip in enumerate(session.coaching_tips, start=1):
            st.markdown(f"**{idx}.** {tip}")
