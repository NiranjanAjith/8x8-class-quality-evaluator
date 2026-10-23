"""
Synchronized Transcript & Retained Keyframe Inspector (Left Pane).
Supports Recording/Media URL input, local file upload, FFmpeg extraction,
face-filtered visual analysis (Epic 3), speech transcription & VAD (Epic 4),
Option A PII sanitization, and session-state persistence.
"""
import time
import streamlit as st
from src.mock.telemetry_generator import EvaluationSession, RetainedSlide, TranscriptSnippet
from src.ingestion.media_loader import load_media_from_file, load_media_from_url
from src.ingestion.audio_extractor import extract_audio_pcm_16k
from src.ingestion.models import IngestedMedia
from src.vision.pipeline import run_visual_telemetry_pipeline
from src.audio.pipeline import run_audio_telemetry_pipeline


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
            Size: <strong>{ingested.size_mb:.1f} MB</strong> &bull; Slides: <strong>{ingested.slide_count}</strong> &bull; Faces Evicted: <strong>{ingested.face_frames_dropped}</strong> &bull; Pacing: <strong>{ingested.wpm} WPM</strong> &bull; Dead Air: <strong>{ingested.dead_air_pct:.1f}%</strong> &bull; Questions: <strong>{ingested.question_density:.1f}/hr</strong> ({ingested.total_questions})
        </div>
        <div style="font-size: 0.74rem; color: #15803d; margin-top: 0.4rem; font-weight: 600; display: flex; gap: 1rem; flex-wrap: wrap;">
            <span>🛡️ Video RAM: <strong>Purged</strong></span>
            <span>🛡️ Audio RAM: <strong>{('Purged (Zero Retention)' if ingested.is_audio_evicted else 'Buffered')}</strong></span>
            <span>🔒 PII Sanitizer: <strong>{ingested.pii_redaction_mode}</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if ingested.wav_bytes and not ingested.is_audio_evicted:
        st.caption("🎧 Ephemeral Audio Preview (Pre-Eviction):")
        st.audio(ingested.wav_bytes, format="audio/wav")

    col_btn, _ = st.columns([1.5, 3])
    with col_btn:
        if st.button("🔄 Ingest New Media", use_container_width=True):
            st.session_state.ingested_media = None
            st.rerun()


def _process_and_store_ingested_media(raw_bytes: bytes, source_name: str, source_type: str, size_mb: float) -> bool:
    """Run full visual and audio extraction, transcribe, scrub PII, and evict raw buffers from RAM."""
    with st.spinner("Extracting & normalizing audio (16 kHz Mono)..."):
        audio_res = extract_audio_pcm_16k(raw_bytes)
    if not audio_res.success:
        st.error(audio_res.error_message)
        return False

    with st.spinner("Analyzing slides & dropping face frames (Epic 3)..."):
        visual_res = run_visual_telemetry_pipeline(raw_bytes, sample_interval_sec=5.0)

    with st.spinner("Transcribing speech, redacting PII, & calculating pacing/VAD (Epic 4)..."):
        audio_telemetry = run_audio_telemetry_pipeline(audio_res.wav_bytes)

    # Initialize ingested media model with audio evicted immediately
    ingested = IngestedMedia(
        source_name=source_name,
        source_type=source_type,
        size_mb=size_mb,
        raw_media_bytes=None,  # Purged immediately to uphold zero biometric retention
        wav_bytes=None,        # Purged immediately after transcription & VAD to enforce zero audio retention
        duration_sec=audio_res.duration_sec,
        duration_str=audio_res.duration_str,
        sample_rate=audio_res.sample_rate,
        channels=audio_res.channels,
        is_audio_evicted=True,
        is_video_evicted=True,
        slide_count=visual_res.slide_count,
        face_frames_dropped=visual_res.face_frames_dropped,
        dead_air_pct=audio_telemetry.dead_air_pct if audio_telemetry.success else 0.0,
        wpm=audio_telemetry.wpm if audio_telemetry.success else 0,
        question_density=audio_telemetry.question_density if audio_telemetry.success else 0.0,
        total_questions=audio_telemetry.total_questions if audio_telemetry.success else 0,
        transcript_segments_count=len(audio_telemetry.segments) if audio_telemetry.success else 0,
        pii_redaction_mode="Option A (Regex Sanitizer)",
        ingested_at=time.time(),
    )
    st.session_state.ingested_media = ingested

    if "session_data" in st.session_state:
        session_data = st.session_state.session_data
        session_data.duration_str = audio_res.duration_str
        
        # Update Visual telemetry
        if visual_res.slide_count > 0:
            session_data.telemetry["slide_count"] = visual_res.slide_count
            session_data.telemetry["slide_velocity_min"] = visual_res.slide_velocity_min
            session_data.retained_slides = [
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

        # Update Audio telemetry
        if audio_telemetry.success:
            session_data.telemetry["dead_air_pct"] = audio_telemetry.dead_air_pct
            session_data.telemetry["wpm"] = audio_telemetry.wpm
            session_data.telemetry["question_density"] = audio_telemetry.question_density
            session_data.telemetry["total_questions"] = audio_telemetry.total_questions
            session_data.telemetry["teacher_talk_pct"] = audio_telemetry.teacher_talk_pct
            session_data.telemetry["student_talk_pct"] = audio_telemetry.student_talk_pct

            if audio_telemetry.segments:
                session_data.transcript_snippets = [
                    TranscriptSnippet(
                        timestamp=s.timestamp_str,
                        speaker=s.speaker,
                        text=s.text,
                        keyframe_id=f"frame_{s.segment_id:02d}",
                        pedagogical_tag=s.pedagogical_tag,
                        explanation=s.explanation,
                    )
                    for s in audio_telemetry.segments
                ]

        # Step 4: Run LLM Pedagogical Judgement & Explanations (Epic 5)
        with st.spinner("Generating LLM pedagogical judgement & diagnostic sub-scores..."):
            from src.models.evaluator import run_evaluation, apply_evaluation_to_session
            eval_res = run_evaluation(
                session_data.telemetry,
                session_data.transcript_snippets,
                session_data.duration_str,
            )
            apply_evaluation_to_session(session_data, eval_res)

    return True


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
                    success = _process_and_store_ingested_media(
                        load_res.data, load_res.source_name, load_res.source_type, load_res.size_mb
                    )
                    if success:
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
                    success = _process_and_store_ingested_media(
                        load_res.data, load_res.source_name, load_res.source_type, load_res.size_mb
                    )
                    if success:
                        st.rerun()
            else:
                st.caption("Drop classroom recordings directly from your local machine (max 200MB).")

        # Demonstration notice when no custom media is currently active
        st.info("💡 Demonstrating active session with pre-extracted telemetry data. Ingest media above to evaluate new sessions.")
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
