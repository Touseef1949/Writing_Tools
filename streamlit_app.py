import streamlit as st
import groq
import time
import dotenv
import os

dotenv.load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY is missing. Make sure it's set in your .env file.")
client = groq.Client(api_key=api_key)

def generate_text(instruction, user_message):
    """
    Generates text based on the given instruction.
    """
    if user_message:
        progress_bar = st.progress(0)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f'{instruction} "{user_message}"'}]
        )
        progress_bar.progress(1)
        return response.choices[0].message.content
    return ""

st.title('Writing Tools')

user_input = st.text_area("Enter your text here:")

# Buttons in a single row
col1, col2, col3, col4, col5 = st.columns(5)
rephrased_texts = []

with st.spinner('Processing...'):
    if col1.button('Rephrase'):
        rephrased_texts.append(("Rephrased Version", generate_text(
            "Rewrite this text for better readability while maintaining its original meaning.", user_input
        )))

    if col2.button('Make Gen Z'):
        rephrased_texts.append(("Gen Z Version", generate_text(
            "Rewrite this text to make it sound more relatable and appealing to a Gen Z audience. Use informal and modern language.", user_input
        )))

    if col3.button('Write Email'):
        rephrased_texts.append(("Email Format", generate_text(
            "Convert this text into a professional and well-structured email.", user_input
        )))

    if col4.button('Make Concise'):
        rephrased_texts.append(("Concise Version", generate_text(
            "Rewrite this text in a more concise and direct way while keeping the core message.", user_input
        )))

    if col5.button('Grammar'):
        grammar_response = generate_text(
            "Check the grammar of this sentence, provide a corrected version, and explain the changes made.", user_input
        )
        if "Changes made:" in grammar_response:
            corrected_sentence, explanation = grammar_response.split("Changes made:", 1)
        else:
            corrected_sentence = grammar_response
            explanation = "No detailed explanation provided."

        rephrased_texts.append(("Grammar Correction", corrected_sentence.strip()))
        rephrased_texts.append(("Changes Made", explanation.strip()))

# Display all results in a common section
if rephrased_texts:
    st.write("### Rephrased Texts:")
    for title, text in rephrased_texts:
        st.write(f"**{title}:**")
        st.write(text)
        st.markdown("---")  # Adds a separator for better readability
