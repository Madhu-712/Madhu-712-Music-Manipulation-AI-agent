
#pip install phidata google-generativeai youtube-transcript-api elevenlabs
#pip install streamlit phidata

import streamlit as st
import os
from io import StringIO
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.web import WebTools
from phi.tools.tavily import TavilyTools
from elevenlabs import generate, set_api_key
from Constants import SYSTEM_PROMPT, INSTRUCTIONS

os.environ['TAVILY_API_KEY'] = st.secrets['TAVILY_KEY']
os.environ['GOOGLE_API_KEY'] = st.secrets['GEMINI_KEY']



def get_agent():
    return Agent(
        model=Gemini(id="gemini-2.0-flash-exp" ), # Or the best Gemini model available
        system_prompt=SYSTEM_PROMPT,
        instructions=INSTRUCTIONS,
        tools=[TavilyTools(api_key=os.getenv("TAVILY_API_KEY"))],
        markdown=True,
    )



def generate_audio(text):
    try:
        audio = generate(text=text)
        return audio
    except Exception as e:
        st.error(f"Error generating audio: {e}")
        return None



def download_lyrics(lyrics_content, filename="combined_lyrics.txt"):
    file_stringio = StringIO(lyrics_content)
    st.download_button(
        label="Download Lyrics",
        data=file_stringio,
        file_name=filename,
        mime="text/plain",
    )



def process_input(input_data, target_languages, target_genre, fusion):
    agent = get_agent()
    instruction = {
        "Input": input_data,
        "Target Languages": target_languages,
        "Target Genre": target_genre,
        "Fusion": fusion
    }
    response = agent.run(instruction)
    return response


def main():
    st.title("🎶 LyricMix AI DJ")

    input_method = st.radio("Input Method:", ["YouTube URLs", "Website URLs (Lyrics)", "Text"], index=0)

    input_data = []
    if input_method == "YouTube URLs":
       num_urls = st.number_input("Number of YouTube URLs:", min_value=1, value=1)
       for i in range(num_urls):
            input_data.append(st.text_input(f"YouTube URL {i+1}:"))
        
    elif input_method == "Website URLs (Lyrics)":
         num_urls = st.number_input("Number of Website URLs:", min_value=1, value=1)
         for i in range(num_urls):
            input_data.append(st.text_input(f"Website URL {i+1}:"))
    else:  # Text input
       input_data.append(st.text_area("Enter lyrics:"))


    target_languages = st.multiselect("Target Languages (Optional):", ["Hindi", "Kannada", "Spanish", "French", "German", "Japanese", "etc."])
    target_genre = st.text_input("Target Genre (Optional):")
    fusion = st.checkbox("Fuse Lyrics", value=False)


    if st.button("Process"):
        with st.spinner("Processing..."):
            response = process_input(input_data, target_languages, target_genre, fusion)

            try:
                lyrics_start = response.content.find("```") + 3
                lyrics_end = response.content.find("```", lyrics_start)
                lyrics_content = response.content[lyrics_start:lyrics_end].strip()
                download_lyrics(lyrics_content)

                st.subheader("Audio Generation ")
                if st.button("Generate Audio from Lyrics"):
                    with st.spinner("Generating audio..."):
                        audio_content = generate_audio(lyrics_content)
                        if audio_content:
                            st.audio(audio_content, format="audio/mpeg")

                explanation = (response.content[:lyrics_start-3] + response.content[lyrics_end+3:]).strip()
                st.write(explanation)

            except Exception as e:
                st.error(f"Could not extract lyrics or there are no lyrics returned: {e}")
                st.write(response.content)



if __name__ == "__main__":
    st.set_page_config(
        page_title="LyricMix AI DJ",
        layout="wide",
    )
    main()
