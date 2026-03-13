import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
import json
import uuid
from pathlib import Path
from typing import AsyncGenerator

import aiofiles
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

from config import AVATARS_DIR, BACKGROUNDS_DIR, OUTPUTS_DIR, AVAILABLE_VOICES
from pipeline import run_pipeline

app = FastAPI(title="StudioAvatarAI", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_jobs: dict = {}


def _update(job_id: str, progress: int, step: str, status: str = "running"):
    _jobs[job_id] = {"status": status, "progress": progress, "step": step, "error": None}


@app.get("/voices")
async def list_voices():
    return {"voices": AVAILABLE_VOICES}


@app.post("/generate")
async def generate_avatar(
    avatar: UploadFile = File(...),
    background: UploadFile = File(...),
    script: str = Form(...),
    voice: str = Form("en-US-AriaNeural"),
    removal_mode: str = Form("ai"),
    speaking_rate: float = Form(1.0),
):
    if voice not in AVAILABLE_VOICES:
        voice = "en-US-AriaNeural"

    job_id = str(uuid.uuid4())
    _update(job_id, 0, "Initialising job…")

    avatar_ext = Path(avatar.filename).suffix or ".png"
    bg_ext     = Path(background.filename).suffix or ".png"
    avatar_path = AVATARS_DIR / f"{job_id}_avatar{avatar_ext}"
    bg_path     = BACKGROUNDS_DIR / f"{job_id}_bg{bg_ext}"

    async with aiofiles.open(avatar_path, "wb") as f:
        await f.write(await avatar.read())
    async with aiofiles.open(bg_path, "wb") as f:
        await f.write(await background.read())

    _update(job_id, 5, "Files uploaded")

    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        None, _run_pipeline_sync,
        job_id, str(avatar_path), str(bg_path),
        script, voice, removal_mode, speaking_rate,
    )

    return {"job_id": job_id, "message": "Processing started"}


def _run_pipeline_sync(job_id, avatar_path, bg_path,
                       script, voice, removal_mode, speaking_rate):
    try:
        def progress_cb(pct: int, label: str):
            _update(job_id, pct, label)

        output = run_pipeline(
            avatar_path=avatar_path,
            bg_path=bg_path,
            script=script,
            job_id=job_id,
            voice=voice,
            removal_mode=removal_mode,
            speaking_rate=speaking_rate,
            progress_cb=progress_cb,
        )
        _jobs[job_id] = {
            "status": "done",
            "progress": 100,
            "step": "Video ready!",
            "error": None,
            "output": output,
        }
    except Exception as exc:
        import traceback
        traceback.print_exc()
        _jobs[job_id] = {
            "status": "error",
            "progress": 0,
            "step": "Failed",
            "error": str(exc),
        }


@app.get("/progress/{job_id}")
async def stream_progress(job_id: str):
    async def event_generator() -> AsyncGenerator[str, None]:
        while True:
            info = _jobs.get(job_id)
            if info is None:
                yield f"data: {json.dumps({'status':'not_found','progress':0,'step':'Unknown job'})}\n\n"
                return
            yield f"data: {json.dumps(info)}\n\n"
            if info["status"] in ("done", "error"):
                return
            await asyncio.sleep(0.6)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/download/{job_id}")
async def download_video(job_id: str):
    info = _jobs.get(job_id)
    if not info or info["status"] != "done":
        raise HTTPException(404, "Video not ready or job not found")
    output_path = info.get("output")
    if not output_path or not Path(output_path).exists():
        raise HTTPException(404, "Output file missing")
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=f"avatar_{job_id[:8]}.mp4",
    )


@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}