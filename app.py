import streamlit as st
import feedparser
import requests
import json
import time

# --- 1. CONFIGURATION ---
# You can add or remove URLs inside these brackets. 
# Ensure every URL (except the last one) has a comma after it.
RSS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/"
]

# Pulls your Google API Key from Streamlit Cloud Secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "missing")

@st.cache_data(ttl=3600)
def get_ai_summary(text):
    """Sends the article directly to Google's Gemini API for a summary."""
    if GEMINI_API_KEY == "MISSING":
        return "Error: GEMINI_API_KEY not found in Secrets."
        
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"Summarize this AI news update in a short summary:\n\n{text}"}]
            }]
        }
        
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
        response_data = response.json()
        
        if "error" in response_data:
            return f"Google API Error: {response_data['error']['message']}"
            
        return response_data['candidates'][0]['content']['parts'][0]['text']
        
    except Exception as e:
        return f"System Error: {str(e)}"

# --- 2. USER INTERFACE ---
st.set_page_config(page_title="AI Pulse Dashboard", page_icon="🤖", layout="wide")

st.title("🤖 My Personal AI News Hub")
st.write("Fetching and summarizing the latest in Artificial Intelligence...")

# The "Fetch" Button logic
if st.button("Fetch Latest News"):
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        st.subheader(f"📡 Source: {feed.feed.title}")
        
        # We loop through the top 3 articles from each source
        for entry in feed.entries[:3]:
            with st.container():
                st.markdown(f"### [{entry.title}]({entry.link})")
                
                # We wait 2 seconds to avoid the "Quota Exceeded" error
                time.sleep(2)
                
                with st.spinner("Gemini is reading..."):
                    # Use summary if available, otherwise use the title
                    content = entry.summary if 'summary' in entry else entry.title
                    summary_text = get_ai_summary(content)
                    st.info(summary_text)
                
                st.divider()

# Footer
st.caption("Built with Streamlit and Google Gemini 2.0")
