# 🎬 AptPath Reel Transcriber

Turn any video into a scroll-stopping **Instagram/TikTok reel** with **AI-powered transcription, subtitles, and key highlights**.

## ✨ Features

- 📤 Upload videos (`.mp4`, `.mov`, `.avi`, `.mkv`)
- 🎧 Extract audio and transcribe using **OpenAI Whisper**
- 📜 Generate timestamps and export subtitles in `.ass` format
- 🌟 Summarize & extract **key reel-worthy moments** with **Google Gemini**
- 🎥 Convert video to **1080x1920 (reel format)** with subtitles burnt in
- 🚀 All powered by a **Streamlit app**

## 🛠️ Tech Stack

- **Frontend + Backend:** Streamlit
- **Transcription:** OpenAI Whisper
- **AI Analysis:** Google Gemini API
- **Video Processing:** FFmpeg
- **Language:** Python

## 📂 Project Structure

├── uploads/ # Original uploaded videos
├── audio/ # Extracted audio files
├── transcripts/ # Generated transcripts & subtitles
├── reels/ # Final reel outputs
app.py # Main Streamlit app

## 🚀 Getting Started

1. Clone this repo  
   git clone https://github.com/username/AptPath_Reel.git
   cd AptPath_Reel
2. Install dependencies
   pip install -r requirements.txt
3. Add your Gemini API Key to .streamlit/secrets.toml:
   GEMINI_API_KEY = "your_api_key_here"
4. Run the app
   streamlit run app.py

🎯 Example Workflow
Upload your video
Audio is extracted → Transcribed via Whisper
Key reel-worthy moments extracted via Gemini
Video converted to 1080x1920 with subtitles
Download and share your AI-generated reel 🎉

🌟 Future Enhancements
🎨 Custom subtitle styles & fonts
🧠 Auto-clip highlights into short 30s reels
☁️ Cloud storage & one-click sharing
🤖 Multi-language support
