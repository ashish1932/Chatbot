import streamlit as st
from llama_cpp import Llama
import html
import re
import json
import os
from datetime import datetime
from auth import auth_controller, logout_button

# ===== CONFIG =====
MODEL_PATH = "F:/Bot/model/mistral-7b-instruct-v0.2.Q5_K_M.gguf"
MAX_TOKENS = 512
CHAT_HISTORY_FILE = "chat_history.json"

# ===== MODEL =====
@st.cache_resource
def load_model():
    return Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,       # reduced context size (faster)
        n_threads=6,      # match your physical cores
        n_batch=128,      # faster CPU inference
        use_mmap=True,    # memory mapping
        use_mlock=True,   # keep in RAM (if enough)
        verbose=False
    )

llm = load_model()

# ===== HISTORY =====
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_chat_history(history):
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

chat_history = load_chat_history()

# ===== CSS (same UI as before) =====
st.markdown("""
<style>
/* Title animation */
@keyframes fadeInDown {
    0% { opacity: 0; transform: translateY(-30px); }
    100% { opacity: 1; transform: translateY(0); }
}
.animated-title {
    animation: fadeInDown 1s ease-out;
    font-family: 'Segoe UI', sans-serif;
    text-align: center;
    font-size: 36px;
    margin-bottom: 10px;
}

/* Chat bubbles */
.chat-bubble-user {
    background: #a1c4fd;
    padding: 12px 18px;
    border-radius: 20px 20px 0 20px;
    margin: 8px 0;
    max-width: 80%;
    float: right;
    clear: both;
    box-shadow: 0 4px 12px rgba(161,196,253,0.5);
    animation: fadeInRight 0.5s ease forwards;
    font-family: 'Segoe UI', sans-serif;
    color: #222;
}
.chat-bubble-bot {
    background: #d4fc79;
    padding: 12px 18px;
    border-radius: 20px 20px 20px 0;
    margin: 8px 0;
    max-width: 80%;
    float: left;
    clear: both;
    box-shadow: 0 4px 12px rgba(212,252,121,0.5);
    animation: fadeInLeft 0.5s ease forwards;
    font-family: 'Segoe UI', sans-serif;
    color: #222;
}

/* Text input hover effect */
input[type="text"] {
    width: 100%;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid #ccc;
    transition: all 0.3s ease;
}
input[type="text"]:hover {
    border-color: #4a90e2;
    box-shadow: 0 0 5px rgba(74,144,226,0.5);
}

/* Button hover effect */
button[kind="secondary"], button[kind="primary"] {
    transition: all 0.3s ease;
}
button[kind="secondary"]:hover, button[kind="primary"]:hover {
    background-color: #4a90e2 !important;
    color: white !important;
    transform: scale(1.05);
}

/* Title animation loop */
@keyframes fadeInDown {
    0% { opacity: 0; transform: translateY(-30px); }
    50% { opacity: 1; transform: translateY(0); }
    100% { opacity: 0; transform: translateY(-30px); }
}
.animated-title {
    animation: fadeInDown 3s ease-in-out infinite;
    font-family: 'Poppins', sans-serif;
    text-align: center;
    font-size: 42px;
    margin-bottom: 10px;
    color: #4a90e2;
    letter-spacing: 2px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

# ===== SESSION STATE =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# ===== MAIN CHAT APP =====
def chat_app():
    with st.sidebar:
        st.markdown(f"**👤 Logged in as:** {st.session_state.username}")
        logout_button()
        st.markdown("---")
        st.title("💬 Chat History")
        for chat_id, chat in chat_history.items():
            cols = st.columns([0.85, 0.15])
            if cols[0].button(chat["title"], key=f"load_{chat_id}"):
                st.session_state.chat_id = chat_id
                st.session_state.messages = chat["messages"]
            if cols[1].button("🗑️", key=f"del_{chat_id}"):
                chat_history.pop(chat_id)
                save_chat_history(chat_history)
                if st.session_state.chat_id == chat_id:
                    st.session_state.chat_id = None
                    st.session_state.messages = []
                st.rerun()
        if st.button("🧹 New Chat"):
            st.session_state.chat_id = None
            st.session_state.messages = []

    st.markdown("<div class='animated-title'>🤖 Cube AI Chatbot</div><hr>", unsafe_allow_html=True)

    # Display messages
    for msg in st.session_state.messages:
        role = msg["role"]
        content_html = html.escape(msg['content']).replace('\n', '<br>')
        if role == "user":
            st.markdown(f'<div class="chat-bubble-user"><b>You:</b> {content_html}</div>', unsafe_allow_html=True)
        else:
            code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", msg["content"], re.DOTALL)
            pre_code = re.sub(r"```.*?```", "", msg["content"], flags=re.DOTALL).strip()
            if pre_code:
                st.markdown(f'<div class="chat-bubble-bot"><b>Bot:</b> {html.escape(pre_code).replace("\n","<br>")}</div>', unsafe_allow_html=True)
            for code in code_blocks:
                st.code(code.strip())

    st.markdown("---")

    # Input box
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        with st.form(key="chat_form", clear_on_submit=True):
            cols = st.columns([10, 1])
            user_input = cols[0].text_input("Type your message...", label_visibility="collapsed", placeholder="Ask me anything...")
            send = cols[1].form_submit_button("➡️")
        st.markdown('</div>', unsafe_allow_html=True)

    if send and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})
        chat_placeholder = st.empty()
        bot_reply = ""

        with st.spinner("🤖 Thinking..."):
            try:
                # ✅ Faster ChatCompletion API
                stream = llm.create_chat_completion(
                    messages=[{"role": "system", "content": "You are a helpful assistant."}] +
                             [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    max_tokens=MAX_TOKENS,
                    temperature=0.7,
                    stream=True
                )

                for chunk in stream:
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    bot_reply += delta
                    chat_placeholder.markdown(
                        f'<div class="chat-bubble-bot"><b>Bot:</b> {html.escape(bot_reply).replace("\n","<br>")}</div>',
                        unsafe_allow_html=True
                    )

            except Exception as e:
                bot_reply = f"❌ Error: {e}"
                chat_placeholder.error(bot_reply)

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        if not st.session_state.chat_id:
            new_id = datetime.now().strftime("chat_%Y%m%d%H%M%S")
            title = user_input[:30] + ("..." if len(user_input) > 30 else "")
            st.session_state.chat_id = new_id
            chat_history[new_id] = {"title": title, "messages": st.session_state.messages.copy()}
        else:
            chat_history[st.session_state.chat_id]["messages"] = st.session_state.messages.copy()

        save_chat_history(chat_history)
        st.rerun()

# ===== RUN APP =====
if st.session_state.logged_in:
    chat_app()
else:
    auth_controller()
