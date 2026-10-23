"""
UI Styling & Custom CSS for the 8x8 Class Quality Evaluator.
"""

CUSTOM_CSS = """
<style>
/* Hide Sidebar Completely */
[data-testid="stSidebar"], [data-testid="collapsedControl"] {
    display: none !important;
}

/* Fix Streamlit Top Bar Overlap */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 3.0rem !important;
}

/* Main Container Spacing - Clear Top Bar Comfortably */
.block-container {
    padding-top: 4.25rem !important;
    padding-bottom: 2.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 98% !important;
}

/* Header & Subtitle Styling */
.main-title {
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.sub-title {
    color: #64748b;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}

/* Pane Header */
.pane-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 0.5rem;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Grade Tier Badge Container */
.badge-container {
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
}

.badge-excellent {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(5, 150, 105, 0.05) 100%);
    border: 1.5px solid #10b981;
}

.badge-good {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(37, 99, 235, 0.05) 100%);
    border: 1.5px solid #3b82f6;
}

.badge-average {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.12) 0%, rgba(217, 119, 6, 0.05) 100%);
    border: 1.5px solid #f59e0b;
}

.badge-poor {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.12) 0%, rgba(220, 38, 38, 0.05) 100%);
    border: 1.5px solid #ef4444;
}

.badge-tier-title {
    font-size: 1.7rem;
    font-weight: 800;
    letter-spacing: -0.01em;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.badge-score-pill {
    font-size: 1.05rem;
    font-weight: 700;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.9);
}

.badge-headline {
    font-size: 1.0rem;
    font-weight: 600;
    color: #1e293b;
    margin-top: 0.2rem;
}

.badge-rationale {
    font-size: 0.88rem;
    color: #475569;
    line-height: 1.45;
}

/* Metric KPI Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}

.kpi-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.85rem 1.0rem;
    display: flex;
    flex-direction: column;
}

.kpi-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748b;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.kpi-value-row {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
}

.kpi-value {
    font-size: 1.45rem;
    font-weight: 800;
    color: #0f172a;
}

.kpi-benchmark {
    font-size: 0.75rem;
    padding: 0.15rem 0.5rem;
    border-radius: 6px;
    font-weight: 600;
}

.kpi-bench-good {
    background: #dcfce7;
    color: #15803d;
}

.kpi-bench-warning {
    background: #fef3c7;
    color: #b45309;
}

.kpi-bench-alert {
    background: #fee2e2;
    color: #b91c1c;
}

/* Section Card Container */
.section-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

/* Transcript Evidence Card with Explanation Spacing */
.transcript-card {
    border: 1px solid #e2e8f0;
    border-left: 4px solid #6366f1;
    padding: 1.0rem 1.15rem;
    margin-bottom: 1.25rem;
    background: #ffffff;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.transcript-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.45rem;
}

.speaker-teacher {
    background: #e0e7ff;
    color: #4338ca;
    font-size: 0.74rem;
    font-weight: 700;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
}

.speaker-student {
    background: #ccfbf1;
    color: #0f766e;
    font-size: 0.74rem;
    font-weight: 700;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
}

.transcript-time {
    font-size: 0.75rem;
    color: #64748b;
    font-family: monospace;
    font-weight: 600;
}

.transcript-tag {
    font-size: 0.74rem;
    font-weight: 700;
    color: #475569;
    margin-left: auto;
    background: #f1f5f9;
    padding: 0.12rem 0.45rem;
    border-radius: 4px;
}

.transcript-quote-box {
    margin-top: 0.4rem;
    margin-bottom: 0.75rem;
    padding: 0.5rem 0.85rem;
    background: #fafafa;
    border-left: 3px solid #cbd5e1;
    border-radius: 0 6px 6px 0;
    font-size: 0.88rem;
    color: #1e293b;
    font-style: italic;
    line-height: 1.45;
}

.transcript-explanation {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 3px solid #3b82f6;
    border-radius: 6px;
    padding: 0.65rem 0.85rem;
    font-size: 0.82rem;
    color: #334155;
    line-height: 1.45;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.transcript-explanation-header {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    font-weight: 700;
    font-size: 0.76rem;
    color: #2563eb;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

/* Slide Card */
.slide-card {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.65rem 0.85rem;
    background: #ffffff;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.slide-meta {
    display: flex;
    flex-direction: column;
}

.slide-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #1e293b;
}

.slide-type {
    font-size: 0.72rem;
    color: #64748b;
}
</style>
"""


def clean_html(raw_html: str) -> str:
    """Clean HTML string to ensure safe, flawless rendering in st.markdown without code block leakage."""
    return " ".join(line.strip() for line in raw_html.splitlines() if line.strip())


def render_html(raw_html: str):
    """Render HTML safely via st.markdown without Markdown indentation artifacts."""
    import streamlit as st
    st.markdown(clean_html(raw_html), unsafe_allow_html=True)
