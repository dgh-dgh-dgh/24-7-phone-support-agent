"""Step 1 smoke test: generate speech with the ElevenLabs API and save it as an MP3.

Run from the repo root:  python scripts/hello_voice.py
"""

import os

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

audio = client.text_to_speech.convert(
    text="Thanks for calling screening support. I'm an AI assistant, available 24/7. How can I help?",
    voice_id="JBFqnCBsd6RMkjVDRZzb",  # "George", the example voice from the ElevenLabs docs
    model_id="eleven_v4",
    output_format="mp3_44100_128",
)

# convert() returns an iterator of audio byte chunks
with open("hello.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)

print("Saved hello.mp3")
