import streamlit as st
import google.generativeai as genai
import time
import random
import PyPDF2 as pdf
import pyttsx3
import speech_recognition as sr
from gtts import gTTS
import playsound
import json

# Set the page config
st.set_page_config(page_title="Interview chat bot")

st.title("Interview Chat Bot")
st.caption("A Chatbot Powered by Google Gemini Pro")

# Set the API key
st.session_state.app_key = "AIzaSyDGNV6x59Bx7DJEEXdygmIBTLkwnixkNro"

# Initialize Google Gemini Pro
genai.configure(api_key=st.session_state.app_key)
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=st.session_state.get("history", []))

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize speech recognition
recognizer = sr.Recognizer()

# Interview instructions
inst = "You are a professional interviewer and you will ask questions in a professional manner. Start with the introduction of the candidate.You will ask questions about the candidate's experience, skills, and other relevant information. You will also ask questions about the candidate's previous work experience, education, and other relevant details.  Ask question one at a time. You are an interviewer, you will ask questions and do not answer them. Also ask technical question related to the candidate's profile"

# Sidebar content
with st.sidebar:
    if st.button("Clear Chat Window", use_container_width=True, type="primary"):
        st.session_state.history = []  # Clear the chat history without rerunning the script

    st.subheader("Connect with Shivansh:")
    st.write("[LinkedIn](https://linkedin.com/in/shivanshtri010)", "[GitHub](https://github.com/shivanshtri010)", "[Instagram](https://www.instagram.com/shivanshtripathi010/)")

# Main content
if "app_key" in st.session_state:
    uploaded_file = st.file_uploader("Upload PDF Resume", type="pdf", help="Please upload the candidate's PDF resume")

    if uploaded_file:
        resume_text = ""
        try:
            reader = pdf.PdfReader(uploaded_file)
            for page in range(len(reader.pages)):
                resume_text += reader.pages[page].extract_text()
        except Exception as e:
            st.exception(f"Error extracting text from PDF: {e}")

        # Start chatbot logic
        chat_started = st.session_state.get("chat_started", False)
        if not chat_started:
            st.session_state.history = []  # Reset chat history if chat not started yet
            chat_started = True
            st.session_state.chat_started = chat_started

            # Initialize Google Gemini Pro
            model = genai.GenerativeModel("gemini-pro")
            chat = model.start_chat(history=st.session_state.history)

        if st.button("Speak"):
            with st.spinner("Listening..."):
                st.write("Speak now...")
                with sr.Microphone() as source:
                    audio = recognizer.listen(source)
                st.success("Processing...")

            try:
                # Convert speech to text
                user_input = recognizer.recognize_google(audio)
                with st.chat_message("user"):
                    st.markdown(user_input)

                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    message_placeholder.markdown("Thinking...")

                    # Combine context, user input, and resume text
                    input_text = json.dumps({'resume_text': resume_text, 'prompt': user_input, 'instructions': inst})
                    full_response = ""
                    for chunk in chat.send_message(input_text, stream=True):
                        word_count = 0
                        random_int = random.randint(5, 10)
                        for word in chunk.text:
                            full_response += word
                            word_count += 1
                            if word_count == random_int:
                                time.sleep(0.05)
                                message_placeholder.markdown(full_response + "_")
                                word_count = 0
                                random_int = random.randint(5, 10)
                    message_placeholder.markdown(full_response)

                    # Speak the response using gTTS
                    tts = gTTS(full_response, lang="en")
                    tts.save("response.mp3")
                    playsound.playsound("response.mp3")

            except sr.UnknownValueError:
                st.warning("Sorry, I couldn't understand what you said.")
            except sr.RequestError as e:
                st.error(f"Speech Recognition request failed: {e}")

            st.session_state.history.extend(chat.history)  # Preserve chat history
