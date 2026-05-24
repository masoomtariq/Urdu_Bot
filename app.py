import streamlit as st
import tempfile
import wave
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import os
import hashlib
import shutil

import numpy as np
import soundfile as sf
import torch
from huggingface_hub import hf_hub_download
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
from piper import PiperVoice

load_dotenv()

# LangSmith tracking
LANGCHAIN_PROJECT = "Urdu Bot"
os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")

groq_api_key = os.getenv("GROQ_API_KEY")
WHISPER_MODEL_ID = "Abdul145/whisper-medium-urdu-custom"
PIPER_REPO_ID = "IhorShevchuk/piper-voice-ur-fasih"
PIPER_MODEL_FILE = "ur_PK-male-medium.onnx"
PIPER_CONFIG_FILE = "ur_PK-male-medium.onnx.json"

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
        instructions = "آپ ایک مددگار اے آئی اسسٹنٹ ہیں۔ آپ ہر وہ کام کر سکتے ہیں جو مناسب ہو لیکن آپ صرف اردو زبان جانتے ہیں اور ہمیشہ صرف اردو زبان میں جواب دیتے ہیں۔"
        st.session_state.history.append(SystemMessage(content=instructions))


@st.cache_resource
def load_whisper_assets():
    """Load the fine-tuned Urdu Whisper processor and model."""
    processor = AutoProcessor.from_pretrained(WHISPER_MODEL_ID)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        WHISPER_MODEL_ID,
        dtype=dtype,
        low_cpu_mem_usage=True,
    )
    model.to(device)
    model.eval()
    return processor, model, device


@st.cache_resource
def load_piper_assets():
    """Download the Piper voice model and config from Hugging Face."""
    model_path = hf_hub_download(repo_id=PIPER_REPO_ID, filename=PIPER_MODEL_FILE)
    config_path = hf_hub_download(repo_id=PIPER_REPO_ID, filename=PIPER_CONFIG_FILE)
    voice = PiperVoice.load(model_path, config_path)
    return voice


def get_text():
    """Convert speech to text using the fine-tuned Urdu Whisper model."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        temp_file.write(st.session_state.audio.read())
        file_path = temp_file.name

    try:
        audio_array, sample_rate = sf.read(file_path)

        if audio_array.ndim > 1:
            audio_array = audio_array.mean(axis=1)

        audio_array = audio_array.astype(np.float32)

        if sample_rate != 16000:
            waveform = torch.from_numpy(audio_array).unsqueeze(0).unsqueeze(0)
            target_length = int(audio_array.shape[0] * 16000 / sample_rate)
            audio_array = torch.nn.functional.interpolate(
                waveform,
                size=target_length,
                mode="linear",
                align_corners=False,
            ).squeeze().numpy()
            sample_rate = 16000

        processor, model, device = load_whisper_assets()
        inputs = processor(
            audio_array,
            sampling_rate=sample_rate,
            return_tensors="pt",
            return_attention_mask=True,
        )
        input_features = inputs.input_features.to(device)
        attention_mask = inputs.get("attention_mask")
        if attention_mask is not None:
            attention_mask = attention_mask.to(device)

        with torch.no_grad():
            generate_kwargs = {"input_features": input_features}
            if attention_mask is not None:
                generate_kwargs["attention_mask"] = attention_mask
            generated_ids = model.generate(**generate_kwargs)

        transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
        if not transcription:
            raise ValueError("Whisper model returned an empty transcription.")

        st.session_state.prompt = transcription
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
    """Convert text response to speech using Piper Urdu voice."""
    if not st.session_state.text_response:
        return

    voice = load_piper_assets()
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name

    try:
        with wave.open(output_path, "wb") as wav_file:
            voice.synthesize_wav(st.session_state.text_response, wav_file)

        with open(output_path, "rb") as audio_file:
            st.audio(audio_file.read(), format="audio/wav")

        st.write(f"🎤 **بوٹ کا جواب:** {st.session_state.text_response}")
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)


if __name__ == "__main__":
    main()
