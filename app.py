import streamlit as st
import speech_recognition as sr
import tempfile
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from gtts import gTTS
from dotenv import load_dotenv
import os
import hashlib
from io import BytesIO
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

load_dotenv()

# LangSmith tracking
LANGCHAIN_PROJECT = "Urdu Bot"
os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")

google_key = os.getenv("GOOGLE_API_KEY")

def main():
    st.set_page_config(page_title="Urdu Voice Chatbot", layout="wide")
    st.title("🤖 Urdu Voice Chatbot")
        
    st.sidebar.title('''About this App''')
    st.sidebar.info(f'''This is a Urdu voice chatbot created using Streamlit. It takes in Urdu voice input and responds in Urdu voice''')

    st.sidebar.write("")
    st.sidebar.write("")

    st.sidebar.write("Developed by :blue[Masoom Tariq]")
    
    # Clear chat button in sidebar
    if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.clear()
        initialize_state()
        st.rerun()

    initialize_state()

    # Display chat history
    display_chat_history()
    
    st.divider()

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
                st.success("✅ جواب تیار ہے!")
            
            except sr.UnknownValueError:
                st.error("❌ آپ کی آواز واضح نہیں ہے - براہ کرم دوبارہ کوشش کریں۔")
            
            except sr.RequestError:
                st.error("❌ معذرت، سسٹم کی سروس مصروف ہے، براہ کرم دوبارہ کوشش کریں۔")
            
            except ChatGoogleGenerativeAIError as e:
                st.error("❌ معذرت، AI سروس میں خرابی ہے۔ براہ کرم دوبارہ کوشش کریں۔")
                st.warning("⚠️ براہ کرم بعد میں دوبارہ کوشش کریں")
            
            except Exception as e:
                st.error("❌ ایک غیر متوقع خرابی واقع ہوئی۔")


def display_chat_history():
    """Display formatted chat history with messages"""
    
    # Filter out SystemMessage (only show user and AI messages)
    chat_messages = [msg for msg in st.session_state.history 
                     if not isinstance(msg, SystemMessage)]
    
    if not chat_messages:
        st.info("📭 کوئی بھی بات چیت ابھی شروع نہیں ہوئی۔ اپنا سوال پوچھیں!")
        return
    
    st.subheader("💬 بات چیت کی تاریخ")
    
    # Create a container for chat messages
    chat_container = st.container(border=True)
    
    with chat_container:
        # Display messages in order (oldest to newest)
        for message in chat_messages:
            if isinstance(message, HumanMessage):
                with st.chat_message("user", avatar="👤"):
                    st.markdown(f"**آپ:** {message.content}")
            
            elif isinstance(message, AIMessage):
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(f"**بوٹ:** {message.content}")
    
    # Show message count
    st.caption(f"📊 کل پیغامات: {len(chat_messages)}")


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
        instructions = "آپ ایک مددگار اے آئی اسسٹنٹ ہیں۔ آپ ہر وہ کام کر سکتے ہیں جو مناسب ہو لیکن آپ صرف اردو زبان جانتے ہیں اور ہمیشہ صرف اردو زبان میں جواب دیتے ہیں۔"
        st.session_state.history.append(SystemMessage(content=instructions))


def get_text():
    """Convert speech to text using Google Speech Recognition"""
    # Audio is already at position 0 from main() seek operation
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        temp_file.write(st.session_state.audio.read())
        file_path = temp_file.name

    try:
        with sr.AudioFile(file_path) as source:
            r = sr.Recognizer()
            recorded = r.record(source)
            st.session_state.prompt = r.recognize_google(audio_data=recorded, language='ur')
            st.write(f"📝 **آپ کا پیغام:** {st.session_state.prompt}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


def generate_response():
    """Generate response from LLM using chat history"""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, api_key=google_key)
    st.session_state.history.append(HumanMessage(content=st.session_state.prompt))
    
    response = llm.invoke(st.session_state.history)
    st.session_state.text_response = response.content
    st.session_state.history.append(AIMessage(content=response.content))
  

def play_audio():
    """Convert text response to speech using gTTS"""
    if not st.session_state.text_response:
        return
        
    ai_audio = gTTS(text=st.session_state.text_response, lang='ur')
    
    # Read audio into bytes instead of saving to file
    audio_buffer = BytesIO()
    ai_audio.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    
    # Pass bytes directly to st.audio (no file path issues)
    st.audio(audio_buffer, format='audio/mp3')
    st.write(f"🎤 **بوٹ کا جواب:** {st.session_state.text_response}")


if __name__ == "__main__":
    main()
