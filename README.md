# 🤖 Urdu Voice Chatbot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.54.0+-red.svg)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-green.svg)](https://groq.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Enabled-yellow.svg)](https://langchain.com/)

🚀 **[Try the Live App](https://masoomtariq-urdu-bot.hf.space/)** 🚀

An intelligent voice-based conversational AI chatbot designed specifically for **Urdu language** speakers. This bot allows users to interact naturally through voice in Urdu, leveraging cutting-edge AI models and speech processing technologies.

## 🌟 Features

- 🎤 **Voice Input** - Speak naturally in Urdu and get instant text transcription
- 🤖 **AI-Powered Responses** - Uses Groq's Llama 3.3 70B model for intelligent, context-aware conversations
- 🔊 **Voice Output** - Responses are automatically converted to natural Urdu speech using Piper
- 💬 **Chat History** - Maintains complete conversation context with smart display
- 🎯 **Urdu-First Design** - Fully optimized for Urdu language processing
- ⚡ **Lightning Fast** - Powered by Groq's LPU technology for ultra-fast responses
- 📊 **LangSmith Integration** - Full observability and tracing for monitoring
- 🛡️ **Robust Error Handling** - Comprehensive error management for production use

## 🎥 Demo

Interact with the chatbot by:
1. Speaking in Urdu
2. Getting instant AI responses
3. Listening to natural voice output
4. Viewing complete conversation history

## 🏗️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | Streamlit | Interactive web UI |
| **LLM Provider** | Groq | Fast AI inference |
| **AI Model** | Llama 3.3 70B Versatile | Natural language understanding |
| **LLM Integration** | LangChain | Message handling & history |
| **Speech-to-Text** | Groq Whisper (whisper-large-v3-turbo) | Urdu voice → text conversion via Groq Cloud |
| **Text-to-Speech** | Piper | Urdu text → voice synthesis with a fine-tuned model |
| **Observability** | LangSmith | Request tracing & monitoring |
| **Environment** | python-dotenv | Secure API key management |

## 🎯 Architecture

```
User Voice (Urdu) 
      ↓
[Groq Speech-to-Text (whisper-large-v3-turbo)]
      ↓
Urdu Text Input
      ↓
[LangChain + Groq Llama 3.3 70B]
      ↓
Urdu Text Response
      ↓
[Piper Fine-Tuned Urdu Voice Model]
      ↓
Voice Output (Urdu)
```

## 📋 Prerequisites

- Python 3.8 or higher
- Microphone access for voice input
- Internet connection
- Groq API key (free tier available)
- LangSmith API key (optional, for monitoring)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/masoomtariq/Urdu_Bot.git
cd Urdu_Bot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Notes for Local Run

For a local Linux run, you need the Piper binary and both Urdu model files in the project root:

- `piper/piper`
- `ur_PK-fasih-medium-model.onnx`
- `ur_PK-fasih-medium-model.onnx.json`

One-time Linux setup:

```bash
mkdir -p piper
curl -L "https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz" -o /tmp/piper_linux_x86_64.tar.gz
tar -xzf /tmp/piper_linux_x86_64.tar.gz -C piper --strip-components=1
chmod +x piper/piper
rm -f /tmp/piper_linux_x86_64.tar.gz
curl -L "https://huggingface.co/IhorShevchuk/piper-voice-ur-fasih/resolve/main/ur_PK-fasih-medium-model.onnx" -o ur_PK-fasih-medium-model.onnx
curl -L "https://huggingface.co/IhorShevchuk/piper-voice-ur-fasih/resolve/main/ur_PK-fasih-medium-model.onnx.json" -o ur_PK-fasih-medium-model.onnx.json
```

Windows note: the Dockerfile uses the Linux Piper build, so native Windows users should use WSL/Linux or a Windows-compatible Piper release instead of the commands above.

### 5. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional (for monitoring)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

**Get Your API Keys:**
- **Groq API**: Sign up at [console.groq.com](https://console.groq.com/)
- **LangSmith**: Sign up at [smith.langchain.com](https://smith.langchain.com/)

## 💻 Usage

### Run the Application

```bash
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`

### How to Use

1. **Grant Microphone Permission** - Allow browser to access your microphone
2. **Click "پوچھیے" (Ask)** - Start recording your question in Urdu
3. **Speak Your Question** - Talk naturally in Urdu
4. **Wait for Processing** - The bot will:
   - Transcribe your voice to text
   - Generate an intelligent response
      - Convert response to voice using Piper
5. **Listen & Read** - View and hear the complete conversation
6. **Continue Chatting** - Ask follow-up questions with full context

### Clear Chat History

Click the **"🗑️ بات چیت صاف کریں"** button in the sidebar to start a new conversation.

## 📁 Project Structure

```
Urdu_Bot/
│
├── main.py                 # Main application file
│   ├── main()              # UI orchestration & workflow
│   ├── initialize_state()   # Session state management
│   ├── get_text()           # Speech recognition (Urdu)
│   ├── generate_response()  # AI response generation
│   ├── play_audio()         # Piper-based text-to-speech synthesis
│   ├── normalize_tts_text()  # Clean text before speech synthesis
│   └── display_previous_chats() # Chat history display
│
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (create this)
├── README.md              # Project documentation
└── LICENSE                # MIT License

```

## 🔧 How It Works

- Voice input is transcribed with Groq Whisper (`whisper-large-v3-turbo`)
- Responses are generated with Groq Llama 3.3 70B and stored in chat history
- Text-to-speech uses Piper with the Urdu voice model files listed above
- The current conversation stays in session and previous messages remain visible

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Contribution
- Add support for other Pakistani languages (Pashto, Sindhi, Punjabi)
- Implement voice selection (male/female)
- Add conversation export feature
- Improve UI/UX design
- Add unit tests

## 🙏 Acknowledgments

- **Groq** - For providing ultra-fast LPU inference
- **Meta** - For the Llama 3.3 70B model
- **LangChain** - For excellent LLM integration framework
- **Groq** - For Speech-to-Text (Whisper) and model hosting
- **Piper** - For high-quality Urdu text-to-speech synthesis
- **Streamlit** - For the amazing web framework

## 👨‍💻 Author

**Masoom Tariq**
- GitHub: [@masoomtariq](https://github.com/masoomtariq)
- Email: mmasoomtariq@gmail.com
- LinkedIn: [Connect with me](https://www.linkedin.com/in/masoom-tariq-b0aa89291/))

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Open an [Issue](https://github.com/masoomtariq/Urdu_Bot/issues)
3. Review existing issues for solutions

---

⭐ **If you find this project useful, please consider giving it a star!** ⭐

---

**Built with ❤️ for the Urdu-speaking community**
