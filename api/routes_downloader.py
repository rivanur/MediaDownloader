"""
Media Downloader API Routes
Endpoints for downloading video/audio from 1000+ platforms via yt-dlp
"""
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.models.database import DownloadTask, get_session
from src.core.media_downloader import MediaDownloader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/downloader", tags=["downloader"])

downloader = MediaDownloader()

# SSE active streams: task_id -> list of event dicts
_sse_streams: dict = {}
_sse_lock = threading.Lock()


# ============================================================
# Pydantic Models
# ============================================================

class DownloadInfoRequest(BaseModel):
    url: str


class DownloadStartRequest(BaseModel):
    url: str
    format_id: str
    output_type: str         # "video" or "audio"
    output_ext: str          # "mp4", "mp3", "m4a"
    title: Optional[str] = None
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    uploader: Optional[str] = None
    platform: Optional[str] = "other"
    format_label: Optional[str] = None
    output_dir: Optional[str] = None  # User-chosen folder path (None = use default)
    project_id: Optional[int] = None  # Add project context


class SendToProjectRequest(BaseModel):
    project_id: int


# ============================================================
# Helper: push SSE event
# ============================================================

def _push_event(task_id: int, event_type: str, data: dict):
    """Push a server-sent event to all listeners of a task"""
    with _sse_lock:
        if task_id not in _sse_streams:
            _sse_streams[task_id] = []
        _sse_streams[task_id].append({"type": event_type, "data": data})


def _format_task(task: DownloadTask) -> dict:
    return {
        "id": task.id,
        "url": task.url,
        "title": task.title,
        "platform": task.platform,
        "thumbnail": task.thumbnail,
        "duration": task.duration,
        "uploader": task.uploader,
        "format_label": task.format_label,
        "output_type": task.output_type,
        "output_ext": task.output_ext,
        "file_path": task.file_path,
        "file_size": task.file_size,
        "status": task.status,
        "progress": task.progress,
        "speed": task.speed,
        "eta": task.eta,
        "error_msg": task.error_msg,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }


# ============================================================
# Background download worker
# ============================================================

def _run_download(task_id: int, url: str, format_id: str, output_type: str,
                  output_ext: str, platform: str, output_dir: Optional[str] = None):
    """Background worker that runs the actual download and reports progress via SSE"""
    from sqlalchemy.orm import sessionmaker
    from src.models.database import init_db
    
    engine = init_db()
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        task = db.query(DownloadTask).filter(DownloadTask.id == task_id).first()
        if not task:
            logger.error(f"DownloadTask {task_id} not found")
            return

        task.status = "downloading"
        task.progress = 0
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
            except Exception:
                pass
            _push_event(task_id, "progress", {
                "progress": percent,
                "speed": speed,
                "eta": eta,
                "file_size": file_size_str,
            })

        result = downloader.download_with_progress(
            url=url,
            format_id=format_id,
            output_type=output_type,
            output_ext=output_ext,
            platform=platform,
            custom_output_dir=output_dir,
            progress_callback=on_progress,
        )

        # Re-fetch task (session may have staled)
        task = db.query(DownloadTask).filter(DownloadTask.id == task_id).first()

        if result["success"]:
            task.status = "completed"
            task.progress = 100
            task.file_path = result["file_path"]
            task.file_size = result.get("file_size", 0)
            task.completed_at = datetime.utcnow()
            task.speed = None
            task.eta = None
            db.commit()

            _push_event(task_id, "completed", {
                "status": "completed",
                "progress": 100,
                "file_path": result["file_path"],
                "file_size": result.get("file_size_str", ""),
            })
            logger.info(f"Task {task_id} completed: {result['file_path']}")
        else:
            task.status = "failed"
            task.error_msg = result.get("error", "Download gagal")
            task.completed_at = datetime.utcnow()
            db.commit()

            _push_event(task_id, "failed", {
                "status": "failed",
                "error": result.get("error"),
            })
            logger.error(f"Task {task_id} failed: {result.get('error')}")

    except Exception as e:
        logger.error(f"Unexpected error in download worker for task {task_id}: {e}")
        try:
            task = db.query(DownloadTask).filter(DownloadTask.id == task_id).first()
            if task:
                task.status = "failed"
                task.error_msg = str(e)[:300]
                task.completed_at = datetime.utcnow()
                db.commit()
            _push_event(task_id, "failed", {"status": "failed", "error": str(e)[:300]})
        except Exception:
            pass
    finally:
        db.close()


