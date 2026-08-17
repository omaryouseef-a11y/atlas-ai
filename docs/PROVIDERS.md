# Optional Providers

The core test and example workflow uses no cloud provider. Install extras individually; do not install every integration by default.

| Extra | Legacy integration | Configuration | Data/network note |
|---|---|---|---|
| `ai` | CrewAI and Gemini examples | `GEMINI_API_KEY` | Prompts/content may leave the machine and may incur cost |
| `video` | Fal.ai video and MoviePy utilities | `FAL_API_KEY` | Prompts and generated media use external services/runtime |
| `audio` | gTTS | none/API behavior | Text is sent to an external TTS service |
| `youtube` | Google OAuth and YouTube upload | user-provided `client_secrets.json` | Upload is external and publishing is disabled by default |
| `whisper` | local Whisper transcription | local model | May download large model files; never done by CI |

Example: `python -m pip install -e '.[video]'`.

Credentials are read from environment variables or provider credential files only. Do not commit `.env`, OAuth files, tokens, generated content, or databases. OAuth tokens are stored as JSON with mode `0600`; treat them as secrets. Missing configuration must produce `NOT_CONFIGURED` or `PROVIDER_UNAVAILABLE`, never a fabricated URL, identifier, or media file.

Provider APIs and model names are legacy and may need verification before use. Add bounded timeouts, cost limits, and manual confirmation before any real call.
