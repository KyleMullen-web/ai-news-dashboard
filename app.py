import time
import streamlit as st
import feedparser
import requests
import json

# --- CONFIGURATION ---
# We use official RSS feeds to gather news for free
RSS_FEEDS = [
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
    all_news_text = ""
    articles = []

    # 1. Collect all titles first
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            articles.append(entry)
            all_news_text += f"Title: {entry.title}\nContent: {entry.summary if 'summary' in entry else entry.title}\n---\n"

    # 2. Send ONE single request to Gemini for everything
    for entry in feed.entries[:4]:
        with st.container():
        st.markdown(f"### [{entry.title}]({entry.link})")

        # This tiny pause prevents the "Quota Exceeded" error!
        time.sleep(4) 

        with st.spinner("AI is generating summary..."):
            # ... your existing summary code ...
    with st.spinner("AI is summarizing the entire feed..."):
        combined_summary = get_ai_summary(f"Here is a list of news. Provide a short summary for EACH individual story separately:\n\n{all_news_text}")
    
    # 3. Display the big summary
    st.markdown("### 📰 Today's AI Briefing")
    st.info(combined_summary)
    
    st.divider()
    st.markdown("🔗 **Original Sources:**")
    for art in articles:
        st.write(f"- [{art.title}]({art.link})")
        
        # Grab the top 2 most recent articles from each source
        for entry in feed.entries[:2]:
            with st.container():
                st.markdown(f"### [{entry.title}]({entry.link})")
                
                with st.spinner("AI is generating summary..."):
                    content_to_summarize = entry.summary if 'summary' in entry else entry.title
                    summary = get_ai_summary(content_to_summarize)
                    st.info(summary)
                st.divider()
