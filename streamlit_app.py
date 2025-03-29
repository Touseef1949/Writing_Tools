import streamlit as st
import groq
import time
import dotenv
import os
import re # Import regular expressions for parsing
from streamlit_copy_button import copy_button # Import the copy button component

dotenv.load_dotenv()

# Initialize the Groq client
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    # Attempt to get API key from Streamlit secrets if not in .env
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except KeyError:
        st.error("GROQ_API_KEY is missing. Set it in your .env file or Streamlit secrets.")
        st.stop() # Stop execution if no API key

# Check if api_key is still None or empty after trying secrets
if not api_key:
    st.error("GROQ_API_KEY is missing or empty. Please provide a valid API key.")
    st.stop()

# It's good practice to handle potential errors during client initialization
try:
    client = groq.Client(api_key=api_key)
    # Optional: Add a simple API call to verify the key works early on
    # client.models.list()
except Exception as e:
    st.error(f"Failed to initialize Groq client: {e}")
    st.stop()


# --- Function Definitions ---

def process_with_llm(instruction, user_message, num_responses=1):
    """Generic function to call the LLM and handle progress."""
    if not user_message:
        return [] if num_responses > 1 else ""

    responses = []
    prompt = f'{instruction} "{user_message}"'

    # Use a placeholder for the progress bar if num_responses > 1
    progress_bar_placeholder = st.empty()
    if num_responses > 1:
        progress_bar = progress_bar_placeholder.progress(0)
    else:
        progress_bar = None # No progress bar for single response

    try:
        for i in range(num_responses):
            response = client.chat.completions.create(
                model="llama3-70b-8192", # Use a specific, available model
                messages=[{"role": "user", "content": prompt}],
                # Optional: Add temperature, max_tokens etc. if needed
                # temperature=0.7,
                # max_tokens=1000,
            )
            responses.append(response.choices[0].message.content)
            if progress_bar:
                progress_bar.progress((i + 1) / num_responses)

        # Clear progress bar after completion
        progress_bar_placeholder.empty()

        return responses if num_responses > 1 else responses[0]

    except groq.APIError as e:
        st.error(f"Groq API Error: {e}")
        progress_bar_placeholder.empty() # Clear progress bar on error
        return [] if num_responses > 1 else ""
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        progress_bar_placeholder.empty() # Clear progress bar on error
        return [] if num_responses > 1 else ""


def extract_corrected_sentence(llm_response):
    """
    Attempts to extract the clearly marked corrected sentence from the LLM response.
    Searches for patterns like "Corrected Sentence:", "Suggested Correction:", etc.
    """
    # Define patterns to search for (case-insensitive)
    patterns = [
        r"Corrected Sentence:\s*(.*)",
        r"Suggested Correction:\s*(.*)",
        r"Corrected version:\s*(.*)",
        r"Here is the corrected sentence:\s*(.*)",
        # Add more patterns if needed based on observed LLM output
    ]

    for pattern in patterns:
        match = re.search(pattern, llm_response, re.IGNORECASE | re.DOTALL)
        if match:
            # Return the captured group (the sentence after the label), stripped of leading/trailing whitespace
            corrected = match.group(1).strip()
            # Sometimes the LLM might add quotes around it, remove them
            if corrected.startswith('"') and corrected.endswith('"'):
                corrected = corrected[1:-1]
            if corrected.startswith("'") and corrected.endswith("'"):
                corrected = corrected[1:-1]
            # Return the first match found
            return corrected

    # Fallback if no specific pattern is found:
    # Try to find the last paragraph or a sentence that looks like a standalone correction.
    # This is less reliable. A simple fallback is to return None.
    # Or you could return the entire response as the "correction" if no better candidate exists.
    # For now, let's return None to indicate failure to parse distinctly.
    return None

# --- Streamlit App Layout ---

st.set_page_config(layout="wide") # Use wider layout

# Sidebar for options
with st.sidebar:
    option = st.selectbox(
        "Choose an option:",
        ("Writing Tools", "Chat with AI")
    )

# --- Main Content ---

