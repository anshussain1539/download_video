import os
import re
import tempfile
import uuid
from pathlib import Path

import yt_dlp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask

app = FastAPI(title="Video Downloader")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_DIR = Path(tempfile.gettempdir()) / "video_downloader"
DOWNLOAD_DIR.mkdir(exist_ok=True)

# If a cookies.txt is sitting next to main.py, hand it to yt-dlp.
# Used to bypass YouTube/FB cloud-IP bot checks during deploy testing.
# DO NOT commit real account cookies to a public repo.
_cookies_path = Path(__file__).parent / "cookies.txt"
COOKIES_FILE = str(_cookies_path) if _cookies_path.exists() else None


class DownloadRequest(BaseModel):
    url: str


def _safe_filename(name: str) -> str:
    name = re.sub(r"[^\w\-. ]", "_", name).strip()
    return name or "video.mp4"


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/download")
def download(req: DownloadRequest):
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    job_id = uuid.uuid4().hex
    out_template = str(DOWNLOAD_DIR / f"{job_id}.%(ext)s")

    ydl_opts = {
        "outtmpl": out_template,
        "format": "best[ext=mp4]/best",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "restrictfilenames": True,
    }

    if COOKIES_FILE:
        ydl_opts["cookiefile"] = COOKIES_FILE

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            title = info.get("title") or "video"
            ext = info.get("ext") or "mp4"
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=400, detail=f"Could not download: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="File not produced")

    pretty_name = _safe_filename(f"{title}.{ext}")

    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=pretty_name,
        background=BackgroundTask(lambda p=file_path: os.path.exists(p) and os.remove(p)),
    )
