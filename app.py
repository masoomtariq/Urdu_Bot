import streamlit as st
import speech_recognition as sr
import tempfile
from groq import Groq
from langchain_google_genai import ChatGoogleGenerativeAI
from streamlit_chat import message
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from gtts import gTTS
from dotenv import load_dotenv
import os

load_dotenv()

#Langsmith tracking
LANGCHAIN_PROJECT = "Urdu Bot"
LANGSMITH_TRACING='true'
LANGSMITH_ENDPOINT = 'https://api.smith.langchain.com'
os.environ["LANGSMITH_API_KEY"] = os.getenv["LANGSMITH_API_KEY"]

##groq_key = os.getenv("GROQ_API_KEY")
google_key = st.secrets["GOOGLE_API_KEY"]

def main():

    st.title("Urdu Voice Chatbot")
        
    st.sidebar.title('''About this App''')
    st.sidebar.info(f'''This a Urdu voice chatbot created using Streamlit. It takes in Urdu voice input and response in Urdu voice''')

    st.sidebar.write("")  # Adds one line of space
    st.sidebar.write("")  # Adds one line of space

    st.sidebar.write("Developed by :blue[Masoom Tariq]")

    initailize_state()

    st.session_state.audio = st.audio_input("پوچھیے")

    if st.session_state.audio:

        try:
            
            get_text()
        
            generate_response()

        except sr.UnknownValueError:
            st.session_state.history.append(HumanMessage(content = "کچھ غیر واضح الفاظ"))
            st.session_state.text_response = "آپ کی آواز واضح نہیں ہے - براہ کرم دوبارہ کوشش کریں۔"
            st.session_state.history.append(AIMessage(content=st.session_state.text_response))
        
        except sr.RequestError:
            st.session_state.history.append(HumanMessage(content= "کچھ الفاظ"))
            st.session_state.text_response = "معذرت، سسٹم کی سروس مصروف ہے، براہ کرم دوبارہ کوشش کریں۔"
            st.session_state.history.append(AIMessage(content=st.session_state.text_response))

        finally:
            play_audio()

    if st.sidebar.button("Clear Chat History"):
        st.session_state.clear()
        initailize_state()

        

    with st.expander("جواب دیکھیں"):
        st.success(message(st.session_state.text_response))
    

def initailize_state():
    # Define initial states and assign values
    initialStates = {
        'text_response': '',
        'user_audio': [],
        'ai_audio': [],
        'history': [],
        'prompt': '',
        'comp_time': '',
        'audio': ''
    }
    for key, value in initialStates.items():
        if key not in st.session_state:
            st.session_state[key] = value
    instructions = "آپ ایک مددگار اے آئی اسسٹنٹ ہیں۔ آپ ہر وہ کام کر سکتے ہیں جو مناسب ہو لیکن آپ صرف اردو زبان جانتے ہیں اور ہمیشہ صرف اردو زبان میں جواب دیتے ہیں۔"
    
    #st.session_state.history.append(SystemMessage(content= instructions))

def get_text():
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        temp_file.write(st.session_state.audio.read())
        file_path = temp_file.name

    with sr.AudioFile(file_path) as source:
        r = sr.Recognizer()
        recorded = r.record(source)
        
        st.session_state.prompt = r.recognize_google(audio_data = recorded, language='ur')
        st.session_state.user_audio.append(st.session_state.audio)
    temp_file.close()
    os.remove(file_path)


def generate_response():
    #client = Groq(api_key=groq_key)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-pro-exp-02-05", temperature=0, api_key=google_key)
    #st.session_state.history.append({"role": "assistant", "content": "ہیلو! آج میں آپ کی مدد کیسے کر سکتا ہوں؟"})
    st.session_state.history.append(HumanMessage(content=st.session_state.prompt))
    
    response = llm.invoke(st.session_state.history)

    #st.session_state.comp_time = chat.usage.completion_time
    st.session_state.text_response = response.content
    st.session_state.history.append(AIMessage(content=response.content))
  
def play_audio():
    ai_audio = gTTS(text=st.session_state.text_response, lang = 'ur')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as audio_file:
        ai_audio.save(audio_file.name)
        audio_file.name

    st.session_state.ai_audio.append(audio_file.name)
    st.audio(audio_file.name)

    audio_file.close()
    os.remove(audio_file.name)

if __name__ == "__main__":
    main()
