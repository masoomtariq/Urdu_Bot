import streamlit as st
import speech_recognition as sr
import tempfile
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from gtts import gTTS
from dotenv import load_dotenv
import os
import hashlib
from io import BytesIO

load_dotenv()

# LangSmith tracking
LANGCHAIN_PROJECT = "Urdu Bot"
os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")

groq_api_key = os.getenv("GROQ_API_KEY")

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
                st.success("✅ جواب تیار ہے!")
            
            except sr.UnknownValueError:
                st.error("❌ آپ کی آواز واضح نہیں ہے - براہ کرم دوبارہ کوشش کریں۔")
            
            except sr.RequestError:
                st.error("❌ معذرت، سسٹم کی سروس مصروف ہے، براہ کرم دوبارہ کوشش کریں۔")
            
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
        st.divider()
        st.subheader("💬 پچھلی بات چیت")
        
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
