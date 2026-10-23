"""
Test Runner for 8x8 Class Quality Evaluator.
Executes all unit and integration test suites.
"""
import sys
import unittest

def run_all_tests():
    import tests.test_session_and_ui as t1
    import tests.test_ingestion as t2
    import tests.test_vision as t3
    import tests.test_audio as t4
    import tests.test_models as t5
    import tests.test_resilience_and_deployment as t6

    suites = [
        ("Epic 1: Production Domain Models & UI Orchestration", [
            t1.test_empty_session_structure,
            t1.test_chart_generation,
            t1.test_empty_state_initial_rendering,
            t1.test_monologue_rubric_downgrade,
        ]),
        ("Epic 2: Media Ingestion & Ephemeral Lifecycle", [
            t2.test_ffmpeg_binary_availability,
            t2.test_load_media_from_file,
            t2.test_load_media_from_file_size_limit,
            t2.test_load_media_from_invalid_url,
            t2.test_audio_extraction_and_normalization,
            t2.test_ephemeral_lifecycle_guard,
        ]),
        ("Epic 3: Face-Filtered Visual Content Engine", [
            t3.test_visual_clutter_computation,
            t3.test_face_detection_on_uniform_image,
            t3.test_slide_transitions_detection,
            t3.test_pipeline_on_empty_payload,
        ]),
        ("Epic 4: Audio Telemetry, VAD & PII Sanitizer", [
            t4.test_transcript_pii_sanitization,
            t4.test_in_memory_vad_dead_air_detection,
            t4.test_speech_pacing_and_question_metrics,
            t4.test_audio_pipeline_execution,
            t4.test_ui_audio_pipeline_integration,
        ]),
        ("Epic 5: Pedagogical Evaluation & LLM Engine", [
            t5.test_pedagogical_prompt_builder,
            t5.test_deterministic_rubric_evaluator_high_engagement,
            t5.test_deterministic_rubric_evaluator_poor_monologue,
            t5.test_parse_json_evaluation,
            t5.test_apply_evaluation_to_session,
        ]),
        ("Epic 7: Deployment, Resource Hardening & Resilience", [
            t6.test_deployment_manifests,
            t6.test_audio_only_media_pipeline,
            t6.test_total_silence_and_zero_division,
            t6.test_all_faces_dropped_resilience,
            t6.test_multi_session_memory_eviction_loop,
        ]),
    ]

    total_passed = 0
    total_tests = 0

    print("=" * 60)
    print("🚀 Running 8x8 Class Quality Evaluator Test Suites")
    print("=" * 60)

    for suite_name, test_funcs in suites:
        print(f"\n▶ {suite_name}")
        for fn in test_funcs:
            total_tests += 1
            try:
                fn()
                print(f"  ✓ {fn.__name__}")
                total_passed += 1
            except Exception as e:
                print(f"  ✗ {fn.__name__}: {e}")
                raise e

    print("\n" + "=" * 60)
    print(f"🎉 Results: {total_passed}/{total_tests} tests passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