if option == "Writing Tools":
    st.title('✍️ Writing Tools')

    user_input = st.text_area("Enter your text here:", height=150)

    st.write("Select an action:")
    col1, col2, col3, col4, col5 = st.columns(5)

    # Store results and the type of action performed
    results = None
    action_type = None
    start_time = 0

    with st.spinner('Processing...'): # Spinner covers all button clicks
        with col1:
            if st.button('✨ Rephrase'):
                action_type = 'Rephrase'
                start_time = time.time()
                instruction = 'Rewrite this text for better readability and flow while maintaining its original meaning. Focus on improving sentence structure, clarity, and word choice.'
                results = process_with_llm(instruction, user_input, num_responses=1) # Get 1 clearer rephrase

        with col2:
            if st.button('😎 Make Gen Z'):
                action_type = 'Make Gen Z'
                start_time = time.time()
                instruction = 'Rewrite this text to make it sound like it was written by Gen Z. Use current slang and a casual, relatable tone, maybe even an emoji or two, but keep the core message.'
                results = process_with_llm(instruction, user_input, num_responses=1) # Get 1 Gen Z version

        with col3:
            if st.button('📧 Write Email'):
                action_type = 'Write Email'
                start_time = time.time()
                instruction = 'Convert this text into a professional and formal email format. Ensure the tone is respectful, the language is polished, and it includes appropriate salutations and closings, while keeping the original message intact.'
                results = process_with_llm(instruction, user_input, num_responses=1)

        with col4:
            if st.button('✂️ Make Concise'):
                action_type = 'Make Concise'
                start_time = time.time()
                instruction = 'Rewrite this text to be more concise. Remove unnecessary words, jargon, and redundant phrases. Aim for clarity and brevity, while preserving the essential meaning.'
                results = process_with_llm(instruction, user_input, num_responses=1)

        with col5:
            if st.button('🧐 Grammar'):
                action_type = 'Grammar'
                start_time = time.time()
                # Modified instruction to guide the LLM
                instruction = (
                    'Please check the following text for grammatical errors, spelling mistakes, punctuation issues, and clarity. '
                    'Provide a brief explanation of the main issues found. '
                    'Finally, present the fully corrected sentence clearly labelled like this:\n'
                    'CORRECTED_SENTENCE: [Your corrected sentence here]'
                    )
                results = process_with_llm(instruction, user_input, num_responses=1) # Get 1 corrected version + explanation


    if results is not None and action_type is not None:
        end_time = time.time()
        elapsed_time = end_time - start_time
        st.markdown("---") # Separator
        st.subheader(f"Result for: {action_type}")

        # If results is not a list (because num_responses=1), make it a list for uniform handling
        if not isinstance(results, list):
            results = [results]

        for i, result_text in enumerate(results):
            if not result_text: # Skip if LLM returned empty string
                st.warning(f"Result {i+1}: No response generated.")
                continue

            if action_type == 'Grammar':
                corrected_sentence = extract_corrected_sentence(result_text)

                if corrected_sentence:
                    st.write("**Corrected Text:**")
                    col_text, col_btn = st.columns([0.9, 0.1]) # Text gets 90% width, button 10%
                    with col_text:
                        st.markdown(f"> {corrected_sentence}") # Use markdown blockquote for emphasis
                    with col_btn:
                        copy_button(corrected_sentence, key=f"copy_grammar_{i}")

                    with st.expander("Show Full Explanation & Original Response"):
                        st.write(result_text)
                        copy_button(result_text, key=f"copy_grammar_full_{i}") # Copy full explanation too
                else:
                    # Fallback if parsing failed
                    st.warning("Could not automatically extract the corrected sentence. Displaying full response:")
                    st.write(result_text)
                    copy_button(result_text, key=f"copy_grammar_fallback_{i}")

            else:
                # Handling for other actions (Rephrase, Gen Z, Email, Concise)
                st.write(f"**Suggestion {i+1}:**")
                col_text, col_btn = st.columns([0.9, 0.1])
                with col_text:
                     st.write(result_text)
                with col_btn:
                     copy_button(result_text, key=f"copy_{action_type.lower()}_{i}")

        st.caption(f"Response generated in {elapsed_time:.2f} seconds using Llama3-70b via Groq.")


elif option == "Chat with AI":
    st.title('💬 Chat with AI')

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                # Prepare messages in the format Groq expects
                api_messages = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]

                start_time = time.time()
                with st.spinner("Thinking..."):
                    response = client.chat.completions.create(
                        model="llama3-70b-8192",
                        messages=api_messages,
                        # Optional: Add streaming for better UX
                        # stream=True
                    )
                    # Assuming non-streaming for simplicity here based on original code
                    full_response = response.choices[0].message.content
                    message_placeholder.markdown(full_response)
                end_time = time.time()
                st.caption(f"Response time: {end_time - start_time:.2f} seconds")

            except groq.APIError as e:
                 st.error(f"Groq API Error: {e}")
                 full_response = f"Sorry, I encountered an API error: {e}"
                 message_placeholder.markdown(full_response)
            except Exception as e:
                 st.error(f"An unexpected error occurred: {e}")
                 full_response = f"Sorry, I encountered an error: {e}"
                 message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
