---
title: 8x8 Class Quality Evaluator
emoji: 🎓
colorFrom: indigo
colorTo: blue
sdk: streamlit
sdk_version: "1.38.0"
app_file: app.py
pinned: false
---

# 🎓 8x8 Class Quality Evaluator
An interactive prototype built for the **Humaniti AI / 8x8 Class Quality Challenge**. It assesses online classroom recordings into **Poor, Average, Good, or Excellent** by extracting in-memory audio and visual telemetry, paired with an LLM pedagogical judge and a deterministic local fallback.

---

## 🔍 What Is Implemented

The application is delivered as a dual-pane Streamlit interface:
* **Media Ingestion & Ephemeral Lifecycle (`src/ingestion/`):**
  * Accepts media input via direct URL (HTTP/HTTPS stream or cloud recording) or local file upload (`.mp4`, `.m4a`, `.wav`, `.mp3`).
  * Extracts audio in-memory to 16 kHz Mono PCM using FFmpeg.
  * Enforces an ephemeral lifecycle: raw audio buffers are purged and garbage-collected post-processing (`EphemeralAudioBuffer`).
* **Content-Only Visual Pipeline (`src/vision/`):**
  * Samples video frames sparsely (1 frame every 5 seconds).
  * **Face Dropping Gate:** Employs an OpenCV Haar cascade face detector to immediately discard any frame containing a human face to avoid storing pupil or teacher biometrics.
  * Extracts retained instructional frames (slides, whiteboards, code editors) and computes visual clutter using Canny edge density.
  * Estimates slide transition velocity based on frame dissimilarity.
* **Audio Telemetry & Transcription (`src/audio/`):**
  * **Voice Activity Detection (VAD):** In-memory 30ms RMS energy thresholding to compute active speech time and silence voids (dead air %).
  * **Speech-to-Text:** Quantized INT8 Whisper-tiny running locally on CPU.
  * **Regex PII Redaction:** Sanitizes emails, phone numbers, URLs, student IDs, and teacher/student references from transcripts before display or model evaluation.
  * **Cadence & Inquiry:** Measures Words Per Minute (WPM) during active speech and parses question density (interrogatives per hour).
* **Pedagogical Evaluation Engine (`src/models/`):**
  * Evaluates telemetry and scrubbed dialogue against 4 dimensions: *Instructional Clarity*, *Student Engagement*, *Pacing & Delivery*, and *Content & Visual Structure*.
  * **Dual-Inference Path:** Calls Gemini or OpenAI if API keys are provided in the environment. If no API keys are present, it falls back to a deterministic, rule-based rubric engine so the app runs offline with zero external dependencies.
* **Interactive UI Dashboard (`src/ui/`):**
  * **Left Pane:** Media loader, retained non-face slide gallery, and searchable synchronized transcript.
  * **Right Pane:** Quality badge (`Poor`, `Average`, `Good`, `Excellent`), KPI cards with benchmark flags, 4 dimension sub-scores with feedback, actionable coaching tips, and a confidence distribution chart.

---

## 🚀 How to Run Locally

### 1. Requirements
* **Python 3.10+**
* **FFmpeg** installed and accessible in your system `PATH`:
  * **macOS:** `brew install ffmpeg`
  * **Ubuntu/Debian:** `sudo apt-get install -y ffmpeg`
  * **Windows:** `choco install ffmpeg`

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/your-username/8x8-class-quality-evaluator.git
cd 8x8-class-quality-evaluator

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch Application
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser. The app starts with a pre-loaded reference scenario for immediate inspection, and allows you to ingest any `.mp4`/`.wav` file or direct link.

### 4. (Optional) External LLM Configuration
By default, the system evaluates recordings locally using the deterministic rubric engine. To enable live LLM evaluation via external APIs:
```bash
export GEMINI_API_KEY="your-gemini-api-key"
# or
export OPENAI_API_KEY="your-openai-api-key"
```

---

## 🧪 How to Run Tests

The repository includes a test suite covering the ingestion pipeline, face filtering, VAD dead-air detection, PII sanitization, the evaluation engine, and deployment resilience:

