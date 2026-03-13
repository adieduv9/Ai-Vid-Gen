import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import logging
import shutil
from typing import Callable

import cv2
import numpy as np
import soundfile as sf
from moviepy.editor import AudioFileClip, ImageSequenceClip

from config import FRAMES_DIR, OUTPUTS_DIR, VIDEO_FPS, VIDEO_WIDTH, VIDEO_HEIGHT

log = logging.getLogger("animation")

_MOUTH_OUTER = [61,185,40,39,37,0,267,269,270,409,291,375,321,405,314,17,84,181,91,146]


def animate_avatar(
    img_path: str,
    audio_path: str,
    job_id: str,
    progress_cb: Callable = lambda p, s: None,
) -> str:
    progress_cb(0.0, "Loading avatar and audio…")

    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Cannot read composited image: {img_path}")
    img = _fit_to_canvas(img, VIDEO_WIDTH, VIDEO_HEIGHT)

    audio, sr = sf.read(audio_path, always_2d=False)
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    duration     = len(audio) / sr
    total_frames = int(duration * VIDEO_FPS) + 1

    progress_cb(0.05, "Detecting face landmarks…")
    landmarks  = _detect_landmarks(img)
    mouth_data = _extract_mouth_data(landmarks, img.shape) if landmarks else None

    if not landmarks:
        log.warning("No face detected — using fallback animation")

    progress_cb(0.08, "Analysing audio…")
    amplitudes = _compute_amplitudes(audio, sr, total_frames)
    amplitudes = np.convolve(amplitudes, np.ones(3)/3, mode="same")

    frames_dir = FRAMES_DIR / job_id
    frames_dir.mkdir(parents=True, exist_ok=True)

    progress_cb(0.10, f"Rendering {total_frames} frames…")
    frame_paths = []

    for i in range(total_frames):
        amp   = float(amplitudes[i])
        frame = _morph_mouth(img, mouth_data, amp) if mouth_data else _fallback_mouth(img, amp)
        path  = str(frames_dir / f"frame_{i:06d}.png")
        cv2.imwrite(path, frame)
        frame_paths.append(path)
        if i % 25 == 0:
            progress_cb(0.10 + 0.60 * (i / total_frames),
                        f"Rendering frames… ({i}/{total_frames})")

    progress_cb(0.72, "Encoding video…")
    out_path = str(OUTPUTS_DIR / f"{job_id}.mp4")
    _encode_video(frame_paths, audio_path, out_path)
    shutil.rmtree(str(frames_dir), ignore_errors=True)

    progress_cb(1.0, "Animation complete")
    return out_path


def _detect_landmarks(img: np.ndarray):
    try:
        import mediapipe as mp
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        with mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.4,
        ) as fm:
            res = fm.process(rgb)
            if res.multi_face_landmarks:
                return res.multi_face_landmarks[0].landmark
    except ImportError:
        log.warning("mediapipe not installed")
    return None


def _extract_mouth_data(landmarks, img_shape: tuple) -> dict:
    h, w = img_shape[:2]
    def pt(idx):
        lm = landmarks[idx]
        return np.array([int(lm.x * w), int(lm.y * h)])
    outer_pts = np.array([pt(i) for i in _MOUTH_OUTER])
    return {
        "cx": int(outer_pts[:,0].mean()),
        "cy": int(outer_pts[:,1].mean()),
        "bw": int(outer_pts[:,0].ptp() * 1.1),
        "bh": int(outer_pts[:,1].ptp() * 2.5),
    }


def _morph_mouth(img: np.ndarray, mouth: dict, amplitude: float) -> np.ndarray:
    cx, cy, bw, bh = mouth["cx"], mouth["cy"], mouth["bw"], mouth["bh"]
    max_open = int(bh * 0.65)
    open_px  = max(0, min(int(amplitude * max_open), max_open))
    frame    = img.copy()
    pad = 8
    x1 = max(cx - bw//2 - pad, 0)
    x2 = min(cx + bw//2 + pad, img.shape[1])
    y1 = max(cy - bh//2 - pad, 0)
    y2 = min(cy + bh//2 + pad, img.shape[0])
    roi      = img[y1:y2, x1:x2].copy()
    roi_h, roi_w = roi.shape[:2]

    if open_px > 2:
        stretched = cv2.resize(roi, (roi_w, roi_h + open_px), interpolation=cv2.INTER_LINEAR)
        roi_new   = stretched[:roi_h, :]
        rel_cx    = cx - x1
        rel_cy    = cy - y1 + open_px // 2
        cv2.ellipse(roi_new, (rel_cx, rel_cy),
                    (max(2, bw//2 - 4), max(1, open_px//2)),
                    0, 0, 360, (15, 10, 10), -1)
        cv2.ellipse(roi_new, (rel_cx, rel_cy - open_px//4),
                    (max(1, bw//3), max(1, open_px//4)),
                    0, 0, 360, (230, 225, 220), -1)
        frame[y1:y2, x1:x2] = roi_new
    return frame


def _fallback_mouth(img: np.ndarray, amplitude: float) -> np.ndarray:
    frame   = img.copy()
    h, w    = frame.shape[:2]
    cx, cy  = w//2, int(h * 0.68)
    open_px = int(amplitude * 28)
    if open_px > 2:
        cv2.ellipse(frame, (cx, cy), (24, open_px), 0, 0, 360, (15,10,10), -1)
        cv2.ellipse(frame, (cx, cy - open_px//2),
                    (14, max(1, open_px//4)), 0, 0, 360, (220,215,210), -1)
    return frame


def _compute_amplitudes(audio: np.ndarray, sr: int, n_frames: int) -> np.ndarray:
    amps = []
    for i in range(n_frames):
        start = int(i / VIDEO_FPS * sr)
        end   = int((i+1) / VIDEO_FPS * sr)
        seg   = audio[start:end] if end <= len(audio) else audio[start:]
        amps.append(float(np.sqrt(np.mean(seg**2))) if len(seg) > 0 else 0.0)
    arr  = np.array(amps, dtype=np.float32)
    peak = arr.max()
    return arr / peak if peak > 0 else arr


def _encode_video(frame_paths: list, audio_path: str, out_path: str):
    import imageio
    # imageio-ffmpeg must be importable
    try:
        import imageio_ffmpeg
    except ImportError:
        pass

    video = ImageSequenceClip(frame_paths, fps=VIDEO_FPS)
    audio = AudioFileClip(audio_path)
    final = video.set_audio(audio)
    final.write_videofile(
        out_path,
        codec="libx264",
        audio_codec="aac",
        fps=VIDEO_FPS,
        preset="fast",
        ffmpeg_params=["-crf", "22"],
        verbose=False,
        logger=None,
    )
    video.close()
    audio.close()
    final.close()


def _fit_to_canvas(img: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    h, w    = img.shape[:2]
    scale   = min(target_w/w, target_h/h)
    nw, nh  = int(w*scale), int(h*scale)
    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LANCZOS4)
    canvas  = np.zeros((target_h, target_w, 3), dtype=np.uint8)
    ox, oy  = (target_w - nw)//2, (target_h - nh)//2
    canvas[oy:oy+nh, ox:ox+nw] = resized
    return canvas