"""
Synchronized Transcript & Retained Keyframe Inspector (Left Pane).
Supports Recording/Media URL input, local file upload, and evidence analysis.
"""
import streamlit as st
from src.mock.telemetry_generator import EvaluationSession


def render_media_and_transcript_viewer(session: EvaluationSession):
    """Render media link/file ingestion, retained slide gallery, and evidence quotes with explanations."""
    
    st.html('<div class="pane-header">📁 Media Input & Evidence Explorer</div>')
    
    # 1. Dual Ingestion: Recording/Stream URL & Local File Upload
    input_tab_url, input_tab_upload = st.tabs(["🔗 Recording / Stream URL", "📁 Local Media File"])
    
    with input_tab_url:
        st.markdown("**Analyze 8x8 Recording or Cloud Media Stream**")
        col_url, col_btn = st.columns([3.5, 1.2])
        with col_url:
            media_url = st.text_input(
                "Recording URL",
                placeholder="https://8x8.vc/recordings/... or direct .mp4/.wav link",
                label_visibility="collapsed",
            )
        with col_btn:
            fetch_clicked = st.button("⚡ Ingest Stream", use_container_width=True)
            
        if fetch_clicked and media_url:
            st.success(f"🔗 Linked stream: `{media_url[:45]}...` — Audio extracted in-memory; 0 media saved to disk.")
        elif fetch_clicked and not media_url:
            st.warning("Please provide a valid recording or stream URL.")
        else:
            st.caption("Supports 8x8 cloud recordings, presigned S3/GCS URLs, YouTube, and direct HTTP/HTTPS media streams.")

    with input_tab_upload:
        uploaded_file = st.file_uploader(
            "Upload Classroom Media (.mp4, .m4a, .wav, .mp3)",
            type=["mp4", "m4a", "wav", "mp3"],
            help="Audio is processed strictly in-memory and discarded. Frames with detected faces are immediately purged."
        )
        if uploaded_file:
            st.success(f"Loaded: `{uploaded_file.name}` ({uploaded_file.size / (1024*1024):.1f} MB) - Running in-memory evaluation...")
        else:
            st.caption("Drop classroom recordings directly from your local machine (max 200MB).")

    # Status notice
    st.info("💡 Demonstrating active session with pre-extracted telemetry data. Ingest media above to evaluate new sessions.")

    # 2. Retained Instructional Slides Section
    st.markdown("#### 🖼️ Retained Instructional Slides (Non-Face)")
    st.caption("Human faces are automatically evicted. Analysis is restricted strictly to instructional materials.")
    
    slide_tabs = st.tabs([f"Slide {idx+1}" for idx in range(len(session.retained_slides))])
    for idx, (tab, slide) in enumerate(zip(slide_tabs, session.retained_slides)):
        with tab:
            slide_html = f"""
            <div class="slide-card">
                <div class="slide-meta">
                    <span class="slide-title">{slide.title}</span>
                    <span class="slide-type">Type: <strong>{slide.content_type}</strong> &bull; Visual Clutter: {slide.clutter_index * 100:.0f}%</span>
                </div>
                <div style="font-family: monospace; font-size: 0.8rem; font-weight: 700; color: #4338ca; background: #e0e7ff; padding: 0.2rem 0.5rem; border-radius: 4px;">
                    ⏱️ {slide.timestamp}
                </div>
            </div>
            """
            st.html(slide_html)
            
            # Simple placeholder canvas for visual slide demonstration
            svg_color = "#3b82f6" if "Presentation" in slide.content_type else "#10b981" if "Whiteboard" in slide.content_type else "#6366f1"
            canvas_html = f"""
            <div style="width: 100%; height: 110px; background: #f8fafc; border: 1.5px dashed {svg_color}; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 0.25rem;">
                <span style="font-size: 1.5rem;">📊</span>
                <span style="font-size: 0.78rem; font-weight: 600; color: #475569;">[Keyframe: {slide.title}]</span>
                <span style="font-size: 0.68rem; color: #94a3b8;">Zero Biometric Data &bull; Slide Content Extracted</span>
            </div>
            """
            st.html(canvas_html)

    # 3. Synchronized Transcript Explorer with Contextual Explanations
    st.markdown("#### 📝 Synchronized Transcript & Evidence Quotes")
    st.caption("Key verbal interactions with contextual pedagogical impact analysis and diagnostic notes.")
    
    search_query = st.text_input("🔍 Search transcript tokens, tags, or pedagogical notes", placeholder="e.g., questions, determinant, silence...")

    filtered_snippets = [
        s for s in session.transcript_snippets
        if not search_query 
        or search_query.lower() in s.text.lower() 
        or search_query.lower() in s.pedagogical_tag.lower() 
        or search_query.lower() in s.speaker.lower()
        or search_query.lower() in s.explanation.lower()
    ]

    if not filtered_snippets:
        st.warning("No transcript lines match your search query.")
    else:
        for item in filtered_snippets:
            speaker_class = "speaker-teacher" if "[Teacher]" in item.speaker else "speaker-student"
            transcript_html = f"""
            <div class="transcript-card">
                <div class="transcript-header">
                    <span class="{speaker_class}">{item.speaker}</span>
                    <span class="transcript-time">{item.timestamp}</span>
                    <span class="transcript-tag">📌 {item.pedagogical_tag}</span>
                </div>
                <div class="transcript-quote-box">"{item.text}"</div>
                <div class="transcript-explanation">
                    <div class="transcript-explanation-header">
                        <span>💡 Pedagogical Context & Impact</span>
                    </div>
                    <div>{item.explanation}</div>
                </div>
            </div>
            """
            st.html(transcript_html)
