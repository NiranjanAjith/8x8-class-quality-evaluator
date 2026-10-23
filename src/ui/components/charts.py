"""
Plotly Visualizations for Pedagogical Confidence Probabilities.
"""
from typing import Dict
import plotly.graph_objects as go
import streamlit as st


def render_probability_chart(probabilities: Dict[str, float], predicted_tier: str):
    """Render horizontal bar chart for quality tier confidence probabilities."""
    tiers = ["Poor", "Average", "Good", "Excellent"]
    probs = [probabilities.get(t, 0.0) * 100 for t in tiers]
    
    tier_colors = {
        "Poor": "#ef4444",
        "Average": "#f59e0b",
        "Good": "#3b82f6",
        "Excellent": "#10b981",
    }
    
    colors = [
        tier_colors.get(t, "#94a3b8") if t == predicted_tier else "rgba(148, 163, 184, 0.4)"
        for t in tiers
    ]
    
    fig = go.Figure(
        go.Bar(
            x=probs,
            y=tiers,
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(
                    color=[tier_colors.get(t, "#94a3b8") for t in tiers],
                    width=1.5
                )
            ),
            text=[f"{p:.1f}%" for p in probs],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>Confidence: %{x:.1f}%<extra></extra>",
        )
    )
    
    fig.update_layout(
        title=dict(
            text="<b>Classification Probability Distribution</b>",
            font=dict(size=14, color="#0f172a"),
            x=0.0,
        ),
        margin=dict(l=10, r=40, t=35, b=25),
        height=190,
        xaxis=dict(
            title="",
            range=[0, 105],
            showgrid=True,
            gridcolor="#f1f5f9",
            zeroline=False,
            ticksuffix="%",
        ),
        yaxis=dict(
            title="",
            autorange="reversed",
            tickfont=dict(size=12, color="#1e293b"),
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
