import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
import logging
from typing import Callable

import edge_tts

from config import AUDIO_DIR, DEFAULT_VOICE

log = logging.getLogger("tts")


def generate_tts(
    script: str,
    job_id: str,
    voice: str = DEFAULT_VOICE,
    speaking_rate: float = 1.0,
    progress_cb: Callable = lambda p, s: None,
) -> str:
    progress_cb(0.0, "Preparing TTS…")
    rate_pct = _rate_to_percent(speaking_rate)
    out_path = str(AUDIO_DIR / f"{job_id}.mp3")

    progress_cb(0.2, f"Synthesising with voice: {voice}…")
    asyncio.run(_synthesise(script, voice, rate_pct, out_path))

    progress_cb(1.0, "Audio synthesis complete")
    log.info("TTS → %s", out_path)
    return out_path


async def _synthesise(text: str, voice: str, rate: str, out_path: str):
    await edge_tts.Communicate(text, voice, rate=rate).save(out_path)


def _rate_to_percent(rate: float) -> str:
    pct = int((rate - 1.0) * 100)
    return f"+{pct}%" if pct >= 0 else f"{pct}%"