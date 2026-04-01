import streamlit as st
import feedparser
import requests
import json

# --- CONFIGURATION ---
# We use official RSS feeds to gather news for free
RSS_FEEDS = [
    "https://openai.com/news/rss.xml",
    "https://blog.google/technology/ai/rss/",
    "https://techcrunch.com/category/artificial-intelligence/feed/"
]

# The API key will be securely stored in Streamlit Cloud secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"] 

@st.cache_data(ttl=3600)
def get_ai_summary(text):
    """Sends the article directly to Google's Gemini API for a summary."""
    try:
        # We are using Gemini 2.0 Flash, which is incredibly fast and free in AI Studio
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": f"Summarize this AI news update in a short summary:\n\n{text}"}]}]
        }
        
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
        response_data = response.json()
        
        # Catch any Google-specific errors
        if "error" in response_data:
            return f"Google API Error: {response_data['error']['message']}"
            
        # Extract the text from Google's specific response format
        return response_data['candidates'][0]['content']['parts'][0]['text']
        
    except Exception as e:
        return f"System Error: {str(e)}"

# --- USER INTERFACE ---
st.set_page_config(page_title="AI Pulse", page_icon="🤖", layout="centered")
st.title("🤖 Free AI News Dashboard")
st.markdown("Gathering the latest AI updates and summarizing them using free open-source models.")

if st.button("Fetch Latest News"):
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        st.subheader(f"📡 {feed.feed.title}")
        
        # Grab the top 2 most recent articles from each source
        for entry in feed.entries[:2]:
            with st.container():
                st.markdown(f"### [{entry.title}]({entry.link})")
                
                with st.spinner("AI is generating summary..."):
                    content_to_summarize = entry.summary if 'summary' in entry else entry.title
                    summary = get_ai_summary(content_to_summarize)
                    st.info(summary)
                st.divider()
