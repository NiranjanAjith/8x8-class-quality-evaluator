"""
Synchronized Transcript & Retained Keyframe Inspector (Left Pane).
Supports Recording/Media URL input, local file upload, FFmpeg extraction,
face-filtered visual analysis (Epic 3), and session-state persistence.
"""
import time
import streamlit as st
from src.mock.telemetry_generator import EvaluationSession, RetainedSlide
from src.ingestion.media_loader import load_media_from_file, load_media_from_url
from src.ingestion.audio_extractor import extract_audio_pcm_16k
from src.ingestion.models import IngestedMedia
from src.vision.pipeline import run_visual_telemetry_pipeline


def render_active_ingested_card(ingested: IngestedMedia):
    """Render the active ingested media card stored in session state."""
    type_badge = "🔗 Cloud Stream" if ingested.source_type == "url" else "📁 Local File"
    
    st.markdown(f"""
    <div style="background: #f0fdf4; border: 1.5px solid #86efac; border-radius: 10px; padding: 0.85rem 1.1rem; margin-bottom: 1.0rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
            <span style="font-weight: 700; font-size: 0.95rem; color: #166534;">{type_badge}: <code>{ingested.source_name}</code></span>
            <span style="font-size: 0.8rem; background: #dcfce7; color: #15803d; padding: 0.15rem 0.5rem; border-radius: 12px; font-weight: 700;">
                ⏱️ {ingested.duration_str}
            </span>
        </div>
        <div style="font-size: 0.78rem; color: #374151; line-height: 1.45;">
            Size: <strong>{ingested.size_mb:.1f} MB</strong> &bull; Audio: <strong>{ingested.sample_rate} Hz Mono (16-bit PCM)</strong> &bull; Slides: <strong>{ingested.slide_count}</strong> &bull; Faces Evicted: <strong>{ingested.face_frames_dropped}</strong>
        </div>
        <div style="font-size: 0.72rem; color: #15803d; margin-top: 0.35rem; font-weight: 600;">
            🛡️ Raw Video Evicted from RAM &bull; Audio Buffered for Whisper & VAD (Epic 4)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if ingested.wav_bytes:
        st.caption("🎧 Normalized Ephemeral Audio Preview:")
        st.audio(ingested.wav_bytes, format="audio/wav")

    col_btn, _ = st.columns([1.5, 3])
    with col_btn:
        if st.button("🔄 Ingest New Media", use_container_width=True):
            st.session_state.ingested_media = None
            st.rerun()


def render_media_and_transcript_viewer(session: EvaluationSession):
    """Render media link/file ingestion, retained slide gallery, and evidence quotes with explanations."""
    
    st.html('<div class="pane-header">📁 Media Input & Evidence Explorer</div>')
    
    active_media: IngestedMedia = st.session_state.get("ingested_media")
    
    if active_media is not None:
        render_active_ingested_card(active_media)
    else:
        # Ingestion Tabs: Recording/Stream URL & Local File Upload
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
                with st.spinner("Connecting to media stream in-memory..."):
                    load_res = load_media_from_url(media_url)
                if not load_res.success:
                    st.error(load_res.error_message)
                else:
                    with st.spinner("Extracting & normalizing audio (16 kHz Mono)..."):
                        audio_res = extract_audio_pcm_16k(load_res.data)
                    with st.spinner("Analyzing slides & dropping face frames (Epic 3)..."):
                        visual_res = run_visual_telemetry_pipeline(load_res.data, sample_interval_sec=5.0)

                    if not audio_res.success:
                        st.error(audio_res.error_message)
                    else:
                        ingested = IngestedMedia(
                            source_name=load_res.source_name,
                            source_type=load_res.source_type,
                            size_mb=load_res.size_mb,
                            raw_media_bytes=None,  # Purged immediately to uphold zero biometric & zero memory bloat
                            wav_bytes=audio_res.wav_bytes,  # Retained for Epic 4 (Whisper/VAD)
                            duration_sec=audio_res.duration_sec,
                            duration_str=audio_res.duration_str,
                            sample_rate=audio_res.sample_rate,
                            channels=audio_res.channels,
                            is_audio_evicted=False,
                            is_video_evicted=True,
                            slide_count=visual_res.slide_count,
                            face_frames_dropped=visual_res.face_frames_dropped,
                            ingested_at=time.time(),
                        )
                        st.session_state.ingested_media = ingested

                        if "session_data" in st.session_state:
                            st.session_state.session_data.duration_str = audio_res.duration_str
                            if visual_res.slide_count > 0:
                                st.session_state.session_data.telemetry["slide_count"] = visual_res.slide_count
                                st.session_state.session_data.telemetry["slide_velocity_min"] = visual_res.slide_velocity_min
                                st.session_state.session_data.retained_slides = [
                                    RetainedSlide(
                                        slide_id=s.slide_id,
                                        timestamp=s.timestamp,
                                        title=s.title,
                                        content_type=s.content_type,
                                        clutter_index=s.clutter_index,
                                        base64_jpeg=s.base64_jpeg,
                                    )
                                    for s in visual_res.slides
                                ]
                        st.rerun()

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
                with st.spinner("Reading uploaded media into memory..."):
                    load_res = load_media_from_file(uploaded_file)
                if not load_res.success:
                    st.error(load_res.error_message)
                else:
                    with st.spinner("Extracting & normalizing audio (16 kHz Mono)..."):
                        audio_res = extract_audio_pcm_16k(load_res.data)
                    with st.spinner("Analyzing slides & dropping face frames (Epic 3)..."):
                        visual_res = run_visual_telemetry_pipeline(load_res.data, sample_interval_sec=5.0)

                    if not audio_res.success:
                        st.error(audio_res.error_message)
                    else:
                        ingested = IngestedMedia(
                            source_name=load_res.source_name,
                            source_type=load_res.source_type,
                            size_mb=load_res.size_mb,
                            raw_media_bytes=None,  # Purged immediately to uphold zero biometric & zero memory bloat
                            wav_bytes=audio_res.wav_bytes,  # Retained for Epic 4 (Whisper/VAD)
                            duration_sec=audio_res.duration_sec,
                            duration_str=audio_res.duration_str,
                            sample_rate=audio_res.sample_rate,
                            channels=audio_res.channels,
                            is_audio_evicted=False,
                            is_video_evicted=True,
                            slide_count=visual_res.slide_count,
                            face_frames_dropped=visual_res.face_frames_dropped,
                            ingested_at=time.time(),
                        )
                        st.session_state.ingested_media = ingested

                        if "session_data" in st.session_state:
                            st.session_state.session_data.duration_str = audio_res.duration_str
                            if visual_res.slide_count > 0:
                                st.session_state.session_data.telemetry["slide_count"] = visual_res.slide_count
                                st.session_state.session_data.telemetry["slide_velocity_min"] = visual_res.slide_velocity_min
                                st.session_state.session_data.retained_slides = [
                                    RetainedSlide(
                                        slide_id=s.slide_id,
                                        timestamp=s.timestamp,
                                        title=s.title,
                                        content_type=s.content_type,
                                        clutter_index=s.clutter_index,
                                        base64_jpeg=s.base64_jpeg,
                                    )
                                    for s in visual_res.slides
                                ]
                        st.rerun()
            else:
                st.caption("Drop classroom recordings directly from your local machine (max 200MB).")

        # Demonstration notice when no custom media is currently active
        st.info("💡 Demonstrating active session with pre-extracted telemetry data. Ingest media above to evaluate new sessions.")

    # 2. Retained Instructional Slides Section
    st.markdown("#### 🖼️ Retained Instructional Slides (Non-Face)")
    st.caption("Human faces are automatically evicted. Analysis is restricted strictly to instructional materials.")
    
    slides = session.retained_slides
    if not slides:
        st.caption("No visual instructional slides detected in current media.")
    else:
        slide_tabs = st.tabs([f"Slide {idx+1}" for idx in range(len(slides))])
        for idx, (tab, slide) in enumerate(zip(slide_tabs, slides)):
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
                
                # If real extracted base64 image exists, render it; otherwise render placeholder
                if getattr(slide, "base64_jpeg", None):
                    st.markdown(
                        f'<img src="{slide.base64_jpeg}" style="width: 100%; max-height: 260px; object-fit: contain; border-radius: 6px; border: 1px solid #cbd5e1; margin-top: 0.25rem; background: #000;" />',
                        unsafe_allow_html=True
                    )
                else:
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
