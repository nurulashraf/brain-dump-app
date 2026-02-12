import streamlit as st
from google import genai
import json
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Negotiator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- REFINED CUPERTINO CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Overrides */
    .stApp {
        background-color: #F5F5F7 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Main Container */
    .main .block-container {
        padding-top: 4rem !important;
        padding-bottom: 4rem !important;
        max-width: min(800px, 100% - 2rem) !important;
        margin: auto;
    }

    /* Typography */
    h1, h2, h3, h4, .stMarkdown, p, span, label {
        color: #1D1D1F !important;
        font-family: 'Inter', sans-serif !important;
    }

    .hero-title {
        font-size: clamp(2rem, 8vw, 3.5rem) !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        margin-bottom: 0.5rem !important;
        color: #1D1D1F !important;
    }

    .hero-subtitle {
        font-size: clamp(1rem, 4vw, 1.4rem) !important;
        color: #86868B !important;
        font-weight: 400 !important;
        margin-bottom: 3rem !important;
    }

    /* Step Labels */
    .step-badge {
        background-color: #007AFF !important;
        color: white !important;
        padding: 4px 12px !important;
        border-radius: 20px !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        display: inline-block !important;
        margin-bottom: 1rem !important;
    }

    /* Apple-style Cards via st.container(border=True) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important;
        padding: clamp(1.5rem, 4vw, 3rem) !important;
        border-radius: clamp(20px, 4vw, 30px) !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.06) !important;
        margin-bottom: 2rem !important;
        border: 1px solid rgba(0,0,0,0.03) !important;
    }

    /* Remove inner container's default border/padding so our card style is the only one */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border: none !important;
        padding: 0 !important;
    }

    /* Primary Action Buttons */
    div.stButton > button {
        background-color: #007AFF !important;
        color: white !important;
        border-radius: 14px !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 14px 0 rgba(0,118,255,0.39) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }

    div.stButton > button:hover {
        background-color: #0070E0 !important;
        transform: scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(0,118,255,0.23) !important;
    }

    div.stButton > button:active {
        transform: scale(0.98) !important;
    }

    /* Secondary Buttons */
    div.stButton > button[kind="secondary"] {
        background-color: #F5F5F7 !important;
        color: #007AFF !important;
        box-shadow: none !important;
        font-weight: 500 !important;
    }

    /* Input Areas */
    .stTextArea textarea {
        border-radius: 18px !important;
        border: 1px solid #D2D2D7 !important;
        background-color: #FBFBFF !important;
        padding: 1.5rem !important;
        font-size: 1.1rem !important;
        color: #1D1D1F !important;
        line-height: 1.5 !important;
    }

    .stTextArea textarea:focus {
        border-color: #007AFF !important;
        box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1) !important;
    }

    /* Sliders */
    .stSlider label {
        font-weight: 600 !important;
        color: #1D1D1F !important;
    }

    /* Dataframes */
    .stDataFrame {
        border: 1px solid #E5E5E7 !important;
        border-radius: 14px !important;
        overflow: hidden !important;
    }

    /* Recommendation box */
    .rec-box {
        background-color: #F5F5F7 !important;
        padding: 2rem !important;
        border-radius: 20px !important;
        border-left: 6px solid #007AFF !important;
    }
    .rec-box p {
        color: #1D1D1F !important;
    }

    /* Hide standard UI fluff */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .reportview-container .main footer {visibility: hidden;}

    /* --- Mobile Responsive --- */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }

        .hero-subtitle {
            margin-bottom: 2rem !important;
        }

        div.stButton > button {
            padding: 0.7rem 1.5rem !important;
            font-size: 1rem !important;
        }

        .stTextArea textarea {
            padding: 1rem !important;
            font-size: 1rem !important;
            border-radius: 14px !important;
        }

        .rec-box {
            padding: 1.5rem !important;
            border-radius: 16px !important;
        }
    }

</style>
""", unsafe_allow_html=True)

# --- API CLIENT ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = os.getenv("GOOGLE_API_KEY", "YOUR_API_KEY_HERE")

client = genai.Client(api_key=api_key)

def extract_tasks(text):
    prompt = f"""Extract tasks from this notes dump. Return only raw JSON list of objects:
    [ {{"task": "...", "time_min": int, "energy": "Low/Neutral/High" }} ]
    
    Notes: {text}"""
    
    try:
        # User explicitly requested gemma-3-1b-it
        response = client.models.generate_content(model="gemma-3-1b-it", contents=prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        # Fallback to lightning-fast 2.0 Flash
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)

def recommend_focus(tasks, time, energy):
    prompt = f"""Tasks: {json.dumps(tasks)}
    Constraint: {time} mins, {energy} energy.
    Pick 1 task. Respond in a minimalist, sophisticated Apple-style tone.
    Explain precisely why this choice is optimal."""
    
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text

# --- APP LAYOUT ---

# Hero
st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
st.markdown('<div class="hero-title">🧠 Negotiator</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Intelligent focus. Elegantly simple.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# Step 1: Capture
with st.container(border=True):
    st.markdown('<div class="step-badge">Capture</div>', unsafe_allow_html=True)
    st.markdown('<h2 style="margin-top:0;">What\'s on your mind?</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#86868B; margin-bottom:2rem;">Pour your thoughts. We will distill them into actionable steps.</p>', unsafe_allow_html=True)

    notes = st.text_area("Input", placeholder="Write anything here...", height=200, label_visibility="collapsed")

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if st.button("Distill Thoughts"):
            if notes:
                with st.spinner(""):
                    st.session_state.tasks = extract_tasks(notes)
                    st.rerun()
            else:
                st.toast("Entrance required.")

# Step 2: Focus
if st.session_state.tasks:
    with st.container(border=True):
        st.markdown('<div class="step-badge">Focus</div>', unsafe_allow_html=True)
        st.markdown('<h2 style="margin-top:0;">Precision Selection</h2>', unsafe_allow_html=True)

        st.dataframe(st.session_state.tasks, use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)
        with c1:
            time_sel = st.slider("Time Window", 5, 120, 30, format="%d min")
        with c2:
            energy_sel = st.select_slider("Energy Level", options=["Resting", "Low", "Neutral", "High", "Peak"], value="Neutral")

        if st.button("Recommended Path"):
            with st.spinner(""):
                recommendation = recommend_focus(st.session_state.tasks, time_sel, energy_sel)
                st.session_state.rec_text = recommendation

        if 'rec_text' in st.session_state:
            st.markdown(f"""
            <div class="rec-box">
                <p style="font-weight: 600; font-size: 1.2rem; margin-bottom: 1rem;">Optimized Decision</p>
                {st.session_state.rec_text}
            </div>
            """, unsafe_allow_html=True)

    # Global Actions
    bc1, bc2, bc3 = st.columns([2, 1, 2])
    with bc2:
        if st.button("Clear Session", type="secondary"):
            st.session_state.tasks = []
            if 'rec_text' in st.session_state:
                del st.session_state.rec_text
            st.rerun()