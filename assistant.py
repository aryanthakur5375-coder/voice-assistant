import speech_recognition as sr
import os
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import io
import asyncio
import edge_tts
import tempfile
import playsound
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ API key not found. Check your .env file")

client_ai = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

async def async_speak(text):
    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice="en-IN-NeerjaNeural"
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            temp_file = f.name

        await communicate.save(temp_file)
        playsound.playsound(temp_file)

        # 🧹 delete file after playing
        os.remove(temp_file)

    except Exception as e:
        print("TTS Error:", e)

def clean_text(text):
    text = re.sub(r'\*\*|\*|#|`', '', text)
    text = re.sub(r'\n+', '. ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def speak(text):
    clean = clean_text(text)
    print(f"Assistant: {clean}")

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(async_speak(clean))
        else:
            loop.run_until_complete(async_speak(clean))
    except RuntimeError:
        asyncio.run(async_speak(clean))

def ask_ai(prompt):
    try:
        response = client_ai.chat.completions.create(
            model="google/gemma-4-26b-a4b-it:free",
            messages=[
                {"role": "system", "content": "Give short, clear answers in plain English."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        print("AI Error:", e)
        return "AI_ERROR"


def listen():
    recognizer = sr.Recognizer()

    # 🎤 Better mic sensitivity
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    fs = 44100
    seconds = 5

    try:
        print("🎤 Listening...")

        recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()

        byte_io = io.BytesIO()
        write(byte_io, fs, recording)

        audio_data = sr.AudioData(byte_io.getvalue(), fs, 2)

        print("🔍 Recognizing...")
        query = recognizer.recognize_google(audio_data, language='en-in')

        print(f"👤 You said: {query}")
        return query.lower()

    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return "none"

    except sr.RequestError:
        print("❌ Internet error")
        return "none"

    except Exception as e:
        print("❌ Error:", e)
        return "none"