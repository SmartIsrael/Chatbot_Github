import streamlit as st
import numpy as np
import json
import pickle
import random
import torch
from transformers import BertModel, BertTokenizer
from tensorflow.keras.models import load_model
import nltk
from nltk.stem import WordNetLemmatizer

# Page Configuration
st.set_page_config(
    page_title="GitBuddy",
    page_icon="🐙",
    layout="wide"
)

# Custom CSS for an eye-catching, fun UI
st.markdown("""
    <style>
        /* Main styling with gradients and animations */
        .main {
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            color: #e6edf3;
        }
        
        /* Header with animated gradient */
        .header {
            background: linear-gradient(-45deg, #2ea043, #238636, #1f6feb, #6e40c9);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }
        
        @keyframes gradient {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        
        /* Fun chat container with subtle animations */
        .chat-wrapper {
            display: flex;
            flex-direction: column;
            gap: 16px;
            padding: 24px;
            max-width: 900px;
            margin: auto;
            border-radius: 16px;
            background-color: rgba(22, 27, 34, 0.7);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }
        
        /* Message styling with hover effects */
        .message-container {
            display: flex;
            margin-bottom: 14px;
            transition: transform 0.2s ease;
        }
        
        .message-container:hover {
            transform: translateY(-2px);
        }
        
        .user-message {
            justify-content: flex-end;
        }
        
        .bot-message {
            justify-content: flex-start;
        }
        
        /* Avatar styling */
        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            margin: 0 10px;
            background-size: cover;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        }
        
        .user-avatar {
            background-color: #238636;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        
        .bot-avatar {
            background-color: #1f6feb;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        
        /* Message bubbles with fun shapes */
        .message-bubble {
            padding: 16px 20px;
            border-radius: 18px;
            max-width: 80%;
            font-size: 16px;
            line-height: 1.5;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
            position: relative;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(10px);}
            to {opacity: 1; transform: translateY(0);}
        }
        
        .user-bubble {
            background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        .user-bubble::after {
            content: '';
            position: absolute;
            right: -10px;
            bottom: 0;
            width: 20px;
            height: 20px;
            background: #2ea043;
            border-bottom-left-radius: 16px;
            z-index: -1;
        }
        
        .bot-bubble {
            background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%);
            color: white;
            border-bottom-left-radius: 4px;
        }
        
        .bot-bubble::after {
            content: '';
            position: absolute;
            left: -10px;
            bottom: 0;
            width: 20px;
            height: 20px;
            background: #1f6feb;
            border-bottom-right-radius: 16px;
            z-index: -1;
        }
        
        /* Input area with glow effect */
        .input-container {
            background-color: rgba(13, 17, 23, 0.5);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }
        
        .input-container:hover {
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(31, 111, 235, 0.3);
        }
        
        .stTextArea textarea {
            background-color: rgba(13, 17, 23, 0.7);
            color: #e6edf3;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 14px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .stTextArea textarea:focus {
            border-color: #1f6feb;
            box-shadow: 0 0 0 3px rgba(31, 111, 235, 0.3);
        }
        
        /* Button with hover animation */
        .send-button {
            background: linear-gradient(90deg, #238636, #2ea043);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        .send-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
            background: linear-gradient(90deg, #2ea043, #39d353);
        }
        
        /* Card styling */
        .card {
            background-color: rgba(22, 27, 34, 0.7);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Topic pills */
        .topic-pill {
            display: inline-block;
            background: linear-gradient(90deg, #1f6feb, #388bfd);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            margin: 5px;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .topic-pill:hover {
            transform: translateY(-2px) scale(1.05);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            background: linear-gradient(90deg, #388bfd, #1f6feb);
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 15px;
            font-size: 14px;
            color: #8b949e;
            margin-top: 40px;
            background-color: rgba(13, 17, 23, 0.5);
            border-radius: 8px;
            backdrop-filter: blur(8px);
        }
        
        /* Fun loading animation */
        .loading {
            display: inline-block;
            position: relative;
            width: 80px;
            height: 20px;
        }
        
        .loading div {
            position: absolute;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: linear-gradient(135deg, #1f6feb, #388bfd);
            animation: loading 1.2s linear infinite;
        }
        
        .loading div:nth-child(1) {
            animation-delay: 0s;
            left: 8px;
        }
        
        .loading div:nth-child(2) {
            animation-delay: 0.1s;
            left: 32px;
        }
        
        .loading div:nth-child(3) {
            animation-delay: 0.2s;
            left: 56px;
        }
        
        @keyframes loading {
            0% {
                top: 0;
                opacity: 1;
            }
            50% {
                top: 10px;
                opacity: 0.5;
            }
            100% {
                top: 0;
                opacity: 1;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Download required NLTK data
@st.cache_resource
def download_nltk_data():
    nltk.download('punkt')
    nltk.download('wordnet')

download_nltk_data()

# Load BERT
@st.cache_resource
def load_bert():
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    bert_model = BertModel.from_pretrained('bert-base-uncased')
    return tokenizer, bert_model

# Load Model Files
@st.cache_resource
def load_files():
    model = load_model('github_chatbot_model.h5')
    with open('github_words.pkl', 'rb') as f:
        words = pickle.load(f)
    with open('github_classes.pkl', 'rb') as f:
        classes = pickle.load(f)
    with open('github_intents.json', 'r') as f:
        intents = json.load(f)
    return model, words, classes, intents

tokenizer, bert_model = load_bert()
model, words, classes, intents = load_files()

def get_bert_embedding(sentence):
    inputs = tokenizer(sentence, return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        outputs = bert_model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()

def predict_class(sentence):
    embedding = get_bert_embedding(sentence)
    res = model.predict(embedding)[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return [{'intent': classes[r[0]], 'probability': str(r[1])} for r in results]

def get_response(intents_list):
    if not intents_list:
        return "I couldn't find an answer. Can you try rephrasing?"
    tag = intents_list[0]['intent']
    for i in intents['intents']:
        if tag in i['tags']:
            return random.choice(i['responses'])
    return "I'm not sure how to respond to that."

# Initialize Chat History
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "bot", "content": "👋 Hi there! I'm GitBuddy, your friendly GitHub assistant. How can I make your coding journey easier today?"}]

# Initialize first-time animation
if 'first_load' not in st.session_state:
    st.session_state.first_load = True
else:
    st.session_state.first_load = False

# Animated Header
st.markdown('<div class="header"><h1>🐙 GitBuddy</h1><p>Your friendly GitHub assistant powered by AI</p></div>', unsafe_allow_html=True)

# Layout with columns
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    # Profile Card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    octocats = ["Octocat", "Dinotocat", "Spectrocat", "Boxertocat", "Manufacturetocat"]
    octocat = random.choice(octocats)
    st.markdown(f"<h3>Meet {octocat}</h3>", unsafe_allow_html=True)
    st.image("https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", width=100)
    st.markdown("Your AI-powered GitHub guide")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Feature Card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>I'm here to help with:</h3>", unsafe_allow_html=True)
    
    features = [
        "🔄 Git workflows & commands",
        "🔍 Pull request best practices",
        "🏗️ Repository organization",
        "🐞 Issue management",
        "🤝 Contribution guidelines",
        "🚀 GitHub Actions & CI/CD",
        "🔒 Security best practices"
    ]
    
    for feature in features:
        st.markdown(f"<p>{feature}</p>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Action buttons
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>Actions</h3>", unsafe_allow_html=True)
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = [{"role": "bot", "content": "👋 Chat cleared! How can I help you with GitHub today?"}]
        st.rerun()
    
    mood = st.selectbox("🎭 Bot Mood", ["Helpful", "Enthusiastic", "Technical", "Concise"])
    st.markdown(f"<p>Current mood: {mood}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Main Chat UI
with col2:
    # Display Chat in a container
    st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
    
    # Intro animation (only on first load)
    if st.session_state.first_load:
        st.markdown('<div class="loading"><div></div><div></div><div></div></div>', unsafe_allow_html=True)
    
    for i, message in enumerate(st.session_state.messages):
        if message['role'] == "user":
            st.markdown(f'''
                <div class="message-container user-message">
                    <div class="message-bubble user-bubble">{message["content"]}</div>
                    <div class="avatar user-avatar">U</div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
                <div class="message-container bot-message">
                    <div class="avatar bot-avatar">🐙</div>
                    <div class="message-bubble bot-bubble">{message["content"]}</div>
                </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # User Input Area with enhanced styling
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    user_input = st.text_area("", placeholder="Ask me anything about GitHub...", height=100)
    
    cols = st.columns([4, 1])
    with cols[1]:
        st.markdown(f'<button class="send-button">Send 🚀</button>', unsafe_allow_html=True)
        send_button = st.button("Send", key="send_message_button", help="Send your message")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if user_input and send_button:
        st.session_state.messages.append({"role": "user", "content": user_input})
        # Simulate thinking with a slight delay
        response = get_response(predict_class(user_input))
        st.session_state.messages.append({"role": "bot", "content": response})
        st.rerun()

# Right sidebar with interactive elements
with col3:
    # Daily Tip Card with animation
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💡 Git Tip of the Day</h3>", unsafe_allow_html=True)
    
    tips = [
        "Use `git stash` to temporarily store changes you're not ready to commit",
        "Create custom Git aliases for your most-used commands",
        "Try `git bisect` to find which commit introduced a bug",
        "Use branch naming conventions like `feature/`, `bugfix/`, `hotfix/`",
        "Remember to `git pull --rebase` before pushing to avoid messy merge commits",
        "Add `.gitignore` files to exclude build artifacts and dependencies",
        "Use semantic commit messages: 'feat:', 'fix:', 'docs:', etc."
    ]
    
    tip = random.choice(tips)
    st.markdown(f"<p>{tip}</p>", unsafe_allow_html=True)
    if st.button("New Tip 🔄"):
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Popular Topics with interactive pills
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🔥 Popular Topics</h3>", unsafe_allow_html=True)
    
    topics_html = ""
    popular_topics = ["Merge conflicts", "Branch strategy", "Pull requests", "GitHub Actions", "Code reviews", "Gitflow", "Rebasing", "Hooks"]
    for topic in popular_topics:
        topics_html += f'<span class="topic-pill">{topic}</span>'
    
    st.markdown(f"<div style='text-align: center;'>{topics_html}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # GitHub Stats
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>⚡ Quick Facts</h3>", unsafe_allow_html=True)
    
    # Random statistics that update on refresh
    stars = random.randint(1000, 9999)
    commits = random.randint(100, 999)
    forks = random.randint(100, 999)
    
    st.markdown(f"""
        <div style='display: flex; justify-content: space-around; text-align: center;'>
            <div>
                <h2>⭐</h2>
                <p>{stars}</p>
                <small>Stars</small>
            </div>
            <div>
                <h2>🔄</h2>
                <p>{commits}</p>
                <small>Commits</small>
            </div>
            <div>
                <h2>🍴</h2>
                <p>{forks}</p>
                <small>Forks</small>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Animated Footer
st.markdown('<div class="footer">GitBuddy | Made with 💖 and Streamlit | Powered by BERT</div>', unsafe_allow_html=True)