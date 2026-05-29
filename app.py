import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import os
import hashlib
import re
from io import BytesIO
import stat
import subprocess

load_dotenv()


def get_clean_env_value(name):
    """Return an environment variable without surrounding quotes or whitespace."""
    value = os.getenv(name)
    if value is None:
        return None
    return value.strip().strip('"').strip("'")


# LangSmith tracking
LANGCHAIN_PROJECT = "Urdu Bot"
os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
os.environ["LANGSMITH_TRACING"] = "true"

langsmith_endpoint = get_clean_env_value("LANGSMITH_ENDPOINT")
if langsmith_endpoint:
    os.environ["LANGSMITH_ENDPOINT"] = langsmith_endpoint

langsmith_api_key = get_clean_env_value("LANGSMITH_API_KEY")
if langsmith_api_key:
    os.environ["LANGSMITH_API_KEY"] = langsmith_api_key

groq_api_key = get_clean_env_value("GROQ_API_KEY")

def main():
    st.set_page_config(page_title="Urdu Voice Chatbot", layout="wide")
    st.title("🤖 Urdu Voice Chatbot")
        
    st.sidebar.title('''About this App''')
    st.sidebar.info(f'''This is a Urdu voice chatbot created using Streamlit. It takes in Urdu voice input and responds in Urdu voice using Groq's Llama model.''')

    st.sidebar.write("")
    st.sidebar.write("")

    st.sidebar.write("Developed by :blue[Masoom Tariq]")
    st.sidebar.write("Powered by :green[Groq] : Llama 3.3 70B")
    
    # Clear chat button in sidebar
    if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.clear()
        initialize_state()
        st.rerun()

    initialize_state()

    # Audio input section
    st.subheader("🎤 اپنی آواز ریکارڈ کریں")
    st.session_state.audio = st.audio_input("پوچھیے")

    # Flag to prevent reprocessing same audio
    if 'last_audio_hash' not in st.session_state:
        st.session_state.last_audio_hash = None

    if st.session_state.audio:
        # Create hash of audio to detect new recordings
        audio_bytes = st.session_state.audio.read()
        st.session_state.audio.seek(0)  # Reset position for later reading
        current_hash = hashlib.md5(audio_bytes).hexdigest()
        
        # Only process if this is a new audio (different from last one)
        if current_hash != st.session_state.last_audio_hash:
            st.session_state.last_audio_hash = current_hash
            
            try:
                with st.spinner("🔄 سن رہے ہیں..."):
                    get_text()
                with st.spinner("💭 سوچ رہے ہیں..."):
                    generate_response()
                with st.spinner("🎵 آواز تیار کر رہے ہیں..."):
                    play_audio()

            except ValueError as ve:
                # Errors raised for invalid/missing audio
                st.error(f"❌ {str(ve)}")

            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a rate limit error (Groq: 30 req/min)
                if "429" in error_msg or "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
                    st.error("❌ API کی حد پوری ہو گئی (Rate Limit)")
                    st.warning("⏳ Groq Free: 30 requests/minute - براہ کرم کچھ سیکنڈ انتظار کریں")
                
                # Check for authentication error
                elif "401" in error_msg or "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                    st.error("❌ API Key غلط ہے۔ براہ کرم .env فائل چیک کریں")
                    st.warning("ℹ️ GROQ_API_KEY درکار ہے")
                
                else:
                    st.error("❌ معذرت، AI سروس میں خرابی ہے۔ براہ کرم دوبارہ کوشش کریں۔")
                    st.warning(f"⚠️ تفصیلات: {error_msg[:150]}")
                
                print(f"Error: {type(e).__name__}: {error_msg}")
    
    # Show previous chat history (if exists)
    display_previous_chats()


def display_previous_chats():
    """Display previous chat conversations (excluding the current one)"""
    # Filter out SystemMessage
    chat_messages = [msg for msg in st.session_state.history 
                     if not isinstance(msg, SystemMessage)]
    
    # If there are more than 2 messages (current conversation), show previous ones
    if len(chat_messages) > 2:
        # Show previous conversations (skip the last 2 which are current)
        previous_messages = chat_messages[:-2]
        
        # Display in reverse order (newest first)
        for i in range(len(previous_messages) - 1, -1, -2):
            if i >= 1:  # Make sure we have both user and assistant messages
                user_msg = previous_messages[i-1]
                assistant_msg = previous_messages[i]
                
                with st.container(border=True):
                    # User message
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(f"**آپ:** {user_msg.content}")
                    
                    # Assistant message
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(f"**بوٹ:** {assistant_msg.content}")




