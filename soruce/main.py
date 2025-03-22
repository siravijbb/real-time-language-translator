import os
import time
import streamlit as st
import speech_recognition as sr
from googletrans import LANGUAGES, Translator
import asyncio

isTranslateOn = False

translator = Translator()  # Initialize the translator module.

# Create a mapping between language names and language codes
language_mapping = {name: code for code, name in LANGUAGES.items()}

def get_language_code(language_name):
    return language_mapping.get(language_name, language_name)

async def translator_function(spoken_text, from_language, to_language):
    loop = asyncio.get_event_loop()
    translated_text = await loop.run_in_executor(None, lambda: translator.translate(spoken_text, src=from_language, dest=to_language))
    return translated_text.text

async def main_process(output_placeholder, from_language, to_language, mic_index):

    global isTranslateOn
    translated_texts = []
    current_text = ""

    while isTranslateOn:

        rec = sr.Recognizer()
        with sr.Microphone(device_index=mic_index) as source:
            rec.pause_threshold = 1
            audio = rec.listen(source, phrase_time_limit=15)

        try:
            spoken_text = rec.recognize_google(audio, language=from_language)

            current_text = "Translating...\n\n" + current_text
            output_placeholder.text(current_text)

            translated_text = await translator_function(spoken_text, from_language, to_language)
            translated_texts.append(translated_text)

            current_text = translated_text + "\n\n" + current_text
            output_placeholder.text(current_text)

        except Exception as e:
            print(e)

# UI layout
st.title("Language Translator")

# Dropdowns for selecting languages
from_language_name = st.selectbox("Select Source Language:", list(LANGUAGES.values()))
to_language_name = st.selectbox("Select Target Language:", list(LANGUAGES.values()))

# Convert language names to language codes
from_language = get_language_code(from_language_name)
to_language = get_language_code(to_language_name)

# List available microphones
mic_list = sr.Microphone.list_microphone_names()
mic_index = st.selectbox("Select Microphone:", range(len(mic_list)), format_func=lambda x: mic_list[x])

# Button to trigger translation
start_button = st.button("Start")
stop_button = st.button("Stop")

# Check if "Start" button is clicked
if start_button:
    if not isTranslateOn:
        isTranslateOn = True
        output_placeholder = st.empty()
        asyncio.run(main_process(output_placeholder, from_language, to_language, mic_index))

# Check if "Stop" button is clicked
if stop_button:
    isTranslateOn = False