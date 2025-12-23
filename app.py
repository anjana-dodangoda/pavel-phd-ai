import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="Pavel PhD AI", page_icon="🎓", layout="wide")

# Custom CSS for "PhD Level" Aesthetics
st.markdown("""
<style>
    .stChatMessage { font-family: 'Times New Roman', serif; }
    h1, h2, h3 { color: #4F46E5; }
    .stButton button { background-color: #4F46E5; color: white; }
</style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR: CONTROL PANEL ---
with st.sidebar:
    st.header("🧠 Neural Engine")
    
    # API Key Input (Secure)
    api_key = st.text_input("Enter Gemini API Key", type="password")
    
    # The "Dual Brain" Toggle
    brain_type = st.radio(
        "Select Intelligence Level:",
        ["Gemini 1.5 Flash (Fast & Study)", "Gemini 1.5 Pro (PhD Research)"],
        captions=["Good for revision & chat.", "Solves hardest equations. Slower."]
    )
    
    model_name = "gemini-1.5-pro" if "Pro" in brain_type else "gemini-1.5-flash"

    st.divider()
    
    st.header("📚 The Library")
    uploaded_files = st.file_uploader(
        "Upload Textbooks / Notes (PDF/IMG)", 
        accept_multiple_files=True,
        type=['pdf', 'png', 'jpg', 'jpeg']
    )
    
    if uploaded_files:
        st.success(f"{len(uploaded_files)} References Loaded")

# --- 3. SESSION STATE (Memory) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Initial "System Prompt" to define persona
    st.session_state.messages.append({
        "role": "model", 
        "parts": ["You are Pavel, a PhD-level Research Assistant in Theoretical Physics & Applied Maths. "
                  "You must solve equations step-by-step using LaTeX. "
                  "You must cite the uploaded documents for every claim. "
                  "You are capable of reading handwriting and interpreting complex plots."]
    })

# --- 4. THE AI FUNCTION ---
def get_ai_response(prompt, files, key, model):
    if not key:
        return "⚠️ Please enter your API Key in the sidebar."
    
    genai.configure(api_key=key)
    
    # Configure the Brain
    generation_config = {
        "temperature": 0.2, # Low temp = More precise math
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192, # Long answers for complex proofs
    }
    
    model = genai.GenerativeModel(
        model_name=model,
        generation_config=generation_config,
        system_instruction="You are a PhD Research Assistant. Solve harder problems by breaking them down. Use LaTeX for math."
    )

    # Prepare the "Context" (User text + Uploaded Files)
    content = [prompt]
    
    # Add files to the prompt (Gemini can "see" them directly)
    for file in files:
        bytes_data = file.getvalue()
        mime_type = file.type
        
        # Convert images/pdfs to Gemini-friendly format
        if "image" in mime_type:
             content.append({"mime_type": mime_type, "data": bytes_data})
        elif "pdf" in mime_type:
             content.append({"mime_type": "application/pdf", "data": bytes_data})

    try:
        # Generate Answer
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- 5. MAIN CHAT INTERFACE ---
st.title("🎓 Pavel AI: PhD Research Station")
st.caption("Theoretical Physics | Pure Math | Applied Math")

# Display Chat History
for msg in st.session_state.messages:
    if msg["role"] != "system": # Hide system prompt
        with st.chat_message(msg["role"]):
            st.markdown(msg["parts"][0])

# Input Area
if prompt := st.chat_input("Enter a complex equation or question..."):
    # 1. Show User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "parts": [prompt]})

    # 2. Generate AI Response
    with st.chat_message("assistant"):
        with st.spinner(f"Pavel is analyzing {len(uploaded_files or [])} documents..."):
            response_text = get_ai_response(prompt, uploaded_files, api_key, model_name)
            st.markdown(response_text)
            
    # 3. Save AI Message
    st.session_state.messages.append({"role": "model", "parts": [response_text]})
