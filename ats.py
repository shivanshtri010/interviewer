import streamlit as st
import google.generativeai as genai
import time
import random
import PyPDF2 as pdf
import pyttsx3
from gtts import gTTS
import playsound
import json
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
import socketserver

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

# Interview instructions
inst = "You are a professional interviewer and you will ask questions in a professional manner. Start with the introduction of the candidate. You will ask questions about the candidate's experience, skills, and other relevant information. You will also ask questions about the candidate's previous work experience, education, and other relevant details. Ask one question at a time. You are an interviewer; you will ask questions and do not answer them. Also, ask technical questions related to the candidate's profile."

# Record function
def record_audio(filename='recorded_audio.wav', duration=5, sample_rate=44100):
    print(f"Recording... ({duration} seconds)")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2, dtype='int16')
    sd.wait()
    wav.write(filename, sample_rate, audio_data)

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
                record_audio('user_input.wav', duration=5)  # Adjust duration as needed
                st.success("Processing...")

            try:
                # Convert recorded speech to text
                with sr.AudioFile('user_input.wav') as source:
                    audio = recognizer.record(source)
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

# Microphone Access Example
if st.button("Microphone Access Example"):
    st.subheader("Microphone Access Example")
    st.markdown("Click the 'Start Recording' button to access the microphone.")
    
    st.components.v1.html("""
        <button id="startButton">Start Recording</button>
        <button id="stopButton" disabled>Stop Recording</button>
        <script>
            document.addEventListener('DOMContentLoaded', (event) => {
                const startButton = document.getElementById('startButton');
                const stopButton = document.getElementById('stopButton');

                let mediaRecorder;
                let audioChunks = [];

                const onSuccess = (stream) => {
                    mediaRecorder = new MediaRecorder(stream);

                    mediaRecorder.ondataavailable = (event) => {
                        if (event.data.size > 0) {
                            audioChunks.push(event.data);
                        }
                    };

                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const audioUrl = URL.createObjectURL(audioBlob);

                        // Do something with the recorded audio URL, such as sending it to the server or playing it
                        console.log('Recording stopped. Audio URL:', audioUrl);

                        // Reset
                        audioChunks = [];
                        startButton.disabled = false;
                        stopButton.disabled = true;
                    };
                };

                const onError = (error) => {
                    console.error('Error accessing microphone:', error);
                };

                startButton.addEventListener('click', async () => {
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        onSuccess(stream);

                        // Start recording
                        mediaRecorder.start();

                        startButton.disabled = true;
                        stopButton.disabled = false;
                    } catch (error) {
                        onError(error);
                    }
                });

                stopButton.addEventListener('click', () => {
                    // Stop recording
                    mediaRecorder.stop();
                });
            });
        </script>
    """)
