import json
import streamlit as st
import google.generativeai as genai
import time
import random
import os
import PyPDF2 as pdf

st.set_page_config(
    page_title="Interview chat bot",
)

st.title("Interview Chat Bot")
st.caption("A Chatbot Powered by Google Gemini Pro")

st.session_state.app_key = "AIzaSyDGNV6x59Bx7DJEEXdygmIBTLkwnixkNro"

if "history" not in st.session_state:
    st.session_state.history = []

genai.configure(api_key=st.session_state.app_key)

model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=st.session_state.history)

inst = "You are a professional interviewer and you will ask questions in a professional manner. You will ask questions about the candidate's experience, skills, and other relevant information. You will also ask questions about the candidate's previous work experience, education, and other relevant details. Start with the introduction of the candidate. Ask question one at a time. You are an interviewer, you will ask questions and do not answer them."

with st.sidebar:
    if st.button("Clear Chat Window", use_container_width=True, type="primary"):
        st.session_state.history = []  # Clear the chat history without rerunning the script

    st.subheader("Connect with Shivansh:")
    st.write("[LinkedIn | ](https://linkedin.com/in/shivanshtri010)", "[ GitHub](https://github.com/shivanshtri010)", "[ | Instagram](https://www.instagram.com/shivanshtripathi010/)")

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

        if prompt := st.chat_input(""):
            prompt = prompt.replace('\n', ' \n')
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Thinking...")
                try:
                    # Combine context, user input, and resume text
                    input_text = json.dumps({'resume_text': resume_text, 'prompt': prompt, 'instructions': inst})
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
                except genai.types.generation_types.BlockedPromptException as e:
                    st.exception(e)
                except Exception as e:
                    st.exception(e)
                st.session_state.history.extend(chat.history)  # Preserve chat history
