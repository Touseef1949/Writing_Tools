import streamlit as st
import groq
import time
import dotenv
import os
from PIL import Image
import requests

dotenv.load_dotenv()

# Initialize the Groq client
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY is missing. Make sure it's set in your .env file.")
client = groq.Client(api_key=api_key)


def rephrase(instruction, user_message):
    if user_message:
        rephrases = []
        prompt = f'Check the following sentence for grammar and clarity: "{user_message}". {instruction}'
        progress_bar = st.progress(0)
        for i in range(3):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            rephrases.append(response.choices[0].message.content)
            progress_bar.progress((i + 1) / 3)
        return rephrases
    return []

def generate_response(instruction, user_message):
    if user_message:
        prompt = f'{instruction} "{user_message}"'
        progress_bar = st.progress(0)
        for i in range(1):  # Reduced iterations for faster response
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            progress_bar.progress(1)
            return response.choices[0].message.content
    return ""


# Image URLs
logo_url = "https://www.groq.com/wp-content/uploads/2024/04/groq-logo-dark.svg"  # Replace with your logo URL
background_image_url = "https://images.unsplash.com/photo-1618032786529-69999a76999f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Y29tcHV0ZXJ8ZW58MHx8MHx8fDA%3D&w=1000&q=80"  # Replace with your background image URL

# CSS Styling
st.markdown(
    """
    <style>
    body {
        background-image: url('{background_image_url}'); /* Replace with your background image URL */
        background-size: cover;
        background-repeat: no-repeat;
        color: #fff;
        font-family: 'Arial', sans-serif;
    }
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.8);
        border: 1px solid #ccc;
        padding: 10px;
        border-radius: 5px;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #3e8e41;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar for options
with st.sidebar:
    try:
        response = requests.get(logo_url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        logo_image = Image.open(response.raw)
        st.image(logo_image, width=150)
    except requests.exceptions.RequestException as e:
        st.error(f"Error loading logo: {e}")

    st.header("Navigation")
    option = st.selectbox(
        "Choose a tool:",
        ("Writing Tools", "Chat with AI"),
        format_func=lambda x: f"<span style='color: #4CAF50;'>{x}</span>",  # Style the options
    )

# Main content based on selected option
if option == "Writing Tools":
    st.title('✨ Unleash Your Inner Writer ✨')
    st.write("Transform your text with our powerful writing tools.")

    user_input = st.text_area("📝 Enter your text here:", height=200)

    col1, col2, col3, col4, col5 = st.columns(5)

    rephrases = []

    start_time = time.time()

    with st.spinner('🪄 Processing...'):
        with col1:
            if st.button('✍️ Rephrase', use_container_width=True):
                rephrases = rephrase('Rewrite this text for better readability while maintaining its original meaning. Focus on improving sentence structure and clarity.', user_input)

        with col2:
            if st.button('😎 Make Gen Z', use_container_width=True):
                rephrases = rephrase('Rewrite this text to make it more appealing and relatable to a younger, millennial or Gen Z audience. Use contemporary language, slang, and references that resonate with this demographic, while keeping the original message intact.', user_input)

        with col3:
            if st.button('📧 Write Email', use_container_width=True):
                rephrases = rephrase('Create an email to make it sound more professional and formal. Ensure the tone is respectful and the language is polished, while keeping the original message intact.', user_input)

        with col4:
            if st.button('✂️ Make Concise', use_container_width=True):
                rephrases = rephrase('Rewrite this section to make it more concise. Remove any unnecessary words and redundant phrases, while keeping the original message intact.', user_input)

        with col5:
            if st.button('✅ Grammar Check', use_container_width=True):
                rephrases = rephrase('Identify any grammatical errors, suggest corrections, and explain the reasoning behind the changes.  Maintain the original meaning of the sentence.', user_input)

    end_time = time.time()
    elapsed_time = end_time - start_time

    if rephrases:
        st.write("✨ Rephrased Texts:")
        for i, rephrase in enumerate(rephrases, 1):
            st.write(f"{i}. {rephrase}")
        st.write(f"⏱️ Overall response time: {elapsed_time:.2f} seconds")

elif option == "Chat with AI":
    st.title('💬 Chat with the AI 🤖')
    st.write("Ask anything and get intelligent responses.")

    user_input = st.text_area("💬 Enter your message here:", height=200)
    chat_instruction = st.text_input("💡 Enter your instruction (e.g., 'Summarize this', 'Translate to French'):")

    start_time = time.time()

    if st.button("🚀 Send", use_container_width=True):
        with st.spinner('🪄 Processing...'):
            if chat_instruction:
                response = generate_response(chat_instruction, user_input)
                st.write("🤖 Response:")
                st.write(response)
            else:
                st.warning("⚠️ Please enter an instruction in the text box above.")

    end_time = time.time()
    elapsed_time = end_time - start_time

    st.write(f"⏱️ Response time: {elapsed_time:.2f} seconds")
