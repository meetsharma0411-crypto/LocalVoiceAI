# 🎙️ LocalVoiceAI — Local Hindi Voice Assistant

A locally running AI voice assistant built with **Django, Ollama, Gemma, Faster-Whisper, and Piper TTS**. It can understand spoken Hindi, generate AI responses locally, and reply using a Hindi voice.

The goal is to run an AI assistant on your own computer without depending on paid cloud AI APIs.

## ✨ Features

- 🎤 Voice input through the browser microphone
- 🗣️ Hindi speech recognition using Faster-Whisper
- 🧠 Local AI responses using Ollama and Gemma 3 (1B)
- 🔊 Hindi text-to-speech using Piper TTS
- 💬 Text-based chat interface
- 👂 Experimental wake-word listening mode
- 🌐 Django-based web application
- 🔒 Local processing after required models and dependencies are downloaded

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Django | Web application and backend |
| Ollama | Local AI model runtime |
| Gemma 3 (1B) | AI response generation |
| Faster-Whisper | Speech recognition |
| Piper TTS | Hindi speech generation |
| HTML, CSS, JavaScript | Web interface |

## 📁 Project Structure

```text
LocalVoiceAI/
├── assistant/
│   ├── templates/
│   │   └── assistant/
│   │       └── chat.html
│   ├── urls.py
│   └── views.py
├── VoiceProject/
│   ├── settings.py
│   └── urls.py
├── models/
├── media/
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

*The exact folder structure may vary depending on your local setup.*

## 💻 Requirements

- Windows 10/11 or another compatible operating system
- Python 3.12 recommended for this project
- Ollama
- Internet connection for initial installation and model downloads
- Microphone and browser microphone permission
- Sufficient RAM and disk space for the AI models

## 🚀 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/meetsharma0411-crypto/LocalVoiceAI.git
cd LocalVoiceAI
```

### 2. Create a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

If `requirements.txt` is not available, install the required packages individually:

```powershell
pip install django requests faster-whisper piper-tts
```

### 4. Install and start Ollama

Install Ollama from https://ollama.com/

Download the Gemma model:

```powershell
ollama pull gemma3:1b
```

Ensure Ollama is running locally and the model is available:

```powershell
ollama list
```

### 5. Configure the Hindi Piper voice

Download the appropriate Piper Hindi voice model and its matching `.onnx.json` configuration file.

Place the files in the location expected by `assistant/views.py`. For example:

```text
models/
└── hi_IN-pratham-medium.onnx
    hi_IN-pratham-medium.onnx.json
```

Also ensure the Piper executable is installed and accessible from the active virtual environment.

### 6. Run Django migrations

```powershell
python manage.py migrate
```

### 7. Start the development server

```powershell
python manage.py runserver
```

Open the application in your browser:

http://127.0.0.1:8000/

Allow microphone access when prompted.

## 🎤 How to Use

1. Start the Django server and Ollama.
2. Open the application in your browser.
3. Type a message or use the microphone button.
4. Speak in Hindi and wait for transcription.
5. The local Gemma model generates a response.
6. Piper generates the spoken Hindi reply.
7. Try the experimental wake-word mode if enabled.

## 🔐 Privacy

The application is designed for local inference using Ollama, Faster-Whisper, and Piper. After initial setup and model downloads, these components can operate locally.

However, microphone access, browser behavior, and any additional network requests should be reviewed before claiming the entire application is fully offline.

## ⚠️ Current Limitations

- Response speed depends on available CPU, RAM, and hardware.
- Speech recognition accuracy depends on microphone quality and background noise.
- Wake-word detection uses speech transcription and may not be instantaneous.
- Hindi voice output requires a compatible Piper voice model.
- A newly cloned repository may require downloading model files separately.

## 🗺️ Future Improvements

- Improve wake-word detection
- Add multilingual support for Hindi, Gujarati, and English
- Add conversation history
- Improve error handling and user feedback
- Add a configurable offline setup process
- Add automated tests and installation documentation

## 👨‍💻 Author

**Meet Sharma**

GitHub: https://github.com/meetsharma0411-crypto

## 📄 License

Choose a license before distributing this project publicly. Also review the licenses of the AI models, voice models, and dependencies used by the application.