# ============================================================
# Endpoints
# ============================================================

@router.get("/pick-folder", response_model=dict)
def pick_folder(project_id: Optional[int] = None, db: Session = Depends(get_session)):
    """
    Open a native folder picker dialog and return the chosen path.
    Uses tkinter which works on Windows/macOS/Linux for local desktop apps.
    This is safe because the FastAPI server runs on the same machine as the user.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
        import os

        # Create a hidden root window (required by tkinter)
        root = tk.Tk()
        root.withdraw()          # Hide the main window
        root.wm_attributes("-topmost", True)  # Dialog appears on top

        # Default starting folder
        default_dir = str(Path.home() / "StudioFlow Output" / "Downloads")
        
        if project_id:
            from src.models.database import Project
            project = db.query(Project).filter(Project.id == project_id).first()
            if project and project.project_path:
                default_dir = os.path.join(project.project_path, "Media Downloader")

        Path(default_dir).mkdir(parents=True, exist_ok=True)

        folder = filedialog.askdirectory(
            title="Pilih Folder Tujuan Download",
            initialdir=default_dir,
            mustexist=False,
        )
        root.destroy()

        if folder:
            # Ensure folder exists
            Path(folder).mkdir(parents=True, exist_ok=True)
            return {
                "success": True,
                "data": {"folder": folder, "display": folder},
                "error": None,
            }
        else:
            # User cancelled the dialog
            return {"success": False, "data": None, "error": "cancelled"}

    except ImportError:
        # tkinter not available — return default path as fallback
        default_dir = str(Path.home() / "StudioFlow Output" / "Downloads")
        Path(default_dir).mkdir(parents=True, exist_ok=True)
        return {
            "success": True,
            "data": {
                "folder": default_dir,
                "display": default_dir,
                "note": "tkinter tidak tersedia, menggunakan folder default",
            },
            "error": None,
        }
    except Exception as e:
        logger.error(f"pick_folder error: {e}")
        return {"success": False, "data": None, "error": str(e)}


@router.get("/default-folder", response_model=dict)
def get_default_folder(project_id: Optional[int] = None, db: Session = Depends(get_session)):
    """Return the default download folder path"""
    import os
    if project_id:
        from src.models.database import Project
        project = db.query(Project).filter(Project.id == project_id).first()
        if project and project.project_path:
            default_dir = os.path.join(project.project_path, "Media Downloader")
            os.makedirs(default_dir, exist_ok=True)
            return {
                "success": True,
                "data": {"folder": default_dir, "display": default_dir},
                "error": None,
            }

    default_dir = str(Path.home() / "StudioFlow Output" / "Downloads")
    Path(default_dir).mkdir(parents=True, exist_ok=True)
    return {
        "success": True,
        "data": {"folder": default_dir, "display": default_dir},
        "error": None,
    }


@router.get("/proxy-video")
def proxy_video(url: str):
    """
    Proxy a video stream through the local FastAPI server to bypass CORS.
    
    Many CDNs (TikTok, Instagram, etc.) block direct browser requests via CORS.
    This endpoint fetches the video server-side and streams it to the browser,
    since browser <-> localhost has no CORS issues.
    """
    import urllib.request
    import urllib.parse

    if not url:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": "URL required"}, status_code=400)

    # Detect platform from URL for proper Referer header
    platform_referers = {
        "tiktok.com":    "https://www.tiktok.com/",
        "instagram.com": "https://www.instagram.com/",
        "facebook.com":  "https://www.facebook.com/",
        "youtube.com":   "https://www.youtube.com/",
        "youtu.be":      "https://www.youtube.com/",
        "twitter.com":   "https://twitter.com/",
        "x.com":         "https://x.com/",
    }
    referer = "https://www.google.com/"
    for domain, ref in platform_referers.items():
        if domain in url:
            referer = ref
            break

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Referer": referer,
        "Accept": "video/webm,video/mp4,video/*;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Range": "bytes=0-",
    }

    def stream_video():
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                while True:
                    chunk = resp.read(64 * 1024)  # 64 KB chunks
                    if not chunk:
                        break
                    yield chunk
        except Exception as e:
            logger.error(f"proxy_video error: {e}")

    return StreamingResponse(
        stream_video(),
        media_type="video/mp4",
        headers={
            "Cache-Control": "no-cache",
            "Accept-Ranges": "bytes",
        },
    )


@router.post("/info", response_model=dict)
def get_video_info(req: DownloadInfoRequest):
    """Fetch video info and available formats from a URL"""
    if not req.url.strip():
        return {"success": False, "data": None, "error": "URL tidak boleh kosong"}

    # Quick check: yt-dlp available?
    if not downloader.verify_ytdlp():
        return {
            "success": False, "data": None,
            "error": "yt-dlp tidak terinstall. Jalankan: pip install yt-dlp"
        }

    result = downloader.get_info_and_formats(req.url.strip())
    if result["success"]:
        return {"success": True, "data": result, "error": None}
    return {"success": False, "data": None, "error": result.get("error")}


@router.post("/start", response_model=dict)
def start_download(req: DownloadStartRequest, db: Session = Depends(get_session)):
    """Create a download task and start it in the background"""
    if not req.url.strip():
        return {"success": False, "data": None, "error": "URL tidak boleh kosong"}

    # Create DB task
    task = DownloadTask(
        url=req.url.strip(),
        title=req.title or "Untitled",
        platform=req.platform or "other",
        thumbnail=req.thumbnail,
        duration=req.duration,
        uploader=req.uploader,
        format_id=req.format_id,
        format_label=req.format_label or req.output_ext.upper(),
        output_type=req.output_type,
        output_ext=req.output_ext,
        status="pending",
        progress=0,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    output_dir = req.output_dir

    if not output_dir and req.project_id:
        from src.models.database import Project
        import os
        project = db.query(Project).filter(Project.id == req.project_id).first()
        if project and project.project_path:
            output_dir = os.path.join(project.project_path, "Media Downloader")
            os.makedirs(output_dir, exist_ok=True)

    # Launch background thread
    thread = threading.Thread(
        target=_run_download,
        args=(task_id, req.url.strip(), req.format_id,
              req.output_type, req.output_ext, req.platform or "other",
              output_dir),
        daemon=True,
    )
    thread.start()

    return {"success": True, "data": {"task_id": task_id, "status": "pending"}, "error": None}


@router.get("/stream/{task_id}")
def stream_progress(task_id: int):
    """SSE endpoint — streams real-time download progress for a task"""
    import time
    import json as json_lib

    def event_generator():
        # Initialize the stream list for this task
        with _sse_lock:
            if task_id not in _sse_streams:
                _sse_streams[task_id] = []
        
        sent_index = 0
        max_idle_seconds = 600  # 10 minutes timeout
        idle_count = 0

        while idle_count < max_idle_seconds * 5:  # poll every 200ms
            with _sse_lock:
                events = _sse_streams.get(task_id, [])
                new_events = events[sent_index:]

            if new_events:
                idle_count = 0
                for ev in new_events:
                    data_str = json_lib.dumps(ev)
                    yield f"data: {data_str}\n\n"
                sent_index += len(new_events)

                # Stop streaming when terminal state reached
                last_type = new_events[-1].get("type")
                if last_type in ("completed", "failed", "cancelled"):
                    # Cleanup
                    with _sse_lock:
                        _sse_streams.pop(task_id, None)
                    break
            else:
                idle_count += 1

            time.sleep(0.2)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/tasks", response_model=dict)
def get_download_history(db: Session = Depends(get_session)):
    """Get all download tasks (history), newest first"""
    try:
        tasks = db.query(DownloadTask).order_by(DownloadTask.created_at.desc()).limit(100).all()
        return {
            "success": True,
            "data": [_format_task(t) for t in tasks],
            "error": None,
        }
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


@router.get("/tasks/{task_id}", response_model=dict)
def get_task_status(task_id: int, db: Session = Depends(get_session)):
    """Get status of a specific download task"""
    try:
        task = db.query(DownloadTask).filter(DownloadTask.id == task_id).first()
        if not task:
            return {"success": False, "data": None, "error": "Task tidak ditemukan"}
        return {"success": True, "data": _format_task(task), "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


@router.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id: int, db: Session = Depends(get_session)):
    """Delete a download task from history"""
    try:
        task = db.query(DownloadTask).filter(DownloadTask.id == task_id).first()
        if not task:
            return {"success": False, "data": None, "error": "Task tidak ditemukan"}
        db.delete(task)
        db.commit()
        return {"success": True, "data": {"id": task_id, "message": "Task dihapus"}, "error": None}
    except Exception as e:
        db.rollback()
        return {"success": False, "data": None, "error": str(e)}


@router.post("/tasks/{task_id}/open", response_model=dict)
def open_file(task_id: int, db: Session = Depends(get_session)):
    """Open the downloaded file in file explorer"""
    try:
        task = db.query(DownloadTask).filter(DownloadTask.id == task_id).first()
        if not task:
            return {"success": False, "data": None, "error": "Task tidak ditemukan"}
        if not task.file_path or not Path(task.file_path).exists():
            return {"success": False, "data": None, "error": "File tidak ditemukan di disk"}

        success = downloader.open_file_in_explorer(task.file_path)
        if success:
            return {"success": True, "data": {"message": "File Explorer dibuka"}, "error": None}
        return {"success": False, "data": None, "error": "Gagal membuka File Explorer"}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


@router.post("/tasks/{task_id}/send-to-project", response_model=dict)
def send_to_project(task_id: int, req: SendToProjectRequest, db: Session = Depends(get_session)):
    """Send a downloaded file to a StudioFlow project as a ready clip"""
    try:
        from src.models.database import Job, Project, Clip

        task = db.query(DownloadTask).filter(DownloadTask.id == task_id).first()
        if not task:
            return {"success": False, "data": None, "error": "Task tidak ditemukan"}
        if not task.file_path or not Path(task.file_path).exists():
            return {"success": False, "data": None, "error": "File tidak ditemukan di disk"}

        project = db.query(Project).filter(Project.id == req.project_id).first()
        if not project:
            return {"success": False, "data": None, "error": "Project tidak ditemukan"}

        # 1. Buat Job dengan status completed (karena file sudah jadi)
        job = Job(
            project_id=req.project_id,
            title=f"Import: {task.title or 'Media Downloader'}",
            input_source="local",
            input_path=task.file_path,
            mode="IMPORT",
            status="completed",
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        # 2. Buat Clip agar langsung muncul di halaman detail project
        clip = Clip(
            project_id=req.project_id,
            job_id=job.id,
            title=task.title or "Imported Video",
            file_path=task.file_path,
            thumbnail_path=task.thumbnail,
            duration=task.duration or 0,
            status="ready"
        )
        db.add(clip)
        db.commit()

        return {
            "success": True,
            "data": {
                "job_id": job.id,
                "project_id": req.project_id,
                "message": f"File berhasil dikirim ke project '{project.name}' sebagai Clip",
            },
            "error": None,
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "data": None, "error": str(e)}


@router.delete("/tasks", response_model=dict)
def clear_history(db: Session = Depends(get_session)):
    """Clear all completed/failed download tasks from history"""
    try:
        deleted = db.query(DownloadTask).filter(
            DownloadTask.status.in_(["completed", "failed", "cancelled"])
        ).delete(synchronize_session=False)
        db.commit()
        return {
            "success": True,
            "data": {"deleted_count": deleted, "message": f"{deleted} task dihapus dari riwayat"},
            "error": None,
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "data": None, "error": str(e)}
