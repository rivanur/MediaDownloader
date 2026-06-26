
import logging
import threading
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, Session, declarative_base

import sys
# Add parent directory to path so we can import 'core'
sys.path.append(str(Path(__file__).parent.parent))

# Import original downloader logic
from core.media_downloader import MediaDownloader

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MediaDownloader")

# --- DATABASE SETUP ---
Base = declarative_base()

class DownloadTask(Base):
    __tablename__ = "download_tasks"

    id           = Column(Integer, primary_key=True)
    url          = Column(Text, nullable=False)
    title        = Column(String(500), nullable=True)
    platform     = Column(String(100), nullable=True)
    thumbnail    = Column(Text, nullable=True)
    duration     = Column(Integer, nullable=True)
    uploader     = Column(String(255), nullable=True)
    format_id    = Column(String(200), nullable=True)
    format_label = Column(String(100), nullable=True)
    output_type  = Column(String(20), default="video")
    output_ext   = Column(String(10), nullable=True)
    file_path    = Column(Text, nullable=True)
    file_size    = Column(Integer, nullable=True)
    status       = Column(String(30), default="pending")
    progress     = Column(Integer, default=0)
    speed        = Column(String(50), nullable=True)
    eta          = Column(String(20), nullable=True)
    error_msg    = Column(Text, nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

def get_db_path():
    # Render (Linux) uses /tmp for writable persistent storage
    # Locally (Windows) uses home directory
    import platform
    if platform.system() == "Windows":
        db_dir = Path.home() / ".mediadownloader"
    else:
        db_dir = Path("/tmp") / ".mediadownloader"
    db_dir.mkdir(exist_ok=True)
    return db_dir / "tasks.db"

engine = create_engine(f"sqlite:///{get_db_path()}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- APP SETUP ---
app = FastAPI(
    title="MediaDownloader Premium API",
    description="Backend API bertenaga yt-dlp untuk pengunduhan media dari 1000+ platform. Dokumentasi ini dibuat secara otomatis.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

downloader = MediaDownloader()
_sse_streams: Dict[int, List[Dict[str, Any]]] = {}
_sse_lock = threading.Lock()

# --- MODELS ---
class DownloadInfoRequest(BaseModel):
    url: str

class DownloadStartRequest(BaseModel):
    url: str
    format_id: str
    output_type: str
    output_ext: str
    title: Optional[str] = None
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    uploader: Optional[str] = None
    platform: Optional[str] = "other"
    format_label: Optional[str] = None
    output_dir: Optional[str] = None

# --- HELPERS ---
def _push_event(task_id: int, event_type: str, data: dict):
    with _sse_lock:
        if task_id not in _sse_streams:
            _sse_streams[task_id] = []
        _sse_streams[task_id].append({"type": event_type, "data": data})

def _run_download(task_id: int, url: str, format_id: str, output_type: str,
                  output_ext: str, platform: str, output_dir: Optional[str] = None):
    db = SessionLocal()
    try:
        task = db.query(DownloadTask).filter(DownloadTask.id == task_id).first()
        if not task: return

        task.status = "downloading"
        db.commit()
        _push_event(task_id, "status", {"status": "downloading", "progress": 0})

        def on_progress(percent: int, speed: str, eta: str, file_size_str: str):
            try:
                db.query(DownloadTask).filter(DownloadTask.id == task_id).update({
                    "progress": percent,
                    "speed": speed,
                    "eta": eta,
                })
                db.commit()
            except: pass
            _push_event(task_id, "progress", {
                "progress": percent,
                "speed": speed,
                "eta": eta,
                "file_size": file_size_str,
            })

        # Save to temp directory first for browser-side download
        import tempfile
        temp_dir = Path(tempfile.gettempdir()) / "MediaDownloader"
        temp_dir.mkdir(exist_ok=True)

        result = downloader.download_with_progress(
            url=url, format_id=format_id, output_type=output_type,
            output_ext=output_ext, platform=platform,
            custom_output_dir=str(temp_dir), progress_callback=on_progress
        )

        task = db.query(DownloadTask).filter(DownloadTask.id == task_id).first()
        if result["success"]:
            task.status = "completed"
            task.progress = 100
            task.file_path = result["file_path"]
            task.file_size = result.get("file_size", 0)
            task.completed_at = datetime.utcnow()
            db.commit()
            _push_event(task_id, "completed", {
                "status": "completed",
                "task_id": task_id,
                "file_name": Path(result["file_path"]).name
            })
        else:
            task.status = "failed"
            task.error_msg = result.get("error", "Download failed")
            db.commit()
            _push_event(task_id, "failed", {"status": "failed", "error": result.get("error")})
    except Exception as e:
        logger.error(f"Worker error: {e}")
    finally:
        db.close()

import re
import urllib.parse

def sanitize_filename_ascii(name: str) -> str:
    # Keep only ASCII characters and remove invalid Windows filename chars
    name_path = Path(name)
    stem = name_path.stem
    ext = name_path.suffix
    
    # Remove non-ASCII characters (like emojis)
    clean_stem = re.sub(r'[^\x00-\x7F]+', '', stem)
    # Remove characters that are illegal in Windows filenames
    clean_stem = re.sub(r'[\\/*?:"<>|]', '', clean_stem)
    clean_stem = clean_stem.strip()
    if not clean_stem:
        clean_stem = "download"
    return f"{clean_stem}{ext}"

def cleanup_file(file_path: str):
    """Hapus file setelah selesai dikirim ke user (Auto-Cleanup)"""
    import time
    try:
        # Tunggu 5 detik tambahan untuk memastikan FileResponse benar-benar selesai
        time.sleep(5)
        path = Path(file_path)
        if path.exists():
            path.unlink()
            logger.info(f"Auto-cleanup: Berhasil menghapus file dari server -> {file_path}")
    except Exception as e:
        logger.error(f"Auto-cleanup gagal untuk {file_path}: {e}")

@app.get("/api/download-file/{task_id}")
def download_file(task_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task = db.query(DownloadTask).filter(DownloadTask.id == task_id).first()
    if not task or not task.file_path or not Path(task.file_path).exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    original_name = Path(task.file_path).name
    safe_name = sanitize_filename_ascii(original_name)
    encoded_name = urllib.parse.quote(original_name)
    
    # Set headers with both safe ASCII fallback and RFC 5987 UTF-8 encoded filename
    headers = {
        "Content-Disposition": f'attachment; filename="{safe_name}"; filename*=UTF-8\'\'{encoded_name}'
    }
    
    file_path = task.file_path
    
    # Mendaftarkan task penghapusan file setelah video berhasil didownload oleh user
    background_tasks.add_task(cleanup_file, file_path)
    
    return FileResponse(
        path=file_path,
        media_type='application/octet-stream',
        headers=headers
    )

# --- ROUTES ---
@app.get("/api/ping")
def ping():
    return {"status": "ok"}

@app.post("/api/info")
def get_info(req: DownloadInfoRequest):
    result = downloader.get_info_and_formats(req.url)
    if result["success"]:
        return {"success": True, "data": result}
    return {"success": False, "error": result.get("error")}

@app.post("/api/start")
def start_download(req: DownloadStartRequest, db: Session = Depends(get_db)):
    task = DownloadTask(
        url=req.url, title=req.title, platform=req.platform,
        thumbnail=req.thumbnail, duration=req.duration, uploader=req.uploader,
        format_id=req.format_id, format_label=req.format_label,
        output_type=req.output_type, output_ext=req.output_ext, status="pending"
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    threading.Thread(
        target=_run_download,
        args=(task.id, req.url, req.format_id, req.output_type, req.output_ext, req.platform, req.output_dir),
        daemon=True
    ).start()

    return {"success": True, "task_id": task.id}

@app.get("/api/stream/{task_id}")
def stream_progress(task_id: int):
    import time
    def event_generator():
        with _sse_lock:
            if task_id not in _sse_streams: _sse_streams[task_id] = []
        sent_index = 0
        while True:
            with _sse_lock:
                events = _sse_streams.get(task_id, [])
                new_events = events[sent_index:]
            if new_events:
                for ev in new_events:
                    yield f"data: {json.dumps(ev)}\n\n"
                sent_index += len(new_events)
                if new_events[-1]["type"] in ("completed", "failed"):
                    break
            time.sleep(0.5)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/proxy-video")
def proxy_video(url: str):
    import urllib.request
    headers = {"User-Agent": "Mozilla/5.0", "Range": "bytes=0-"}
    def stream():
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            while chunk := resp.read(64*1024): yield chunk
    return StreamingResponse(stream(), media_type="video/mp4")

# Serve Frontend
frontend_path = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
else:
    @app.get("/")
    def index(): return {"message": "API is running. Frontend not built yet."}

if __name__ == "__main__":
    import uvicorn
    # Deteksi port dari environment (wajib untuk server production seperti Render/Heroku)
    port = int(os.environ.get("PORT", 8888))
    uvicorn.run(app, host="0.0.0.0", port=port)
