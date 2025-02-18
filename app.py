import streamlit as st
import speech_recognition as sr
import tempfile
from groq import Groq
from streamlit_chat import message
from gtts import gTTS
from dotenv import load_dotenv
import os

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")

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
            st.session_state.history.append({'role': 'user', 'content': "کچھ غیر واضح الفاظ"})
            st.session_state.text_response = "آپ کی آواز واضح نہیں ہے - براہ کرم دوبارہ کوشش کریں۔"
            st.session_state.history.append({'role': 'user', 'content': st.session_state.text_response})
        
        except sr.RequestError:
            st.session_state.history.append({'role': 'user', 'content': "کچھ الفاظ"})
            st.session_state.text_response = "معذرت، سسٹم کی سروس مصروف ہے، براہ کرم دوبارہ کوشش کریں۔"
            st.session_state.history.append({'role': 'user', 'content': st.session_state.text_response})

        finally:
            if st.session_state.text_response:
                play_audio()

    if st.sidebar.button("Clear Chat History"):
        st.session_state.clear()
        initailize_state()

        

    with st.expander("جواب دیکھیں"):
        st.success(st.session_state.text_response)
    

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
    
    st.session_state.history.append({'role': 'system', 'content': instructions})

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
    client = Groq(api_key=groq_key)
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
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as audio_file:
        ai_audio.save(audio_file.name)
        audio_file.name

    st.session_state.ai_audio.append(audio_file.name)
    st.audio(audio_file.name)

    audio_file.close()
    os.remove(audio_file.name)
if __name__ == "__main__":
    main()
