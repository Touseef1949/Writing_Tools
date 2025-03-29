import streamlit as st
import groq
import time
import dotenv
import os
from typing import List, Optional, Tuple

# Load environment variables
dotenv.load_dotenv()

# --- Constants ---
DEFAULT_MODEL = "llama3-70b-4096" # Or choose a default like "llama3-8b-8192" for speed
AVAILABLE_MODELS = [
    "llama3-70b-4096",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma-7b-it",
]
NUM_REPHRASES = 3 # Number of rephrase variations to generate

# --- Groq Client Initialization ---
# Use st.cache_resource for client initialization to avoid re-creating it on every script run
@st.cache_resource
def get_groq_client():
    """Initializes and returns the Groq client."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY is missing. Please set it in your .env file or environment variables.", icon="🚨")
        st.stop() # Stop execution if key is missing
    try:
        client = groq.Client(api_key=api_key)
        # Test connection briefly (optional but good practice)
        _ = client.models.list()
        return client
    except groq.AuthenticationError:
        st.error("Groq Authentication Failed: Invalid API Key.", icon="🚨")
        st.stop()
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}", icon="🚨")
        st.stop()

client = get_groq_client()

# --- Core Logic Functions with Caching and Error Handling ---

# Helper function for making API calls - easier to cache and manage
@st.cache_data(show_spinner=False) # Show spinner manually outside the cached function
def _call_groq_api(prompt: str, model: str, n: int = 1, temperature: float = 0.7) -> Tuple[Optional[List[str]], Optional[str]]:
    """
    Makes a call to the Groq API and handles potential errors.

    Args:
        prompt: The prompt to send to the model.
        model: The Groq model to use.
        n: Number of completions to generate.
        temperature: Sampling temperature.

    Returns:
        A tuple containing:
        - A list of response contents (str) if successful, else None.
        - An error message (str) if an error occurred, else None.
    """
    try:
        start_time = time.time()
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            n=n,
            temperature=temperature,
            stop=None, # Let model decide when to stop
            # stream=False, # Keep stream=False for simplicity here
        )
        end_time = time.time()
        st.sidebar.info(f"Groq API call ({model}): {end_time - start_time:.2f}s") # Log timing to sidebar

        if completion.choices:
             response_contents = [choice.message.content for choice in completion.choices]
             # Optional: Log token usage if needed
             # usage = completion.usage
             # st.sidebar.info(f"Tokens: Prompt={usage.prompt_tokens}, Completion={usage.completion_tokens}, Total={usage.total_tokens}")
             return response_contents, None
        else:
             return None, "API returned no choices."

    except groq.APIConnectionError as e:
        return None, f"Groq API Connection Error: {e.__cause__}"
    except groq.RateLimitError:
        return None, "Groq Rate Limit Exceeded. Please wait and try again."
    except groq.APIStatusError as e:
        return None, f"Groq API Error (Status {e.status_code}): {e.message}"
    except Exception as e:
        return None, f"An unexpected error occurred: {e}"

def rephrase(instruction: str, user_message: str, model: str) -> List[str]:
    """
    Generates multiple rephrased versions of the user message using a single API call.
    """
    if not user_message:
        return []

    # Refined prompt asking for multiple distinct variations
    prompt = f"""Please rewrite the following text based on the instruction below. Provide {NUM_REPHRASES} distinct variations.

Instruction: {instruction}

Original Text:
"{user_message}"

Generate the {NUM_REPHRASES} variations clearly, perhaps separated by newlines or numbered."""

    # Note: Asking for N variations in one prompt might be less reliable than using n=N.
    # Let's try using the 'n' parameter for better reliability if the model supports it well.
    prompt_for_n = f"""Instruction: {instruction}

