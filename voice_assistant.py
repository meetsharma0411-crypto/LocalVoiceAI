import sys
import time
import subprocess
from pathlib import Path

import requests
import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel

# Project settings
BASE_DIR = Path(__file__).resolve().parent
VOICE_DIR = BASE_DIR / "voices"
INPUT_FILE = BASE_DIR / "input.wav"
OUTPUT_FILE = BASE_DIR / "assistant.wav"

HINDI_VOICE = VOICE_DIR / "hi_IN-pratham-medium.onnx"
ENGLISH_VOICE = VOICE_DIR / "en_US-lessac-medium.onnx"

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "gemma3:1b"

SAMPLE_RATE = 16000
RECORD_SECONDS = 6

print("=" * 50)
print("LOCAL AI VOICE ASSISTANT")
print("Hindi | English | Hinglish | Gujlish")
print("=" * 50)

# Check voice files
if not HINDI_VOICE.exists():
    raise FileNotFoundError(
        f"Hindi voice not found: {HINDI_VOICE}"
    )

if not ENGLISH_VOICE.exists():
    raise FileNotFoundError(
        f"English voice not found: {ENGLISH_VOICE}"
    )

# Load speech recognition model
print("\nLoading Whisper model...")
whisper = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)
print("Whisper ready!")

# Check Ollama
try:
    response = requests.get(
        "http://localhost:11434/api/tags",
        timeout=5
    )
    response.raise_for_status()
    print("Ollama ready!")
except requests.RequestException as error:
    raise RuntimeError(
        "Ollama is not responding. Start Ollama and try again."
    ) from error


def record_audio():
    input(
        "\nEnter dabavo ane bolo "
        "(6 seconds recording, quit mate q): "
    )

    print("Recording... Speak now!")

    audio = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )
    sd.wait()

    write(str(INPUT_FILE), SAMPLE_RATE, audio)
    print("Recording complete.")


def recognize_speech():
    segments, info = whisper.transcribe(
        str(INPUT_FILE),
        beam_size=3
    )

    text = " ".join(
        segment.text.strip() for segment in segments
    ).strip()

    print("Detected language:", info.language)
    print("You said:", text)

    return text, info.language


def ask_gemma(user_text):
    system_prompt = """
You are a helpful local voice assistant.
Understand Hindi, Gujarati, English, Hinglish and Gujlish.
Reply in the same language and style as the user's message.
Use simple, natural, short responses.
For Hindi, use Devanagari script.
For English, use English.
For Hinglish and Gujlish, keep the user's conversational style.
Do not claim you performed actions you did not perform.
"""

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        "stream": False,
        "options": {"temperature": 0.4}
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=180
    )
    response.raise_for_status()

    answer = response.json()["message"]["content"].strip()
    return answer


def speak(text, language):
    # English uses English voice.
    # Other languages currently use Hindi voice.
    if language == "en":
        voice_model = ENGLISH_VOICE
    else:
        voice_model = HINDI_VOICE

    command = [
        sys.executable, "-m", "piper",
        "--model", str(voice_model),
        "--output_file", str(OUTPUT_FILE),
        "--", text
    ]

    subprocess.run(command, check=True)
    # Wait until the generated WAV has finished playing.
    # Windows opens the file in its default audio player.
    subprocess.Popen(["cmd", "/c", "start", "", str(OUTPUT_FILE)])


try:
    while True:
        command_text = input(
            "\nEnter dabavo to talk, or q to quit: "
        ).strip().lower()

        if command_text == "q":
            print("Assistant stopped.")
            break

        try:
            print("\nSpeak in 6 seconds.")
            audio = sd.rec(
                int(RECORD_SECONDS * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="int16"
            )
            sd.wait()
            write(str(INPUT_FILE), SAMPLE_RATE, audio)

            segments, info = whisper.transcribe(
                str(INPUT_FILE),
                beam_size=3
            )
            user_text = " ".join(
                segment.text.strip() for segment in segments
            ).strip()

            if not user_text:
                print("Speech not detected. Please try again.")
                continue

            print("Detected language:", info.language)
            print("You:", user_text)

            print("Gemma is thinking...")
            answer = ask_gemma(user_text)
            print("Assistant:", answer)

            speak(answer, info.language)

        except requests.RequestException as error:
            print("Ollama connection/API error:", error)
        except subprocess.CalledProcessError as error:
            print("Piper voice error:", error)
        except Exception as error:
            print("Error:", error)

except KeyboardInterrupt:
    print("\nAssistant stopped.")