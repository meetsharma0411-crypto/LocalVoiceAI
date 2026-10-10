import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from faster_whisper import WhisperModel


BASE_DIR = Path(settings.BASE_DIR)
MODEL_DIR = BASE_DIR / "models"
WHISPER_DIR = MODEL_DIR / "whisper"
MEDIA_DIR = BASE_DIR / "media"

WHISPER_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# Hindi Piper model files नीचे दिए गए setup steps से डाउनलोड करें।
PIPER_MODEL = MODEL_DIR / "hi_IN-pratham-medium.onnx"

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "gemma3:1b"

_whisper = None


def get_whisper():
    """Load the local speech recognition model once."""
    global _whisper

    if _whisper is None:
        _whisper = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8",
            download_root=str(WHISPER_DIR),
        )

    return _whisper


def transcribe_audio(audio_file):
    """Transcribe the uploaded audio file to Hindi text."""
    suffix = Path(audio_file.name).suffix or ".webm"
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=suffix, delete=False
        ) as temp:
            for chunk in audio_file.chunks():
                temp.write(chunk)
            temp_path = temp.name

        model = get_whisper()

        segments, info = model.transcribe(
            temp_path,
            language="hi",
            beam_size=1,
            vad_filter=True,
        )

        return " ".join(
            segment.text.strip() for segment in segments
        ).strip()

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def ask_gemma(message):
    """Ask the local Ollama model for a Hindi response."""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "आप एक उपयोगी स्थानीय हिंदी वॉइस असिस्टेंट हैं। "
                        "हमेशा सरल हिंदी में देवनागरी लिपि में जवाब दें। "
                        "हिंदी और Hinglish में पूछे गए प्रश्न समझें। "
                        "जवाब स्पष्ट और संक्षिप्त रखें।"
                    ),
                },
                {"role": "user", "content": message},
            ],
            "stream": False,
        },
        timeout=180,
    )

    response.raise_for_status()
    return response.json()["message"]["content"].strip()


def speak_hindi(text):
    """Generate a WAV file using the configured local Piper voice."""

    if not PIPER_MODEL.exists():
        raise FileNotFoundError(
            f"Hindi Piper model not found: {PIPER_MODEL}"
        )

    piper_exe = shutil.which("piper")

    if not piper_exe:
        import sys
        scripts_dir = Path(sys.executable).parent
        piper_path = scripts_dir / "piper.exe"

        if not piper_path.exists():
            raise FileNotFoundError(
                "Piper executable not found in the active venv."
            )

        piper_exe = str(piper_path)

    output_file = MEDIA_DIR / "response.wav"

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    subprocess.run(
        [
            piper_exe,
            "--model", str(PIPER_MODEL),
            "--output_file", str(output_file),
        ],
        input=text.encode("utf-8"),
        capture_output=True,
        timeout=120,
        check=True,
        env=env,
    )

    return "/media/response.wav"

def chat_page(request):
    return render(request, "assistant/chart.html")


def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    message = request.POST.get("message", "").strip()

    if not message:
        return JsonResponse(
            {"error": "कृपया अपना प्रश्न लिखें।"},
            status=400,
        )

    try:
        answer = ask_gemma(message)
        return JsonResponse({"reply": answer})

    except requests.RequestException as error:
        return JsonResponse(
            {"error": f"Ollama connection failed: {error}"},
            status=503,
        )


def voice_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    audio_file = request.FILES.get("audio")
    mode = request.POST.get("mode", "command")

    if audio_file is None:
        return JsonResponse(
            {"error": "Microphone audio नहीं मिला।"},
            status=400,
        )

    try:
        transcript = transcribe_audio(audio_file)

        if not transcript:
            return JsonResponse({
                "transcript": "",
                "message": "आवाज़ समझ नहीं आई। फिर से बोलें।",
            })

        # Wake phrase is checked in the locally transcribed text.
        wake_pattern = (
            r"\b(?:hey assistant|hey assistance|हे असिस्टेंट|"
            r"हे असिस्टन्ट)\b"
        )
        wake_match = re.search(
            wake_pattern, transcript, re.IGNORECASE
        )

        if mode == "listen":
            if not wake_match:
                return JsonResponse({
                    "transcript": transcript,
                    "wake_detected": False,
                })

            message = transcript[wake_match.end():].strip(
                " ,.!?।"
            )

            if not message:
                return JsonResponse({
                    "transcript": transcript,
                    "wake_detected": True,
                    "waiting_for_command": True,
                })
        else:
            message = transcript

        answer = ask_gemma(message)
        audio_url = speak_hindi(answer)

        return JsonResponse({
            "transcript": transcript,
            "reply": answer,
            "audio_url": audio_url,
            "wake_detected": bool(wake_match),
        })

    except requests.RequestException as error:
        return JsonResponse(
            {"error": f"Ollama connection failed: {error}"},
            status=503,
        )
    except subprocess.CalledProcessError as error:
        detail = error.stderr[-1000:] if error.stderr else ""
        return JsonResponse({
            "error": "Hindi voice generate नहीं हुई। Piper model जाँचें।",
            "details": detail,
        }, status=500)
    except Exception as error:
        return JsonResponse({
            "error": f"{type(error).__name__}: {error}"
        }, status=500)