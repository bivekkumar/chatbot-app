import streamlit as st
from bot_backend import chatbot
from langchain_core.messages import HumanMessage
thread_id = '1'
CONFIG = {'configurable':{'thread_id':thread_id}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] =[]

# Mobile-friendly layout
st.set_page_config(
    page_title="AI Resume Assistant 🤖",
    page_icon="📄",
    layout="centered",  # better for mobile
    initial_sidebar_state="collapsed"
)

# ========== FANCY CSS ==========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #e0f7fa, #f9fbe7);
    padding: 0;
    margin: 0;
}

.app-header {
    font-size: 2.5rem;
    font-weight: 700;
    color: #0f4c81;
    margin-top: 2vh;
    margin-bottom: 0.5rem;
    text-align: center;
}

.app-description {
    font-size: 1.1rem;
    color: #333;
    text-align: center;
    margin-bottom: 3vh;
    padding: 0 20px;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.chat-container {
    max-height: 60vh;
    overflow-y: auto;
    padding: 1rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
}

.user-msg, .assistant-msg {
    display: flex;
    align-items: flex-start;
    margin-bottom: 1rem;
    font-size: 1rem;
    line-height: 1.5;
}

.user-msg .msg-bubble, .assistant-msg .msg-bubble {
    padding: 0.8rem 1rem;
    border-radius: 1rem;
    max-width: 80%;
    word-wrap: break-word;
}

.user-msg {
    justify-content: flex-end;
}

.user-msg .msg-bubble {
    background-color: #0f4c81;
    color: white;
    border-bottom-right-radius: 0;
}

.assistant-msg {
    justify-content: flex-start;
}

.assistant-msg .msg-bubble {
    background-color: #e1e8f7;
    color: #0f4c81;
    border-bottom-left-radius: 0;
}

.assistant-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin-right: 0.8rem;
    object-fit: cover;
}

#MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ========== HEADER + DESCRIPTION ==========

st.markdown('<div class="app-header">🤖 Bivek’s Resume Assistant</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="app-description">
        Curious about Bivek’s professional background, skills, or experience across lending, AI/ML, or product leadership? <br><br>
        I’m your AI-powered assistant trained on Bivek’s resume and work history — ready to answer your questions and help evaluate fit for any role. <br><br>
        Ask me anything about his experience, responsibilities, outcomes, or domain knowledge.
    </div>
    """, 
    unsafe_allow_html=True
)

# ========== CHAT AREA ==========

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['message'])

user_input = st.chat_input('Type your query here...')

if user_input:

    st.session_state['message_history'].append({'role':'user','message': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    #response = chatbot.invoke({'messages':HumanMessage(content=user_input)},config=CONFIG)
    #ai_message = response['messages'][-1].content
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream({'messages':[HumanMessage(content=user_input)]},config=CONFIG, stream_mode='messages')
        )
    
    st.session_state['message_history'].append({'role':'assistant','message': ai_message})