Rewrite the following text according to the instruction:
"{user_message}"
"""
    with st.spinner(f"Generating {NUM_REPHRASES} variations using {model}..."):
        responses, error = _call_groq_api(prompt_for_n, model, n=NUM_REPHRASES, temperature=0.7)

    if error:
        st.error(f"Failed to get rephrases: {error}", icon="❌")
        return []
    if responses:
        # Basic cleaning in case the model adds extra text around the core response
        cleaned_responses = [r.strip().strip('"') for r in responses]
        return cleaned_responses
    else:
        st.warning("The model didn't provide any rephrases.", icon="⚠️")
        return []


def generate_response(instruction: str, user_message: str, model: str) -> str:
    """
    Generates a single response based on the instruction and user message.
    """
    if not user_message:
        return ""
    if not instruction: # Handle missing instruction for chat
         st.warning("Please provide an instruction for the chat.", icon="⚠️")
         return ""

    prompt = f'{instruction}\n\n"{user_message}"'

    with st.spinner(f"Generating response using {model}..."):
        responses, error = _call_groq_api(prompt, model, n=1, temperature=0.5) # Lower temp for more focused chat

    if error:
        st.error(f"Failed to generate response: {error}", icon="❌")
        return ""
    if responses:
        return responses[0].strip()
    else:
        st.warning("The model didn't provide a response.", icon="⚠️")
        return ""

# --- Streamlit UI ---

st.set_page_config(layout="wide") # Use wider layout

# Sidebar for global options
with st.sidebar:
    st.header("Options")
    selected_model = st.selectbox(
        "Choose Groq Model:",
        options=AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index(DEFAULT_MODEL) if DEFAULT_MODEL in AVAILABLE_MODELS else 0,
        help="Select the AI model to use. Faster models (like 8b) might be less capable than larger ones (like 70b)."
    )

    st.divider()
    app_mode = st.radio(
        "Choose Mode:",
        ("Writing Tools", "Chat with AI"),
        horizontal=True,
    )
    st.divider()
    st.markdown("--- \n*Powered by Groq & Streamlit*")


# Main content based on selected mode
if app_mode == "Writing Tools":
    st.title('✍️ Writing Tools')
    st.markdown(f"Using model: `{selected_model}`")

    user_input = st.text_area("Enter your text here:", height=150, key="writing_input")

    st.write("Apply a transformation:")
    # Using columns for button layout
    cols = st.columns(5)
    button_actions = {
        "Rephrase": ('Rewrite this text for better readability while maintaining its original meaning. Focus on improving sentence structure and clarity.', cols[0]),
        "Make Gen Z": ('Rewrite this text to make it more appealing and relatable to a younger, millennial or Gen Z audience. Use contemporary language, slang, and references that resonate with this demographic, while keeping the original message intact.', cols[1]),
        "Write Email": ('Create a professional and formal email based on the text. Ensure the tone is respectful and the language is polished, keeping the core message intact.', cols[2]),
        "Make Concise": ('Rewrite this section to make it more concise. Remove any unnecessary words and redundant phrases, while keeping the original message intact.', cols[3]),
        "Grammar Check": ('Identify grammatical errors, suggest corrections, and briefly explain the reasoning behind the changes. Maintain the original meaning.', cols[4]),
    }

    # Store results in session state to persist across reruns if buttons are clicked sequentially
    if 'rephrases_results' not in st.session_state:
        st.session_state.rephrases_results = []
        st.session_state.rephrases_time = 0.0

    clicked_button = None
    instruction_for_action = ""

    for btn_name, (instruction, col) in button_actions.items():
        if col.button(btn_name, key=f"btn_{btn_name.lower().replace(' ','_')}"):
             if user_input:
                 clicked_button = btn_name
                 instruction_for_action = instruction
             else:
                 st.warning("Please enter text in the text area above.", icon="⚠️")

    # Process the clicked button action outside the button check
    if clicked_button:
        start_time = time.time()
        results = rephrase(instruction_for_action, user_input, selected_model)
        end_time = time.time()
        st.session_state.rephrases_results = results
        st.session_state.rephrases_time = end_time - start_time
        # Clear the click state by forcing a rerun (or use more complex state management)
        st.rerun() # Rerun to display results below without button staying "pressed"


    # Display results if they exist in session state
    if st.session_state.rephrases_results:
        st.subheader("Results:")
        for i, result in enumerate(st.session_state.rephrases_results, 1):
            st.markdown(f"**Variation {i}:**")
            st.markdown(f"> {result}") # Use blockquote for better visual separation
            st.write("---") # Separator
        st.success(f"Generated {len(st.session_state.rephrases_results)} variations in {st.session_state.rephrases_time:.2f} seconds.")
        # Optionally clear results after display if desired
        # if st.button("Clear Results"):
        #    st.session_state.rephrases_results = []
        #    st.session_state.rephrases_time = 0.0
        #    st.rerun()


elif app_mode == "Chat with AI":
    st.title('💬 Chat with AI')
    st.markdown(f"Using model: `{selected_model}`")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What can I help you with? (e.g., Summarize this, explain like I'm 5...)"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            # Here, we might need context from previous messages.
            # For simplicity now, we'll treat each input independently.
            # For a real chatbot, you'd pass chat history to the API.
            # Let's assume the user provides context in their single prompt for now.
            # Example: User types "Summarize this: [long text]"
            # We can parse the instruction from the prompt if needed, or assume the whole prompt is the task.
            # For this version, let's treat the whole chat input as the user_message
            # and provide a placeholder instruction, or let the model infer.
            # A better approach would be to have separate fields for instruction/context.

            # Let's make a simplified assumption: the prompt IS the instruction+message
            chat_instruction = "Respond helpfully to the following user request:" # Generic instruction
            user_message_from_chat = prompt

            start_time = time.time()
            response_content = generate_response(chat_instruction, user_message_from_chat, selected_model)
            end_time = time.time()

            if response_content:
                st.markdown(response_content)
                st.session_state.messages.append({"role": "assistant", "content": response_content})
                st.sidebar.info(f"Chat response generated in {end_time - start_time:.2f} seconds.")
            else:
                st.error("Assistant failed to respond.", icon="❌")
                # Optionally add a placeholder message to history
                st.session_state.messages.append({"role": "assistant", "content": "*Assistant failed to respond*"})
