import streamlit as st
import speech_recognition as sr
import tempfile
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from gtts import gTTS
from dotenv import load_dotenv
import os
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
    st.title("Urdu Voice Chatbot")
        
    st.sidebar.title('''About this App''')
    st.sidebar.info(f'''This a Urdu voice chatbot created using Streamlit. It takes in Urdu voice input and response in Urdu voice''')

    st.sidebar.write("")
    st.sidebar.write("")

    st.sidebar.write("Developed by :blue[Masoom Tariq]")

    initialize_state()

    st.session_state.audio = st.audio_input("پوچھیے")

    if st.session_state.audio:
        try:
            get_text()
            generate_response()
            play_audio()
        
        except sr.UnknownValueError:
            st.session_state.history.append(HumanMessage(content="کچھ غیر واضح الفاظ"))
            st.session_state.text_response = "آپ کی آواز واضح نہیں ہے - براہ کرم دوبارہ کوشش کریں۔"
            st.session_state.history.append(AIMessage(content=st.session_state.text_response))
            st.error(st.session_state.text_response)
        
        except sr.RequestError:
            st.session_state.history.append(HumanMessage(content="کچھ الفاظ"))
            st.session_state.text_response = "معذرت، سسٹم کی سروس مصروف ہے، براہ کرم دوبارہ کوشش کریں۔"
            st.session_state.history.append(AIMessage(content=st.session_state.text_response))
            st.error(st.session_state.text_response)
        
        except ChatGoogleGenerativeAIError as e:
            st.session_state.text_response = "معذرت، AI سروس میں خرابی ہے۔ براہ کرم دوبارہ کوشش کریں۔"
            st.error(st.session_state.text_response)
            st.warning("براہ کرم بعد میں دوبارہ کوشش کریں")
        
        except Exception as e:
            st.session_state.text_response = "ایک غیر متوقع خرابی واقع ہوئی۔"
            st.error(st.session_state.text_response)

    if st.sidebar.button("Clear Chat History"):
        st.session_state.clear()
        initialize_state()

    if st.session_state.text_response:
        with st.expander("جواب دیکھیں"):
            st.write(st.session_state.text_response)
    

def initialize_state():
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
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        temp_file.write(st.session_state.audio.read())
        file_path = temp_file.name

    try:
        with sr.AudioFile(file_path) as source:
            r = sr.Recognizer()
            recorded = r.record(source)
            st.session_state.prompt = r.recognize_google(audio_data=recorded, language='ur')
    finally:
        os.remove(file_path)

def generate_response():
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, api_key=google_key)
    st.session_state.history.append(HumanMessage(content=st.session_state.prompt))
    
    response = llm.invoke(st.session_state.history)
    st.session_state.text_response = response.content
    st.session_state.history.append(AIMessage(content=response.content))
  
def play_audio():
    if not st.session_state.text_response:
        return
        
    ai_audio = gTTS(text=st.session_state.text_response, lang='ur')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as audio_file:
        ai_audio.save(audio_file.name)
        file_path = audio_file.name
    
    try:
        st.audio(file_path)
    finally:
        os.remove(file_path)

if __name__ == "__main__":
    main()
