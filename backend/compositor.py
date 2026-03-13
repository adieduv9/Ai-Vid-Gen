import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import logging
from typing import Callable

import cv2
import numpy as np
from PIL import Image

from config import (
    OUTPUTS_DIR, VIDEO_WIDTH, VIDEO_HEIGHT,
    AVATAR_WIDTH, AVATAR_HEIGHT,
    CHROMA_KEY_HSV_LOWER, CHROMA_KEY_HSV_UPPER,
    CHROMA_KEY_SPILL_REDUCTION,
)

log = logging.getLogger("compositor")


def composite_avatar(
    avatar_path: str,
    bg_path: str,
    job_id: str,
    removal_mode: str = "ai",
    progress_cb: Callable = lambda p, s: None,
) -> str:
    progress_cb(0.0, "Loading images…")
    bg_img = _load_and_resize_bg(bg_path)

    if removal_mode == "greenscreen":
        progress_cb(0.3, "Applying chroma key…")
        avatar_rgba = _chroma_key_removal(avatar_path)
    else:
        progress_cb(0.3, "Removing background (AI)…")
        avatar_rgba = _ai_removal(avatar_path)

    progress_cb(0.7, "Compositing scene…")
    result = _composite(bg_img, avatar_rgba)

    out_path = str(OUTPUTS_DIR / f"{job_id}_composited.png")
    result.save(out_path, "PNG")
    progress_cb(1.0, "Compositing complete")
    return out_path


def _load_and_resize_bg(path: str) -> Image.Image:
    return Image.open(path).convert("RGBA").resize(
        (VIDEO_WIDTH, VIDEO_HEIGHT), Image.LANCZOS
    )


def _chroma_key_removal(avatar_path: str) -> Image.Image:
    img_bgr = cv2.imread(avatar_path, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise FileNotFoundError(f"Cannot read avatar: {avatar_path}")

    img_rgb    = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    hsv        = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    lo         = np.array(CHROMA_KEY_HSV_LOWER, dtype=np.uint8)
    hi         = np.array(CHROMA_KEY_HSV_UPPER, dtype=np.uint8)
    green_mask = cv2.inRange(hsv, lo, hi)

    kernel     = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_ERODE, kernel, iterations=1)
    green_mask = cv2.GaussianBlur(green_mask, (9, 9), 0)
    alpha      = 255 - green_mask

    if CHROMA_KEY_SPILL_REDUCTION:
        img_rgb = _suppress_spill(img_rgb, green_mask)

    return Image.fromarray(np.dstack([img_rgb, alpha]), "RGBA")


def _suppress_spill(rgb: np.ndarray, green_mask: np.ndarray) -> np.ndarray:
    spill = cv2.dilate(green_mask, None, iterations=3).astype(np.float32) / 255.0
    r = rgb[:,:,0].astype(float)
    g = rgb[:,:,1].astype(float)
    b = rgb[:,:,2].astype(float)
    avg   = (r + b) / 2.0
    g_new = g * (1 - spill) + avg * spill
    out   = rgb.copy()
    out[:,:,1] = np.clip(g_new, 0, 255).astype(np.uint8)
    return out


def _ai_removal(avatar_path: str) -> Image.Image:
    try:
        import io
        from rembg import remove
        with open(avatar_path, "rb") as f:
            raw = f.read()
        return Image.open(io.BytesIO(remove(raw))).convert("RGBA")
    except Exception as exc:
        log.warning("rembg failed (%s), falling back to chroma key", exc)
        return _chroma_key_removal(avatar_path)


def _composite(background: Image.Image, avatar_rgba: Image.Image) -> Image.Image:
    ow, oh  = avatar_rgba.size
    scale   = min(AVATAR_WIDTH / ow, AVATAR_HEIGHT / oh)
    nw, nh  = int(ow * scale), int(oh * scale)
    avatar_rgba = avatar_rgba.resize((nw, nh), Image.LANCZOS)

    shadow = _make_shadow(nw, nh)
    px = (VIDEO_WIDTH - nw) // 2
    py = VIDEO_HEIGHT - nh - 10

    result = background.copy()
    result.paste(shadow,      (px + 6, py + 8), shadow)
    result.paste(avatar_rgba, (px, py),          avatar_rgba)
    return result


def _make_shadow(w: int, h: int) -> Image.Image:
    from PIL import ImageDraw, ImageFilter
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse(
        [(w//4, h - 40), (3*w//4, h - 5)], fill=(0, 0, 0, 90)
    )
    return shadow.filter(ImageFilter.GaussianBlur(12))