import streamlit as st
import os
import subprocess
import uuid
import whisper
import google.generativeai as genai

# Configure Streamlit page
st.set_page_config(page_title="🎬 AptPath Reel Transcriber", layout="centered")
st.title("🎬 AptPath Reel Transcriber")
st.caption("Upload your video and get the transcript like a boss 😎")

# Gemini API key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# File uploader
video_file = st.file_uploader("📤 Upload your video", type=["mp4", "mov", "avi", "mkv"])

# Gemini: Key moments extraction
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

# Timestamp formatter for ASS format
def format_ass_timestamp(seconds):
    hrs, rem = divmod(int(seconds), 3600)
    mins, secs = divmod(rem, 60)
    millis = int((seconds - int(seconds)) * 100)
    return f"{hrs:01}:{mins:02}:{secs:02}.{millis:02}"

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
    ffmpeg_cmd_audio = ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path, "-y"]

    with st.spinner("🎧 Extracting audio from video..."):
        try:
            subprocess.run(ffmpeg_cmd_audio, check=True)
            st.success("🎵 Audio extracted successfully!")
        except subprocess.CalledProcessError:
            st.error("❌ Audio extraction failed.")
            st.stop()

    # Step 2: Transcribe using Whisper + generate .ass subtitles
    with st.spinner("🧠 Transcribing audio using Whisper..."):
        try:
            model = whisper.load_model("base")
            result = model.transcribe(audio_path)
            segments = result["segments"]

            # Generate timestamped transcript
            timestamped_transcript = ""
            for seg in segments:
                start = round(seg["start"], 2)
                end = round(seg["end"], 2)
                text = seg["text"].strip()
                timestamped_transcript += f"[{start:.2f} - {end:.2f}] {text}\n"

            transcript_path = os.path.join("transcripts", f"{unique_id}.txt")
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(timestamped_transcript)

            # 🔥 Generate .ass subtitle file
            ass_path = os.path.join("transcripts", f"{unique_id}.ass")
            with open(ass_path, "w", encoding="utf-8") as f:
                f.write("""[Script Info]
Title: Whisper Subtitles
ScriptType: v4.00+
Collisions: Normal
PlayResX: 1920
PlayResY: 1080
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,48,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,2,30,30,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
                for seg in segments:
                    start = format_ass_timestamp(seg["start"])
                    end = format_ass_timestamp(seg["end"])
                    text = seg["text"].replace("\n", " ").strip()
                    f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")

            st.success("📜 Transcription complete with subtitles!")
            st.text_area("🕒 Transcript with Timestamps", timestamped_transcript, height=400)

        except Exception as e:
            st.error(f"❌ Whisper transcription failed: {str(e)}")
            st.stop()

    # Step 3: Analyze key moments
    with st.spinner("📊 Analyzing transcript for key reel moments..."):
        try:
            key_moments = extract_key_moments(timestamped_transcript)
            st.subheader("🌟 Top Reel-Worthy Moments")
            st.text_area("🎯 Important Segments", key_moments, height=300)
        except Exception as e:
            st.error(f"❌ Gemini analysis failed: {str(e)}")

    # Step 4: Convert to 1080x1920 and burn subtitles
    reel_path = os.path.join("reels", f"reel_{unique_id}.mp4")
    ass_path_clean = ass_path.replace("\\", "/")  # 🔥 Fix for Windows paths in FFmpeg

    ffmpeg_cmd_reel = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,ass='{ass_path_clean}'",
        "-y",
        reel_path
    ]

    with st.spinner("📱 Converting to Reel format with subtitles..."):
        try:
            subprocess.run(ffmpeg_cmd_reel, check=True)
            st.success("🎥 Reel with subtitles ready to rock!")
            st.video(reel_path)
        except subprocess.CalledProcessError as e:
            st.error("⚠ Failed to convert video to reel format with subtitles.")
            st.text(str(e))