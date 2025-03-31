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
    pattern = r"<think>.*?</think>|<thought>.*?</thought>"
    cleaned_text = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)
    return cleaned_text.strip()
# --- End Helper Function ---


def rephrase(instruction, user_message):
    if user_message:
        rephrases = []
        prompt = f'Check the following sentence for grammar and clarity: "{user_message}". {instruction}'
        progress_bar = st.progress(0)
        try:
            for i in range(1): # Looping once seems intended
                response = client.chat.completions.create(
                    model="qwen-qwq-32b",
                    messages=[{"role": "user", "content": prompt}]
                )
                raw_content = response.choices[0].message.content
                cleaned_content = remove_think_tags(raw_content)
                rephrases.append(cleaned_content)
                progress_bar.progress((i + 1) / 1)
            return rephrases
        except Exception as e:
            st.error(f"Error during rephrasing API call: {e}")
            return [] # Return empty list on error
        finally:
            # Ensure progress bar is cleared or set to complete
            # Using empty() might be better if you want it gone
            progress_bar.progress(1.0) # Show completion
            time.sleep(0.1) # Brief pause
            progress_bar.empty() # Remove the progress bar

    return []

def generate_response(instruction, user_message):
    if user_message:
        prompt = f'{instruction} "{user_message}"'
        progress_bar = st.progress(0)
        try:
            for i in range(1):  # Reduced iterations for faster response
                response = client.chat.completions.create(
                    model="deepseek-r1-distill-llama-70b",
                    messages=[{"role": "user", "content": prompt}]
                )
                raw_content = response.choices[0].message.content
                cleaned_content = remove_think_tags(raw_content)
                progress_bar.progress(1)
                return cleaned_content
        except Exception as e:
            st.error(f"Error during generation API call: {e}")
            return "" # Return empty string on error
        finally:
             # Ensure progress bar is cleared or set to complete
            progress_bar.progress(1.0) # Show completion
            time.sleep(0.1) # Brief pause
            progress_bar.empty() # Remove the progress bar
    return ""


# Sidebar for options
with st.sidebar:
    # st.image("logo.png", width=50)  # Optional: Add a logo
    st.header("Navigation")
    option = st.selectbox(
        "Choose an option:",
        ("Writing Tools", "Chat with AI"),
        label_visibility="collapsed" # Hide the label if the header is enough
    )
    st.markdown("---")
    st.caption("Powered by Groq & Streamlit")


# Main content based on selected option
if option == "Writing Tools":
    st.title('✍️ Writing Tools')
    st.markdown("Enhance your text with various writing assistance tools.")

    user_input = st.text_area("Enter your text here:", height=150, placeholder="Paste or type your text...")

    col1, col2, col3, col4, col5 = st.columns(5)

    # Initialize rephrases outside the button checks
    rephrases_output = []
    processed = False # Flag to check if any button was pressed
    action_taken = None # Keep track of which button was pressed

    # Store button results
    rephrase_clicked = col1.button('✨ Rephrase', help="Improve readability and clarity.")
    genz_clicked = col2.button('😎 Make Gen Z', help="Adapt text for a younger audience.")
    email_clicked = col3.button('👔 Write Email', help="Formalize text into a professional email.")
    concise_clicked = col4.button('✂️ Make Concise', help="Shorten text while keeping the core message.")
    grammar_clicked = col5.button('🧐 Grammar', help="Check and correct grammar.")

    start_time = time.time() # Start timer before potential processing

    # Determine which button was clicked
    if rephrase_clicked: action_taken = "Rephrase"
    elif genz_clicked: action_taken = "Make Gen Z"
    elif email_clicked: action_taken = "Write Email"
    elif concise_clicked: action_taken = "Make Concise"
    elif grammar_clicked: action_taken = "Grammar"

    # Process only if input exists and a button was clicked
    if user_input and action_taken:
        processed = True
        instruction = ""
        if action_taken == "Rephrase":
            instruction = 'Rewrite this text for better readability while maintaining its original meaning. Focus on improving sentence structure and clarity.'
        elif action_taken == "Make Gen Z":
            instruction = 'Rewrite this text to make it more appealing and relatable to a younger, millennial or Gen Z audience. Use contemporary language, slang, and references that resonate with this demographic, while keeping the original message intact.'
        elif action_taken == "Write Email":
            instruction = 'Create an email to make it sound more professional and formal. Ensure the tone is respectful and the language is polished, while keeping the original message intact.'
        elif action_taken == "Make Concise":
            instruction = 'Rewrite this section to make it more concise. Remove any unnecessary words and redundant phrases, while keeping the original message intact.'
        elif action_taken == "Grammar":
            instruction = 'Identify any grammatical errors, suggest corrections, and explain the reasoning behind the changes. Maintain the original meaning of the sentence.'

        with st.spinner(f'Processing: {action_taken}...'):
            rephrases_output = rephrase(instruction, user_input)

    end_time = time.time() # End timer after potential processing
    elapsed_time = end_time - start_time

    # Display results only if processed and output exists
    if processed:
        if rephrases_output:
            st.write("---") # Separator
            st.subheader(f"Result ({action_taken}):") # Show which action produced the result
            # --- CHANGE HERE: Use st.write instead of st.text_area ---
            for i, text in enumerate(rephrases_output, 1):
                 # Using Markdown for potential formatting and a divider
                 st.markdown(f"**Suggestion {i}:**")
                 st.write(text)
                 if len(rephrases_output) > 1 and i < len(rephrases_output):
                     st.markdown("---") # Divider between multiple suggestions if any
            # --- End Change ---
            st.info(f"Processing time: {elapsed_time:.2f} seconds")
        elif user_input: # Check if input was provided but processing failed or returned empty
             st.warning("Processing finished, but no output was generated. Please check for errors above or try again.")
        # else: # No user input case is handled implicitly

elif option == "Chat with AI":
    st.title('💬 Chat with AI')
    st.markdown("Interact with the AI using custom instructions.")

    user_input = st.text_area("Enter your text here:", height=150, placeholder="Provide the text you want the AI to work with...")
    chat_instruction = st.text_input("Enter your instruction:", placeholder="e.g., 'Rewrite for clarity', 'Make it sound professional', 'Summarize this'")

    response_output = None
    processed = False

    if st.button("🚀 Send", help="Send your text and instruction to the AI"):
        processed = True
        start_time = time.time() # Start timer when button is clicked
        if user_input and chat_instruction:
            with st.spinner('Communicating with AI...'):
                response_output = generate_response(chat_instruction, user_input)
        elif not user_input:
             st.warning("⚠️ Please enter some text to process.")
        else: # No instruction
            st.warning("⚠️ Please enter an instruction in the text box above.")
        end_time = time.time() # End timer after processing
        elapsed_time = end_time - start_time

    # Display results only if processed
    if processed:
        if response_output:
            st.write("---") # Separator
            st.subheader("🤖 AI Response:")
            # --- CHANGE HERE: Use st.write instead of st.text_area ---
            st.write(response_output)
            # --- End Change ---
            st.info(f"Response time: {elapsed_time:.2f} seconds")
        # Warnings for missing input are handled above
