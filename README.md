# 🤖 Urdu Voice Chatbot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.54.0+-red.svg)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-green.svg)](https://groq.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Enabled-yellow.svg)](https://langchain.com/)

🚀 **[Try the Live App](https://urdu-bot.streamlit.app/)** 🚀

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

### 4. Set Up Environment Variables

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
streamlit run app.py
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
├── app.py                  # Main application file
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

### 1. **Voice Input Processing**
- User records audio via Streamlit's audio input widget
      - Groq Speech-to-Text (`whisper-large-v3-turbo`) converts Urdu audio to text
- MD5 hash prevents duplicate processing on page reruns

### 2. **AI Response Generation**
- User message added to LangChain conversation history
- Groq's Llama 3.3 70B model processes the request
- System prompt ensures responses are in Urdu only
- Response added to conversation history

### 3. **Voice Output**
- AI response normalized to remove markdown markers and stray symbols
- Text converted to speech using Piper with a fine-tuned Urdu voice model
- Audio buffered in memory (BytesIO) for efficiency
- Auto-plays in the browser with text display

### 4. **Chat History Management**
- Current conversation displays inline with voice players
- Previous conversations show below in text format
- Newest messages appear first
- Full context maintained across session

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
