from pathlib import Path

# When run as package from project root, __file__ is backend/config.py
# BASE_DIR must point to the project root (parent of backend/)
BASE_DIR   = Path(__file__).parent.parent
DATA_DIR   = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

AVATARS_DIR     = DATA_DIR / "avatars"
BACKGROUNDS_DIR = DATA_DIR / "backgrounds"
INPUTS_DIR      = DATA_DIR / "inputs"
FRAMES_DIR      = DATA_DIR / "frames"
AUDIO_DIR       = DATA_DIR / "audio"
OUTPUTS_DIR     = DATA_DIR / "outputs"

for _d in [AVATARS_DIR, BACKGROUNDS_DIR, INPUTS_DIR,
           FRAMES_DIR, AUDIO_DIR, OUTPUTS_DIR, MODELS_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

VIDEO_FPS    = 25
VIDEO_WIDTH  = 1280
VIDEO_HEIGHT = 720
AVATAR_WIDTH  = 520
AVATAR_HEIGHT = 840

AVAILABLE_VOICES: dict = {
    "en-US-AriaNeural":     "Aria — US Female (Friendly)",
    "en-US-GuyNeural":      "Guy — US Male (Casual)",
    "en-US-JennyNeural":    "Jenny — US Female (Professional)",
    "en-US-EricNeural":     "Eric — US Male (Smooth)",
    "en-US-MichelleNeural": "Michelle — US Female (Warm)",
    "en-GB-SoniaNeural":    "Sonia — UK Female (Elegant)",
    "en-GB-RyanNeural":     "Ryan — UK Male (Deep)",
    "en-AU-NatashaNeural":  "Natasha — AU Female (Bright)",
    "en-IN-NeerjaNeural":   "Neerja — IN Female (Clear)",
}
DEFAULT_VOICE = "en-US-AriaNeural"

CHROMA_KEY_HSV_LOWER = (35, 50, 50)
CHROMA_KEY_HSV_UPPER = (85, 255, 255)
CHROMA_KEY_SPILL_REDUCTION = True