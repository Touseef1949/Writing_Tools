import streamlit as st
import groq
import time
import dotenv
import os

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
        for i in range(1):
            response = client.chat.completions.create(
                model="qwen-qwq-32b",
                messages=[{"role": "user", "content": prompt}]
            )
            rephrases.append(response.choices[0].message.content)
            progress_bar.progress((i + 1) / 1)
        return rephrases
    return []

def generate_response(instruction, user_message):
    if user_message:
        prompt = f'{instruction} "{user_message}"'
        progress_bar = st.progress(0)
        for i in range(1):  # Reduced iterations for faster response
            response = client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[{"role": "user", "content": prompt}]
            )
            progress_bar.progress(1)
            return response.choices[0].message.content
    return ""


# Sidebar for options
with st.sidebar:
    option = st.selectbox(
        "Choose an option:",
        ("Writing Tools", "Chat with AI")
    )

# Main content based on selected option
if option == "Writing Tools":
    st.title('Writing Tools')

    user_input = st.text_area("Enter your text here:")

    col1, col2, col3, col4, col5 = st.columns(5)

    rephrases = []

    start_time = time.time()

    with st.spinner('Processing...'):
        with col1:
            if st.button('Rephrase'):
                rephrases = rephrase('Rewrite this text for better readability while maintaining its original meaning. Focus on improving sentence structure and clarity.', user_input)

        with col2:
            if st.button('Make Gen Z'):
                rephrases = rephrase('Rewrite this text to make it more appealing and relatable to a younger, millennial or Gen Z audience. Use contemporary language, slang, and references that resonate with this demographic, while keeping the original message intact.', user_input)

        with col3:
            if st.button('Write Email'):
                rephrases = rephrase('Create an email to make it sound more professional and formal. Ensure the tone is respectful and the language is polished, while keeping the original message intact.', user_input)

        with col4:
            if st.button('Make Concise'):
                rephrases = rephrase('Rewrite this section to make it more concise. Remove any unnecessary words and redundant phrases, while keeping the original message intact.', user_input)

        with col5:
            if st.button('Grammar'):
                rephrases = rephrase('Identify any grammatical errors, suggest corrections, and explain the reasoning behind the changes.  Maintain the original meaning of the sentence.', user_input)

    end_time = time.time()
    elapsed_time = end_time - start_time

    if rephrases:
        st.write("Rephrased Texts:")
        for i, rephrase in enumerate(rephrases, 1):
            st.write(f"{i}. {rephrase}")
        st.write(f"Overall response time: {elapsed_time:.2f} seconds")

elif option == "Chat with AI":
    st.title('Chat with AI')

    user_input = st.text_area("Enter your text here:")
    chat_instruction = st.text_input("Enter your instruction (e.g., 'Rewrite for clarity', 'Make it sound professional', 'Summarize this'):")

    start_time = time.time()

    if st.button("Send"):
        with st.spinner('Processing...'):
            if chat_instruction:
                response = generate_response(chat_instruction, user_input)
                st.write("Response:")
                st.write(response)
            else:
                st.warning("Please enter an instruction in the text box above.")

    end_time = time.time()
    elapsed_time = end_time - start_time

    st.write(f"Response time: {elapsed_time:.2f} seconds")
