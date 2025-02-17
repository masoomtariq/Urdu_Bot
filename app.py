import streamlit as st
import speech_recognition as sr
import tempfile
from groq import Groq
from streamlit_chat import message
from gtts import gTTS
import os

def main():

    st.title("Urdu Voice Chatbot")
        
    st.sidebar.title('''About this App''')
    st.sidebar.info(f'''This a Urdu voice chatbot created using Streamlit. It takes in Urdu voice input and response in Urdu voice''')

    st.sidebar.write("")  # Adds one line of space
    st.sidebar.write("")  # Adds one line of space

    st.sidebar.write("Developed by :blue[Masoom Tariq]")

    initailize_state()

    st.session_state.audio = st.audio_input("Enter Input")

    if st.session_state.audio:
        
        get_text()
    
        generate_response()

        play_audio()

    if st.button("clear_chat"):
        st.session_state.clear()
        #st.rerun()

        

    with st.expander("See Text"):
        message(st.session_state.text_response, key=str())
    

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

def get_text():
    
    with tempfile.NamedTemporaryFile(delete=True, suffix='.wav') as temp_file:
        temp_file.write(st.session_state.audio.read())
        file_path = temp_file.name

        with sr.AudioFile(file_path) as source:
            r = sr.Recognizer()
            recorded = r.record(source)
            try:
                st.session_state.prompt = r.recognize_google(audio_data = recorded, language='ur')
                st.session_state.user_audio.append(st.session_state.audio)
            except sr.UnknownValueError:
                text = "آپ کی آواز واضح نہیں ہے - براہ کرم دوبارہ کوشش کریں۔"
                play_exception(text)


def generate_response():
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    #st.session_state.history.append({"role": "assistant", "content": "ہیلو! آج میں آپ کی مدد کیسے کر سکتا ہوں؟"})
    st.session_state.history.append({"role": "user", "content": st.session_state.prompt})
    chat = client.chat.completions.create(model="llama-3.3-70b-versatile",
                                        messages = st.session_state.history,
                                        temperature=0,
                                        max_completion_tokens=1024,
                                        top_p=0,
                                        stop=None)
    st.session_state.comp_time = chat.usage.completion_time
    st.session_state.text_response = chat.choices[0].message.content
    st.session_state.history.append({"role": "assistant", "content": st.session_state.text_response})
    
def play_audio():
    ai_audio = gTTS(text=st.session_state.text_response, lang = 'ur')
    with tempfile.NamedTemporaryFile(delete=True, suffix='.wav') as audio_file:
        ai_audio.save(audio_file.name)
        audio_file.name

        st.session_state.ai_audio.append(audio_file.name)
        st.audio(audio_file.name)

def play_exception(text):
    ai_audio = gTTS(text=text, lang = 'ur')
    with tempfile.NamedTemporaryFile(delete=True, suffix='.wav') as audio_file:
        ai_audio.save(audio_file.name)

        st.audio(audio_file.name)

if __name__ == "__main__":
    main()