import streamlit as st
import google.generativeai as genai
import os

# --- Configure API Key ---
if "GOOGLE_API_KEY" in st.secrets:
    GEMINI_API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    # Fallback for local testing if you set it as an environment variable
    GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GEMINI_API_KEY:
    st.error("Google API Key not found. Please set it in .streamlit/secrets.toml or as an environment variable (e.g., GOOGLE_API_KEY).")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# --- Initialize the Model ---
# *** CRITICAL CHANGE: Use the model name that worked for you before ***
# If 'gemini-2.0-flash' worked, use it here!
# Add a try-except for model loading as a safety net.
try:
    # Attempt to load gemini-2.0-flash first
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    try:
        # Fallback to gemini-pro if 2.0-flash fails
        model = genai.GenerativeModel('gemini-pro')
    except Exception as e_fallback:
        st.error(f"Could not load 'gemini-pro' either. Error: {e_fallback}")
        st.stop()


# --- Streamlit App Interface ---
st.set_page_config(page_title="AI-Powered Fun Fact Generator", page_icon="🤖")

st.title("🤖 AI-Powered Fun Fact Generator")
st.write("Enter a topic to generate an interesting and unique fact!")

user_topic = st.text_input("What kind of fact would you like? (e.g., 'space', 'animals', 'history')", key="topic_input")

# --- Function to generate fact using the chosen model ---
def generate_ai_fact(topic):
    # Crafting a good prompt is crucial for LLMs!
    # We ask for a short, verifiable fact and specify no greetings/closings.
    prompt = f"Generate a single, interesting, surprising, and verifiable fun fact about {topic}. Ensure the fact is concise and directly answers the request. Do not include any introductory phrases like 'Here's a fact:' or 'Did you know?' or concluding remarks. Just the fact itself."

    try:
        with st.spinner(f"Asking gemini about {topic}..."):
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.9,
                    candidate_count=1,
                    max_output_tokens=80, # Keep this value reasonable
                )
            )

            # Access the generated text. LLM outputs can sometimes be complex objects.
            # Handle cases where response.text might not be directly available for all models/outputs
            if response and hasattr(response, 'text') and response.text:
                fact_text = response.text.strip()
            elif response.candidates and response.candidates[0].content.parts:
                fact_text = response.candidates[0].content.parts[0].text.strip()
            else:
                return "The AI generated an empty or unreadable response. Please try again."

            # Basic post-processing to clean up common LLM tendencies
            undesired_prefixes = ["here's a fun fact about", "a fun fact about", "did you know that", "fact:", "fun fact:", "the fun fact is", "here's an interesting fact about", "an interesting fact about"]
            for prefix in undesired_prefixes:
                if fact_text.lower().startswith(prefix):
                    fact_text = fact_text[len(prefix):].strip()
                    if fact_text.startswith(":"):
                        fact_text = fact_text[1:].strip()

            if len(fact_text) < 15: # A slightly lower minimum length for short facts
                return "The AI couldn't generate a good fact for that. Please try a different topic or click again."

            return fact_text

    except genai.types.BlockedPromptException:
        return "I'm sorry, I cannot generate a fact for that topic due to safety guidelines. Please try a different topic."
    except Exception as e:
        # Catch potential API errors, network issues, or generation problems
        st.error(f"An error occurred while generating the fact: {e}")
        return "Failed to generate fact. Please check your API key, internet connection, or try a different topic."

# --- App Logic ---
if st.button("Generate AI Fact 🚀", key="generate_button"):
    if user_topic:
        fact = generate_ai_fact(user_topic)
        if fact:
            st.markdown("<div class='success'>Here's your fun fact!</div>", unsafe_allow_html=True)
            st.info(fact)
    else:
        st.warning("Please enter a topic to generate a fact!")

st.markdown("---")
st.markdown(f"Powered by Google Generative AI.") # Dynamically show the model used

st.markdown("""
    <style>
    .success {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: "light blue";  /* Change this color code as needed */
        color: white;               /* Text color */
    }
    </style>
""", unsafe_allow_html=True)