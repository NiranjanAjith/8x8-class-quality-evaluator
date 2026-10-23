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

An air-gapped, privacy-first pedagogical assessment dashboard for classroom sessions.

## 🚀 Key Features
* **Dual-Pane Evaluation Dashboard:** Live media inspection on the left, executive quality grading on the right.
* **Privacy via Frame & Audio Eviction:** Drops webcam frames containing detected faces; purges raw audio buffers immediately after local transcription.
* **Multimodal Classroom Telemetry:** Tracks Talk-to-Listen ratio, speech pacing (WPM), question density, silence gaps (dead air %), and slide transition velocity.
* **Pedagogical LLM Judgement & Explanations:** Evaluates classroom quality with structured sub-scores (Clarity, Engagement, Pacing, Content Structure), key observed strengths, and actionable instructional coaching plans.

## 🛠️ Local Development
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit application
streamlit run app.py
```
