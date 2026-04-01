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
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"] 

@st.cache_data(ttl=3600) # Caches the data for 1 hour so you don't overuse the free AI API
def get_ai_summary(text):
    """Sends the article to a free AI model for a bulleted summary."""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://ai-news-dashboard.streamlit.app", # Tells OpenRouter who you are
                "X-Title": "AI News Dashboard"
            },
            data=json.dumps({
               "model": "openrouter/free",
                "messages": [{"role": "user", "content": f"Summarize this AI news update in a short summary:\n\n{text}"}]
            })
        )
        
        response_data = response.json()
        
        # If there's an error from OpenRouter, this will catch it and show it to you!
        if "error" in response_data:
            return f"API Error: {response_data['error']['message']}"
            
        return response_data['choices'][0]['message']['content']
        
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
