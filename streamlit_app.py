import streamlit as st
import groq
import time
import dotenv
import os
import re # <-- Import the regex module

dotenv.load_dotenv()

# Initialize the Groq client
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY is missing. Make sure it's set in your .env file.")
    st.stop() # Stop execution if API key is missing
# Add basic error handling for client initialization
try:
    client = groq.Client(api_key=api_key)
except Exception as e:
    st.error(f"Failed to initialize Groq client: {e}")
    st.stop()

# --- Helper Function to Remove Tags ---
def remove_think_tags(text):
    """Removes <think>...</think> blocks using regex."""
    # This pattern looks for <think>, then matches any character (.*?)
    # non-greedily until it finds </think>.
    # re.DOTALL makes '.' match newlines as well, handling multi-line tags.
    # We also add variations like <thought>
    pattern = r"<think>.*?</think>|<thought>.*?</thought>"
    # Replace found patterns with an empty string
    cleaned_text = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)
    # You might want to trim leading/trailing whitespace that could be left
    return cleaned_text.strip()
# --- End Helper Function ---


def rephrase(instruction, user_message):
    if user_message:
        rephrases = []
        # Consider adding instruction to model not to use tags (less reliable)
        # instruction += "\n\nImportant: Do not include any reasoning or thought process within <think> or similar tags in your final output."
        prompt = f'Check the following sentence for grammar and clarity: "{user_message}". {instruction}'
        progress_bar = st.progress(0)
        try:
            for i in range(1): # Looping once seems intended
                response = client.chat.completions.create(
                    model="qwen-qwq-32b",
                    messages=[{"role": "user", "content": prompt}]
                )
                raw_content = response.choices[0].message.content
                # --- Clean the response ---
                cleaned_content = remove_think_tags(raw_content)
                # --- End Cleaning ---
                rephrases.append(cleaned_content)
                progress_bar.progress((i + 1) / 1)
            return rephrases
        except Exception as e:
            st.error(f"Error during rephrasing API call: {e}")
            return [] # Return empty list on error
        finally:
            progress_bar.empty() # Clear the progress bar
    return []

def generate_response(instruction, user_message):
    if user_message:
        # Consider adding instruction to model not to use tags (less reliable)
        # instruction += "\n\nImportant: Do not include any reasoning or thought process within <think> or similar tags in your final output."
        prompt = f'{instruction} "{user_message}"'
        progress_bar = st.progress(0)
        try:
            for i in range(1):  # Reduced iterations for faster response
                response = client.chat.completions.create(
                    model="deepseek-r1-distill-llama-70b",
                    messages=[{"role": "user", "content": prompt}]
                )
                raw_content = response.choices[0].message.content
                # --- Clean the response ---
                cleaned_content = remove_think_tags(raw_content)
                # --- End Cleaning ---
                progress_bar.progress(1)
                return cleaned_content
        except Exception as e:
            st.error(f"Error during generation API call: {e}")
            return "" # Return empty string on error
        finally:
            progress_bar.empty() # Clear the progress bar
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

    user_input = st.text_area("Enter your text here:", height=150) # Adjusted height

    col1, col2, col3, col4, col5 = st.columns(5)

    # Initialize rephrases outside the button checks
    rephrases_output = []
    processed = False # Flag to check if any button was pressed

    # Store button results
    rephrase_clicked = col1.button('Rephrase')
    genz_clicked = col2.button('Make Gen Z')
    email_clicked = col3.button('Write Email')
    concise_clicked = col4.button('Make Concise')
    grammar_clicked = col5.button('Grammar')

    start_time = time.time() # Start timer before potential processing

    # Process only if input exists and a button was clicked
    if user_input and (rephrase_clicked or genz_clicked or email_clicked or concise_clicked or grammar_clicked):
        processed = True
        with st.spinner('Processing...'):
            if rephrase_clicked:
                rephrases_output = rephrase('Rewrite this text for better readability while maintaining its original meaning. Focus on improving sentence structure and clarity.', user_input)
            elif genz_clicked:
                rephrases_output = rephrase('Rewrite this text to make it more appealing and relatable to a younger, millennial or Gen Z audience. Use contemporary language, slang, and references that resonate with this demographic, while keeping the original message intact.', user_input)
            elif email_clicked:
                rephrases_output = rephrase('Create an email to make it sound more professional and formal. Ensure the tone is respectful and the language is polished, while keeping the original message intact.', user_input)
            elif concise_clicked:
                rephrases_output = rephrase('Rewrite this section to make it more concise. Remove any unnecessary words and redundant phrases, while keeping the original message intact.', user_input)
            elif grammar_clicked:
                rephrases_output = rephrase('Identify any grammatical errors, suggest corrections, and explain the reasoning behind the changes.  Maintain the original meaning of the sentence.', user_input)

    end_time = time.time() # End timer after potential processing
    elapsed_time = end_time - start_time

    # Display results only if processed and output exists
    if processed:
        if rephrases_output:
            st.write("---") # Separator
            st.subheader("Results:")
            # Display results more clearly
            for i, text in enumerate(rephrases_output, 1):
                 st.text_area(f"Result {i}", text, height=100, key=f"rephrase_{i}") # Use text_area for consistency
            st.info(f"Processing time: {elapsed_time:.2f} seconds")
        elif user_input: # Check if input was provided but processing failed or returned empty
             st.warning("Processing finished, but no output was generated. Please check for errors above or try again.")
        # else: # No user input case is handled implicitly by not showing results

elif option == "Chat with AI":
    st.title('Chat with AI')

    user_input = st.text_area("Enter your text here:", height=150)
    chat_instruction = st.text_input("Enter your instruction (e.g., 'Rewrite for clarity', 'Make it sound professional', 'Summarize this'):")

    response_output = None
    processed = False

    if st.button("Send"):
        processed = True
        start_time = time.time() # Start timer when button is clicked
        if user_input and chat_instruction:
            with st.spinner('Processing...'):
                response_output = generate_response(chat_instruction, user_input)
        elif not user_input:
             st.warning("Please enter some text to process.")
        else: # No instruction
            st.warning("Please enter an instruction in the text box above.")
        end_time = time.time() # End timer after processing
        elapsed_time = end_time - start_time

    # Display results only if processed
    if processed:
        if response_output:
            st.write("---") # Separator
            st.subheader("Response:")
            st.text_area("AI Response", response_output, height=200) # Display in a text area
            st.info(f"Processing time: {elapsed_time:.2f} seconds")
        # Warnings for missing input are handled above
