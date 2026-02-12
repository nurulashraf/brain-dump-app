import streamlit as st
from google import genai
import json
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Task Negotiator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUPERTINO CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Overrides */
    .stApp {
        background-color: #F5F5F7;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Padding */
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 5rem;
        max-width: 900px;
    }

    /* Typography */
    h1, h2, h3 {
        color: #1D1D1F;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    
    .stMarkdown p {
        color: #424245;
        font-size: 1.1rem;
    }

    /* Cards / Containers */
    div.stButton > button {
        background-color: #007AFF;
        color: white !important;
        border-radius: 12px;
        border: none;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        font-size: 1rem;
    }

    div.stButton > button:hover {
        background-color: #0063CC !important;
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
        border: none !important;
    }

    div.stButton > button:active {
        transform: scale(0.98);
        background-color: #0056B3 !important;
    }

    /* Secondary Button Styling */
    div.stButton > button[kind="secondary"] {
        background-color: rgba(0, 0, 0, 0.05) !important;
        color: #007AFF !important;
        border: none !important;
    }

    /* Input Fields */
    .stTextArea textarea {
        border-radius: 16px !important;
        border: 1px solid #D2D2D7 !important;
        background-color: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(20px);
        padding: 1.2rem !important;
        font-size: 1.05rem !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.02) !important;
    }

    .stTextArea textarea:focus {
        border-color: #007AFF !important;
        box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.15) !important;
    }

    /* Slider Customization */
    .stSlider > div {
        padding-top: 1rem;
    }

    /* Custom Cupertino Card Class */
    .cupertino-card {
        background: white;
        padding: 2.5rem;
        border-radius: 28px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.04);
        margin-bottom: 2.5rem;
        border: 1px solid rgba(0,0,0,0.03);
    }

    /* Task Table Styling */
    .stDataFrame {
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid #E5E5E7;
    }

    /* Success Message Apple Style */
    .stSuccess {
        background-color: #F2F2F7 !important;
        border-radius: 20px !important;
        border: none !important;
        color: #1D1D1F !important;
        padding: 1.5rem !important;
    }

    /* Hide Streamlit elements for a cleaner look */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Step Labels */
    .step-label {
        color: #007AFF;
        font-weight: 700;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }

</style>
""", unsafe_allow_html=True)

# --- LOGIC & API SETUP ---

try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "YOUR_API_KEY_HERE")

client = genai.Client(api_key=GOOGLE_API_KEY)

def parse_brain_dump(text_input):
    sys_instruction = """
    You are a task extractor for an Apple-style productivity app. 
    Analyze the input text and output a JSON list of tasks.
    Each task must have:
    - "task": The task name (be concise)
    - "time_min": Estimated minutes (integer)
    - "energy": Energy level (Low, Neutral, High)
    
    Return ONLY raw JSON.
    """
    prompt = f"{sys_instruction}\n\n{text_input}"

    try:
        # Try gemma-3-1b-it as requested
        response = client.models.generate_content(model="gemma-3-1b-it", contents=prompt)
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_text)
    except Exception:
        # Fallback to Gemini 2.0 Flash
        try:
            response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_text)
        except Exception as e:
            st.error(f"Unable to parse tasks: {e}")
            return []

def get_recommendation(tasks, time, energy):
    prompt = f"""
    Context: {json.dumps(tasks)}
    User constraint: {time} minutes available, {energy} energy level.
    
    Task: Pick the SINGLE most logical task to do right now. 
    Explain why in a sophisticated, minimalist, and encouraging Apple-style tone. 
    Use clear headings and bullet points if needed.
    """
    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text
    except Exception as e:
        return f"Selection service is currently unavailable. ({e})"

# --- MAIN APPLICATION UI ---

# Hero Header
st.markdown('<div style="text-align: center; margin-top: 1rem; margin-bottom: 3.5rem;">', unsafe_allow_html=True)
st.markdown('<h1 style="font-size: 3.5rem; margin-bottom: 0.5rem;">🧠 Negotiator</h1>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 1.4rem; color: #86868B;">Intelligent focus. Elegantly simple.</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Session State Init
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# Main Container
# Step 1: Capture
st.markdown('<div class="cupertino-card">', unsafe_allow_html=True)
st.markdown('<div class="step-label">Step 1</div>', unsafe_allow_html=True)
st.subheader("Capture your thoughts")
st.markdown("Enter your tasks, ideas, or reminders in any format. We'll organize them for you.")

dump_input = st.text_area(
    "Brain Dump Input",
    placeholder="e.g. Need to finish the presentation by 4pm, call Sarah, buy some oat milk...",
    height=180,
    label_visibility="collapsed"
)

c1, c2, c3 = st.columns([1, 1.5, 1])
with c2:
    if st.button("Extract Tasks"):
        if dump_input:
            with st.spinner("Analyzing..."):
                st.session_state.tasks = parse_brain_dump(dump_input)
                if st.session_state.tasks:
                    st.toast("Tasks extracted successfully!", icon="✅")
                    st.rerun()
        else:
            st.toast("Please enter your thoughts first.", icon="💡")
st.markdown('</div>', unsafe_allow_html=True)

# Step 2: Review & Focus
if st.session_state.tasks:
    st.markdown('<div class="cupertino-card">', unsafe_allow_html=True)
    st.markdown('<div class="step-label">Step 2</div>', unsafe_allow_html=True)
    st.subheader("Define your focus")
    
    # Display table in a clean way
    st.dataframe(
        st.session_state.tasks,
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Your current state")
    
    sc1, sc2 = st.columns(2)
    with sc1:
        time_val = st.slider("Time window", 5, 120, 30, format="%d min")
    with sc2:
        energy_val = st.select_slider(
            "Energy level",
            options=["Resting", "Low", "Neutral", "High", "Peak"],
            value="Neutral"
        )
    
    if st.button("⚡ Recommend Best Path"):
        with st.spinner("Computing optimal focus..."):
            rec = get_recommendation(st.session_state.tasks, time_val, energy_val)
            st.session_state.current_rec = rec
            
    if 'current_rec' in st.session_state:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div style="background: #F5F5F7; padding: 2rem; border-radius: 20px; border-left: 6px solid #007AFF;">', unsafe_allow_html=True)
        st.markdown("### Recommendation")
        st.markdown(st.session_state.current_rec)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Global Actions
    bc1, bc2, bc3 = st.columns([2, 1, 2])
    with bc2:
        if st.button("Reset All", type="secondary"):
            st.session_state.tasks = []
            if 'current_rec' in st.session_state:
                del st.session_state.current_rec
            st.rerun()