def initialize_state():
    """Initialize session state variables"""
    initialStates = {
        'text_response': '',
        'history': [],
        'prompt': '',
        'audio': ''
    }
    for key, value in initialStates.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    if not st.session_state.history:
        instructions = "آپ ایک مددگار اے آئی اسسٹنٹ ہیں۔ آپ صرف اردو میں جواب دیتے ہیں۔ اپنے جواب سادہ، رواں اور غیر رسمی مگر واضح اردو جملوں میں دیں۔ Markdown، bullet points، star markers، اور اردو کے علاوہ الفاظ استعمال نہ کریں۔"
        st.session_state.history.append(SystemMessage(content=instructions))


def get_text():
    """Transcribe uploaded audio using Groq Whisper Turbo"""
    if st.session_state.audio is None:
        raise ValueError("No audio file found.")

    # read bytes from Streamlit's uploaded audio object (be robust)
    try:
        if hasattr(st.session_state.audio, "getvalue"):
            audio_bytes = st.session_state.audio.getvalue()
        else:
            st.session_state.audio.seek(0)
            audio_bytes = st.session_state.audio.read()
    except Exception:
        raise ValueError("Failed to read audio bytes from the uploaded audio object.")

    file_name = getattr(st.session_state.audio, "name", "audio.wav")

    try:
        # Lazy import to avoid adding dependency when not used
        from groq import Groq

        # Instantiate client (will pick up API key from environment if not provided)
        client = Groq(api_key=groq_api_key) if groq_api_key else Groq()

        transcription = client.audio.transcriptions.create(
            file=(file_name, audio_bytes),
            model="whisper-large-v3-turbo",
            language="ur",
            temperature=0.0
        )

        # Groq SDK returns .text for simple transcription
        st.session_state.prompt = transcription.text.strip()
        st.write(f"📝 **آپ کا پیغام:** {st.session_state.prompt}")

    except Exception as e:
        raise Exception(f"Groq Whisper Turbo transcription failed: {str(e)}")


def generate_response():
    """Generate response from LLM using chat history"""
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is missing. Set it in your environment before running the app.")

    # Using Groq's Llama model (free tier: 30 requests/minute, 14,400 tokens/minute)
    # Available models: llama-3.3-70b-versatile, llama-3.1-70b-versatile, mixtral-8x7b-32768
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        api_key=groq_api_key
    )
    st.session_state.history.append(HumanMessage(content=st.session_state.prompt))
    
    response = llm.invoke(st.session_state.history)
    st.session_state.text_response = response.content
    st.session_state.history.append(AIMessage(content=response.content))
  

def play_audio():
    """Convert text response to speech using Piper TTS"""
    if not st.session_state.text_response:
        return

    # Piper handles flowing text more reliably than multiline bullet-style output.
    tts_text = normalize_tts_text(st.session_state.text_response)
        
    # 1. Ensure the piper binary has execution permissions (Crucial for Git deployments)
    piper_path = "./piper/piper"
    if os.path.exists(piper_path):
        current_permissions = os.stat(piper_path).st_mode
        os.chmod(piper_path, current_permissions | stat.S_IEXEC)

    # 2. Configure Piper command
    # Using '-' for output_file streams the raw WAV audio directly to memory
    piper_cmd = [
        piper_path, 
        "--model", "ur_PK-fasih-medium-model.onnx",
        "--config", "ur_PK-fasih-medium-model.onnx.json",
        "--output_file", "-" 
    ]

    try:
        # 3. Run piper, passing text via stdin and capturing WAV via stdout
        process = subprocess.run(
            piper_cmd,
            input=tts_text.encode('utf-8'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        # 4. Load the raw WAV bytes into the BytesIO buffer
        audio_buffer = BytesIO(process.stdout)
        audio_buffer.seek(0)
        
        # 5. Play audio (Piper outputs WAV format) and display text
        st.audio(audio_buffer, format='audio/wav')
        st.write(f"🎤 **بوٹ کا جواب:** {st.session_state.text_response}")
        
    except subprocess.CalledProcessError as e:
        st.error(f"TTS Error: {e.stderr.decode('utf-8')}")
    except FileNotFoundError:
        st.error("Piper binary not found. Please ensure the './piper/piper' folder is committed to your GitHub repository.")


def normalize_tts_text(text):
    """Flatten multiline assistant text into a single pronunciation-friendly string."""
    text = text.strip().strip('"“”')
    text = re.sub(r"(?m)^\s*[*•-]+\s*", "", text)
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"[\*•]+", "", text)
    text = re.sub(r"[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF0-9A-Za-zऀ-ॿ\s،۔,:;!?()/%-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


if __name__ == "__main__":
    main()
