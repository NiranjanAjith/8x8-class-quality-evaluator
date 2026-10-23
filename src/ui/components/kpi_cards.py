"""
Classroom Telemetry KPI Cards Component.
"""
import streamlit as st
from typing import Dict, Any


def render_kpi_cards(telemetry: Dict[str, Any]):
    """Render the primary classroom telemetry KPI grid."""
    
    # 1. Student Talk Share
    student_talk = telemetry.get("student_talk_pct", 0)
    if student_talk >= 30:
        talk_bench_class = "kpi-bench-good"
        talk_bench_text = "Balanced (30-50%)"
    elif student_talk >= 15:
        talk_bench_class = "kpi-bench-warning"
        talk_bench_text = "Moderate (15-30%)"
    else:
        talk_bench_class = "kpi-bench-alert"
        talk_bench_text = "Low (<15%)"

    # 2. WPM
    wpm = telemetry.get("wpm", 0)
    if 125 <= wpm <= 160:
        wpm_bench_class = "kpi-bench-good"
        wpm_bench_text = "Optimal (125-160)"
    elif 100 <= wpm < 125 or 160 < wpm <= 180:
        wpm_bench_class = "kpi-bench-warning"
        wpm_bench_text = "Marginal"
    else:
        wpm_bench_class = "kpi-bench-alert"
        wpm_bench_text = "Off-Target"

    # 3. Dead Air
    dead_air = telemetry.get("dead_air_pct", 0)
    if dead_air <= 12:
        air_bench_class = "kpi-bench-good"
        air_bench_text = "Fluid (<12%)"
    elif dead_air <= 20:
        air_bench_class = "kpi-bench-warning"
        air_bench_text = "Acceptable (12-20%)"
    else:
        air_bench_class = "kpi-bench-alert"
        air_bench_text = "Elevated (>20%)"

    # 4. Question Density
    q_density = telemetry.get("question_density", 0)
    if q_density >= 15:
        q_bench_class = "kpi-bench-good"
        q_bench_text = "High (≥15/hr)"
    elif q_density >= 8:
        q_bench_class = "kpi-bench-warning"
        q_bench_text = "Moderate (8-15/hr)"
    else:
        q_bench_class = "kpi-bench-alert"
        q_bench_text = "Infrequent (<8/hr)"

    # 5. Slide Velocity & Count
    slide_vel = telemetry.get("slide_velocity_min", 0)
    slide_count = telemetry.get("slide_count", 0)

    html = f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Talk-to-Listen Ratio</div>
            <div class="kpi-value-row">
                <span class="kpi-value">{telemetry.get('teacher_talk_pct', 0):.0f}% / {student_talk:.0f}%</span>
                <span class="kpi-benchmark {talk_bench_class}">{talk_bench_text}</span>
            </div>
            <div style="font-size: 0.72rem; color: #64748b; margin-top: 0.2rem;">Teacher vs. Student Voice</div>
        </div>

        <div class="kpi-card">
            <div class="kpi-label">Speech Pacing</div>
            <div class="kpi-value-row">
                <span class="kpi-value">{wpm} <span style="font-size: 0.85rem; font-weight: normal; color: #64748b;">WPM</span></span>
                <span class="kpi-benchmark {wpm_bench_class}">{wpm_bench_text}</span>
            </div>
            <div style="font-size: 0.72rem; color: #64748b; margin-top: 0.2rem;">Words per Minute (Rolling)</div>
        </div>

        <div class="kpi-card">
            <div class="kpi-label">Dead Air / Silence Gaps</div>
            <div class="kpi-value-row">
                <span class="kpi-value">{dead_air:.1f}%</span>
                <span class="kpi-benchmark {air_bench_class}">{air_bench_text}</span>
            </div>
            <div style="font-size: 0.72rem; color: #64748b; margin-top: 0.2rem;">VAD-detected unguided pauses</div>
        </div>

        <div class="kpi-card">
            <div class="kpi-label">Inquiry & Question Density</div>
            <div class="kpi-value-row">
                <span class="kpi-value">{q_density:.1f} <span style="font-size: 0.85rem; font-weight: normal; color: #64748b;">/hr</span></span>
                <span class="kpi-benchmark {q_bench_class}">{q_bench_text}</span>
            </div>
            <div style="font-size: 0.72rem; color: #64748b; margin-top: 0.2rem;">{telemetry.get('total_questions', 0)} total interrogatives detected</div>
        </div>
    </div>

    <div style="display: flex; gap: 0.75rem; margin-bottom: 1.25rem;">
        <div style="flex: 1; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.6rem 0.85rem; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.78rem; font-weight: 600; color: #475569;">🖼️ Content Slides Retained:</span>
            <span style="font-size: 0.88rem; font-weight: 800; color: #0f172a;">{slide_count} slides</span>
        </div>
        <div style="flex: 1; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.6rem 0.85rem; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.78rem; font-weight: 600; color: #475569;">⏱️ Slide Transition Velocity:</span>
            <span style="font-size: 0.88rem; font-weight: 800; color: #0f172a;">{slide_vel:.1f} min / slide</span>
        </div>
        <div style="flex: 1; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 0.6rem 0.85rem; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.78rem; font-weight: 600; color: #166534;">🛡️ Biometric Privacy:</span>
            <span style="font-size: 0.78rem; font-weight: 700; color: #15803d;">Face frames evicted (0 stored)</span>
        </div>
    </div>
    """
    st.html(html)
