import json
import streamlit as st
import google.generativeai as genai
import time
import random
import os
import PyPDF2 as pdf

# Set the page config
st.set_page_config(
    page_title="Interview Chat Bot",
)

st.title("Interview Chat Bot")
st.caption("A Chatbot Powered by Google Gemini Pro")

# Set the API key
st.session_state.app_key = "AIzaSyDGNV6x59Bx7DJEEXdygmIBTLkwnixkNro"

# Initialize Google Gemini Pro
genai.configure(api_key=st.session_state.app_key)
model = genai.GenerativeModel("gemini-pro")

# Initialize or retrieve history
if "history" not in st.session_state:
    st.session_state.history = []

chat = model.start_chat(history=st.session_state.history)

# Interview instructions
inst = (
    "You are a professional interviewer, you will ask questions do not answer them,ask one question at a time and wait for the user to respond. Your goal is to elicit detailed information about the candidate's background. Start with a request for a concise self-introduction. Subsequently, inquire about the candidate's work experience, emphasizing notable projects and accomplishments. Discuss their skills and how they've applied them in past roles. Explore their educational history, including degrees and certifications. To maintain a structured approach, ensure you ask one question at a time. Following each response, provide constructive feedback on the answer provided. Importantly, incorporate technical questions aligned with the candidate's resume, focusing on specific expertise areas. Throughout the interview, uphold a professional tone to foster a thorough and insightful discussion."
)

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

        if not st.session_state.get("initial_message_sent", False):
            # Automatically send the initial message "Hello Sir" only if not sent before
            initial_prompt = "Hello Sir"
            with st.chat_message("user"):
                st.markdown(initial_prompt)
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Thinking...")
                try:
                    # Combine context and user input properly
                    input_text = json.dumps({'resume_text': resume_text, 'prompt': initial_prompt, 'instructions': inst})

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
                st.session_state.initial_message_sent = True  # Set the flag to True

        # Allow users to enter any prompt
        if prompt := st.chat_input(""):
            prompt = prompt.replace('\n', ' \n')
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Thinking...")
                try:
                    # Combine context and user input properly
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