```bash
# Execute the unified test runner
python tests/run_all.py
```
Expected output:
```text
============================================================
🚀 Running 8x8 Class Quality Evaluator Test Suites
============================================================
▶ Epic 1: UI & Telemetry Generator .............. [2 passed]
▶ Epic 2: Media Ingestion & Ephemeral Lifecycle .. [6 passed]
▶ Epic 3: Face-Filtered Visual Content Engine .... [4 passed]
▶ Epic 4: Audio Telemetry, VAD & PII Sanitizer ... [5 passed]
▶ Epic 5: Pedagogical Evaluation & LLM Engine .... [5 passed]
▶ Epic 7: Deployment, Resource Hardening & Res. .. [5 passed]
============================================================
🎉 Results: 27/27 tests passed successfully!
============================================================
```

Individual test files can also be run directly:
```bash
python tests/test_audio.py
python tests/test_vision.py
python tests/test_ingestion.py
python tests/test_models.py
python tests/test_resilience_and_deployment.py
```

---

## 🚀 Hugging Face Spaces Deployment

The repository includes an automated GitHub Action workflow (`.github/workflows/sync_to_hf.yml`) that automatically synchronizes your `main` branch to your Hugging Face Space whenever you push code.

### Step-by-Step Setup:
1. **Create the Hugging Face Space:**
   * Go to [Hugging Face Spaces](https://huggingface.co/new-space).
   * Name: `8x8-class-quality-evaluator`
   * SDK: **Streamlit**
   * Hardware: **CPU Basic (Free - 16GB RAM, 2 vCPU)**
2. **Generate Hugging Face Access Token:**
   * Go to [Hugging Face Access Tokens](https://huggingface.co/settings/tokens).
   * Click **Create new token** $\rightarrow$ select **Write** permission $\rightarrow$ copy the token.
3. **Add Secret to GitHub:**
   * On your GitHub repository, navigate to **Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions**.
   * Click **New repository secret**.
   * **Name:** `HF_TOKEN`
   * **Value:** *(Paste your Hugging Face Write Token)*
   * Click **Add secret**.
4. *(Optional) Custom Space Name:*
   * If your Space name differs from `NiranjanAjith/8x8-class-quality-evaluator`, add a Repository Variable named `HF_SPACE_REPO` under **Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions** $\rightarrow$ **Variables** with value `<YourHFUsername>/<YourSpaceName>`.
5. **Automatic Deployment:**
   * Any push to `main` will automatically trigger the sync workflow and deploy your live Streamlit dashboard on Hugging Face Spaces!

---

## ⚠️ Constraints & Unimplemented Plans

This project was built within the 4–5 hour challenge window. As a result, several planned features were scoped down or deferred:

1. **Lack of Empirical Model Bake-Off:**
   * *Planned:* The initial backlog planned an offline bake-off comparing a baseline LLM prompt against a Jev probabilistic choice model and a multimodal ML hybrid, complete with Expected Calibration Error (ECE) and feature ablation audits.
   * *Current State:* Given the time limit, formal statistical benchmarking was cut. The application relies on heuristic thresholds and a structured LLM prompt with a rule-based fallback. The ratings have **not** been calibrated against a large human-labeled dataset.
2. **Simplified Feature Attribution (SHAP):**
   * *Planned:* True KernelSHAP/TreeSHAP computation calculating exact marginal contribution scores for each feature.
   * *Current State:* Feature impacts shown in demonstration scenarios use pre-calculated heuristic weights rather than live Shapley value estimation.
3. **Speaker Diarization Limitations:**
   * Teacher vs. student voice distribution is estimated using turn length and interrogative triggers rather than acoustic voiceprint clustering. Overlapping speech cannot be cleanly split on single-channel audio.
4. **Lightweight Face Detection:**
   * OpenCV's Haar cascade was chosen for speed on CPU without GPU dependencies. While it drops frontal webcam shots reliably, it can miss extreme profile angles or occluded faces compared to heavier deep-learning detectors (e.g., RetinaFace).
5. **CPU / Free-Tier Resource Constraints:**
   * Designed for $\ge 4\text{ GB}$ RAM CPU environments (Hugging Face Spaces). Long recordings (> 45 minutes) will take several minutes to transcribe on CPU using Whisper-tiny.
