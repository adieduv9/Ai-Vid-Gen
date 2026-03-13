import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import gc
import logging
from typing import Callable

from compositor import composite_avatar
from tts_engine import generate_tts
from animation_engine import animate_avatar

log = logging.getLogger("pipeline")


def run_pipeline(
    avatar_path: str,
    bg_path: str,
    script: str,
    job_id: str,
    voice: str,
    removal_mode: str,
    speaking_rate: float,
    progress_cb: Callable,
) -> str:

    # STAGE 1 — Compositing
    progress_cb(8, "Removing background…")
    log.info("[%s] Stage 1: compositing", job_id)
    composited_path = composite_avatar(
        avatar_path=avatar_path,
        bg_path=bg_path,
        job_id=job_id,
        removal_mode=removal_mode,
        progress_cb=lambda p, s: progress_cb(8 + int(p * 0.22), s),
    )
    gc.collect()

    # STAGE 2 — TTS
    progress_cb(30, "Synthesising voice…")
    log.info("[%s] Stage 2: TTS", job_id)
    audio_path = generate_tts(
        script=script,
        job_id=job_id,
        voice=voice,
        speaking_rate=speaking_rate,
        progress_cb=lambda p, s: progress_cb(30 + int(p * 0.10), s),
    )
    gc.collect()

    # STAGE 3 — Animation
    progress_cb(40, "Animating avatar…")
    log.info("[%s] Stage 3: animation", job_id)
    video_path = animate_avatar(
        img_path=composited_path,
        audio_path=audio_path,
        job_id=job_id,
        progress_cb=lambda p, s: progress_cb(40 + int(p * 0.55), s),
    )
    gc.collect()

    progress_cb(98, "Finalising video…")
    return video_path