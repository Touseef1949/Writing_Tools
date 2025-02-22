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

# Initialize the Groq client
print(f"GROQ_API_KEY: {api_key}")  # Debugging purpose


def rephrase(instruction, user_message):
    if user_message:
        rephrases = []
        prompt = f'Check the following sentence for grammar and clarity: "{user_message}". {instruction}'
        progress_bar = st.progress(0)
        for i in range(3):
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}]
            )
            rephrases.append(response.choices[0].message.content)
            progress_bar.progress((i + 1) / 3)
        return rephrases
    return []

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
        if st.button('Make Formal'):
            rephrases = rephrase('Rewrite this sentence to make it sound more professional and formal. Use appropriate vocabulary and a respectful tone, while keeping the original message intact.', user_input)

end_time = time.time()
elapsed_time = end_time - start_time

if rephrases:
    st.write("Rephrased Texts:")
    for i, rephrase in enumerate(rephrases, 1):
        st.write(f"{i}. {rephrase}")
    st.write(f"Overall response time: {elapsed_time:.2f} seconds")
