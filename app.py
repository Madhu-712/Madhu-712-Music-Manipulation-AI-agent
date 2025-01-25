

import streamlit as st
import os
from PIL import Image
from io import BytesIO
from phi.agent import Agent
from phi.model.google import Gemini  # Or your preferred LLM
from phi.tools.tavily import TavilyTools # Or your preferred translation tool
from tempfile import NamedTemporaryFile
from constants import SYSTEM_PROMPT, INSTRUCTIONS
# Placeholder for YouTube lyric extraction; replace with actual implementation
from youtube_lyrics_extractor import extract_lyrics_from_youtube # Hypothetical function

os.environ['TAVILY_API_KEY'] = st.secrets['TAVILY_KEY'] # Replace with your API Key
os.environ['GOOGLE_API_KEY'] = st.secrets['GEMINI_KEY'] # Replace with your API Key

# ... (resize_image_for_display function remains the same) ...

@st.cache_resource
def get_agent():
    return Agent(
        model=Gemini(id="gemini-2.0-flash-exp"), # Or your preferred LLM
        system_prompt=SYSTEM_PROMPT,
        instructions=INSTRUCTIONS,
        tools=[TavilyTools(api_key=os.getenv("TAVILY_API_KEY"))], # Or your preferred translation tool
        markdown=True,
    )

def analyze_lyrics(youtube_urls):
    agent = get_agent()
    lyrics_list = []
    for url in youtube_urls:
        try:
            lyrics = extract_lyrics_from_youtube(url)
            lyrics_list.append(lyrics)
        except Exception as e:
            st.error(f"Error processing YouTube URL {url}: {e}")
            return None
    if not lyrics_list:
        st.error("No lyrics could be extracted.")
        return None

    lyrics_input = "\n\n".join(lyrics_list)
    with st.spinner('Processing lyrics...'):
        response = agent.run(
            f"Process these lyrics: \n{lyrics_input}",
        )
        st.markdown(response.content)

def main():
    st.title("Lyric Fusion & Translation App")

    youtube_urls = st.text_area("Enter YouTube video URLs (one per line):", height=150)
    urls = [url.strip() for url in youtube_urls.splitlines() if url.strip()]

    if st.button("Analyze Lyrics"):
        analyze_lyrics(urls)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Lyric Fusion App",
        layout="wide",
    )
    main()
