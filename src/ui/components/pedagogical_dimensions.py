"""
Pedagogical Dimensions & LLM Explanations Component.
Renders sub-score dimension breakdowns, key strengths, and actionable coaching action plan.
"""
import streamlit as st
from typing import List, Optional
from src.models.schema import DimensionScore, PedagogicalEvaluation


def render_pedagogical_dimensions(eval_res: Optional[PedagogicalEvaluation]):
    """Render dimension sub-scores, diagnostic feedback, and coaching plan."""
    if eval_res is None or not eval_res.dimension_scores:
        # Fallback to standard dimension breakdown if eval_res is not yet set
        st.info("Pedagogical dimensions will display upon completing session evaluation.")
        return

    st.markdown("#### 🎯 Pedagogical Dimension Breakdown")

    # Render dimension sub-score cards
    dim_cards_html = ['<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; margin-bottom: 1.25rem;">']
    
    for dim in eval_res.dimension_scores:
        if dim.score >= 80:
            color = "#10b981"
            badge_bg = "#dcfce7"
            badge_color = "#15803d"
        elif dim.score >= 65:
            color = "#3b82f6"
            badge_bg = "#dbeafe"
            badge_color = "#1d4ed8"
        else:
            color = "#ef4444"
            badge_bg = "#fee2e2"
            badge_color = "#b91c1c"

        card = f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.85rem 1.0rem; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                    <span style="font-size: 0.82rem; font-weight: 700; color: #1e293b;">{dim.name}</span>
                    <span style="font-size: 0.72rem; font-weight: 700; background: {badge_bg}; color: {badge_color}; padding: 0.12rem 0.45rem; border-radius: 6px;">
                        {dim.benchmark_status}
                    </span>
                </div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #0f172a; margin-bottom: 0.35rem;">
                    {dim.score} <span style="font-size: 0.75rem; font-weight: normal; color: #64748b;">/ 100</span>
                </div>
                <!-- Progress meter -->
                <div style="width: 100%; height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden; margin-bottom: 0.5rem;">
                    <div style="width: {dim.score}%; height: 100%; background: {color}; border-radius: 3px;"></div>
                </div>
            </div>
            <div style="font-size: 0.74rem; color: #475569; line-height: 1.35;">
                {dim.feedback}
            </div>
        </div>
        """
        dim_cards_html.append(card)
        
    dim_cards_html.append('</div>')
    st.markdown("".join(dim_cards_html), unsafe_allow_html=True)

    # Observed Strengths Section
    if eval_res.observed_strengths:
        st.markdown("#### 🌟 Observed Pedagogical Strengths")
        strengths_html = ['<div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 0.85rem 1.1rem; margin-bottom: 1.25rem;">']
        for item in eval_res.observed_strengths:
            strengths_html.append(f"""
            <div style="display: flex; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.45rem; font-size: 0.82rem; color: #166534; line-height: 1.4;">
                <span>✅</span>
                <span>{item}</span>
            </div>
            """)
        strengths_html.append('</div>')
        st.markdown("".join(strengths_html), unsafe_allow_html=True)

    # Actionable Coaching Plan
    if eval_res.coaching_recommendations:
        st.markdown("#### 📋 Targeted Instructional Action Plan")
        coaching_html = ['<div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px; padding: 0.85rem 1.1rem; margin-bottom: 1.25rem;">']
        for idx, rec in enumerate(eval_res.coaching_recommendations, start=1):
            coaching_html.append(f"""
            <div style="display: flex; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.5rem; font-size: 0.82rem; color: #1e40af; line-height: 1.4;">
                <span style="font-weight: 800; background: #dbeafe; padding: 0.1rem 0.4rem; border-radius: 4px; font-size: 0.75rem;">{idx}</span>
                <span>{rec}</span>
            </div>
            """)
        coaching_html.append('</div>')
        st.markdown("".join(coaching_html), unsafe_allow_html=True)
