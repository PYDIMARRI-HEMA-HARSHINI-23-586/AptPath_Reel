import streamlit as st
import os
import subprocess
import uuid
import whisper
import google.generativeai as genai  # ✅ NEW IMPORT

# Configure page
st.set_page_config(page_title="🎬 AptPath Reel Transcriber", layout="centered")
st.title("🎬 AptPath Reel Transcriber")
st.caption("Upload your video and get the transcript like a boss 😎")

# API Key from Streamlit secrets (for Gemini)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])  # ✅ USE GEMINI KEY FROM secrets.toml

# File uploader
video_file = st.file_uploader("📤 Upload your video", type=["mp4", "mov", "avi", "mkv"])

# ✅ Gemini version of extract_key_moments
def extract_key_moments(transcript_text):
    prompt = f"""
You are analyzing a video transcript. Identify the top 3-5 most engaging or insightful moments with their timestamps.

Output format:
1. [start_time] - [end_time]: [summary of event]
2. ...
Transcript:
{transcript_text}
"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

if video_file:
    for folder in ["uploads", "audio", "transcripts", "reels"]:
        os.makedirs(folder, exist_ok=True)

    unique_id = str(uuid.uuid4())[:8]
    video_path = os.path.join("uploads", f"{unique_id}_{video_file.name}")

    with open(video_path, "wb") as f:
        f.write(video_file.read())

    if not any(video_path.lower().endswith(ext) for ext in [".mp4", ".mov", ".avi", ".mkv"]):
        st.error("❌ Unsupported file format.")
        st.stop()

    with st.spinner("🔍 Validating video file..."):
        validation_cmd = ["ffmpeg", "-v", "error", "-i", video_path, "-f", "null", "-"]
        result = subprocess.run(validation_cmd, stderr=subprocess.PIPE, text=True)
        if result.stderr:
            st.error("❌ Video appears to be corrupted or unreadable.")
            st.text(result.stderr)
            st.stop()
        else:
            st.success(f"✅ Video uploaded and validated: {video_file.name}")

    # Step 1: Extract audio
    audio_path = os.path.join("audio", f"{unique_id}.wav")
    ffmpeg_cmd_audio = [
        "ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path, "-y"
    ]

    with st.spinner("🎧 Extracting audio from video..."):
        try:
            subprocess.run(ffmpeg_cmd_audio, check=True)
            st.success("🎵 Audio extracted successfully!")
        except subprocess.CalledProcessError:
            st.error("❌ Audio extraction failed.")
            st.stop()

    # Step 2: Transcribe using Whisper
    with st.spinner("🧠 Transcribing audio using Whisper..."):
        try:
            model = whisper.load_model("base")  # upgrade to "medium" or "large" if needed
            result = model.transcribe(audio_path)
            segments = result["segments"]

            timestamped_transcript = ""
            for seg in segments:
                start = round(seg["start"], 2)
                end = round(seg["end"], 2)
                text = seg["text"].strip()
                timestamped_transcript += f"[{start:.2f} - {end:.2f}] {text}\n"

            transcript_path = os.path.join("transcripts", f"{unique_id}.txt")
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(timestamped_transcript)

            st.success("📜 Transcription complete!")
            st.text_area("🕒 Transcript with Timestamps", timestamped_transcript, height=400)

        except Exception as e:
            st.error(f"❌ Whisper transcription failed: {str(e)}")
            st.stop()

    # Step 3: Analyze Key Moments with Gemini
    with st.spinner("📊 Analyzing transcript for key reel moments..."):
        try:
            key_moments = extract_key_moments(timestamped_transcript)
            st.subheader("🌟 Top Reel-Worthy Moments")
            st.text_area("🎯 Important Segments", key_moments, height=300)
        except Exception as e:
            st.error(f"❌ Gemini analysis failed: {str(e)}")

    # Step 4: Convert to Reel Format
    reel_path = os.path.join("reels", f"reel_{unique_id}.mp4")
    ffmpeg_cmd_reel = [
        "ffmpeg",
        "-i", video_path,
        "-vf", "scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "-y",
        reel_path
    ]

    with st.spinner("📱 Converting to Reel format..."):
        try:
            subprocess.run(ffmpeg_cmd_reel, check=True)
            st.success("🎥 Reel-format video saved successfully!")
            st.video(reel_path)
        except subprocess.CalledProcessError as e:
            st.error("⚠️ Failed to convert video to reel format.")
            st.text(str(e))
