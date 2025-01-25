
import streamlit as st
import os
from phi.agent import Agent
from phi.model.google import Gemini  # Or your preferred LLM
from phi.tools.youtube_tools import YouTubeTools

os.environ['GOOGLE_API_KEY'] = st.secrets['GEMINI_KEY']


@st.cache_resource
def get_agent():
    return Agent(
        model=Gemini(id="gemini-2.0-flash-exp"),  # Or your preferred LLM
        system_prompt="""You are a helpful assistant that extracts lyrics from YouTube videos, interleaves them, and translates the result into Hindi.  Follow these steps precisely:

        **Step 1: Lyric Extraction:** Extract lyrics from each provided YouTube URL using the YouTube tool.  If lyric extraction fails for any URL, report the error and proceed to the next URL.

        **Step 2: Lyric Interleaving:**  If lyrics were successfully extracted from at least two URLs, interleave the lines. Start with the first line from the first set of lyrics, then the first line from the second set, and so on.  Alternate between lyric sets until all lines are used. If any lyric set is shorter, continue until the longest set is finished.  If interleaving is not possible (e.g., due to inconsistent line lengths or structure), report this and provide the original lyrics separately.

        **Step 3: Hindi Translation:** Translate the interleaved lyrics (or the individual lyrics if interleaving failed) into Hindi.

        Always clearly separate the output for each step.""",
        instructions="""Perform lyric extraction, interleaving, and translation as instructed in the system prompt.""",
        tools=[YouTubeTools()],
        markdown=True,
    )


def extract_and_interleave_lyrics(youtube_urls):
    agent = get_agent()
    try:
        with st.spinner('Processing...'):
            lyrics_data = {}
            for url in youtube_urls:
                response = agent.run(f"Extract lyrics from: {url}")
                if "Error" in response.content:  # Simple error check
                    st.warning(f"Lyric extraction failed for {url}: {response.content}")
                else:
                    lyrics_data[url] = response.content

            if len(lyrics_data) < 2:
                st.warning("At least two URLs with lyrics are required for interleaving.")
                for url, lyrics in lyrics_data.items():
                    st.markdown(f"**Lyrics from {url}:**\n{lyrics}")
                return #Exit early if not enough data

            #Interleaving Logic (same as before, but more robust error handling could be added here)
            #... [Interleaving Logic from previous response] ...

    except Exception as e:
        st.error(f"An error occurred: {e}")

def main():
    st.title("Lyric Interleaving and Translation App")
    youtube_urls = st.text_area("Enter YouTube URLs (one per line):", height=150)
    urls = [url.strip() for url in youtube_urls.splitlines() if url.strip()]

    if st.button("Extract and Interleave"):
        extract_and_interleave_lyrics(urls)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Lyric Interleaving App",
        layout="wide",
    )
    main()
