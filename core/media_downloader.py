"""
Media Downloader - Enhanced Downloader using yt-dlp
Supports 1000+ platforms: YouTube, Instagram, Facebook, TikTok, Twitter/X, Vimeo, etc.
"""
import logging
import re
import subprocess
import json
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

# Regex to parse yt-dlp progress output
# e.g. "[download]  45.2% of  50.00MiB at  2.34MiB/s ETA 00:22"
PROGRESS_REGEX = re.compile(
    r"\[download\]\s+([\d.]+)%\s+of\s+~?\s*([\d.]+\w+)\s+at\s+([\d.]+\w+/s)\s+ETA\s+([\d:]+)"
)

# Platform detection map
PLATFORM_MAP = {
    # Google / YouTube
    "youtube.com": "youtube",
    "youtu.be": "youtube",
    # Meta
    "instagram.com": "instagram",
    "facebook.com": "facebook",
    "fb.watch": "facebook",
    "threads.com": "threads",
    "threads.net": "threads",
    # TikTok
    "tiktok.com": "tiktok",
    "vm.tiktok.com": "tiktok",
    # Twitter / X
    "twitter.com": "twitter",
    "x.com": "twitter",
    # Video platforms
    "vimeo.com": "vimeo",
    "dailymotion.com": "dailymotion",
    "twitch.tv": "twitch",
    "kick.com": "kick",
    "rumble.com": "rumble",
    "odysee.com": "odysee",
    # Social
    "reddit.com": "reddit",
    "pinterest.com": "pinterest",
    "pin.it": "pinterest",
    "linkedin.com": "linkedin",
    "snapchat.com": "snapchat",
    "tumblr.com": "tumblr",
    # Audio
    "soundcloud.com": "soundcloud",
    "mixcloud.com": "mixcloud",
    "spotify.com": "spotify",
    # Asian platforms
    "bilibili.com": "bilibili",
    "nicovideo.jp": "nicovideo",
    "weibo.com": "weibo",
}


class MediaDownloader:
    """Download videos/audio from 1000+ platforms using yt-dlp"""

    def __init__(self, ytdlp_path: str = "yt-dlp"):
        self.ytdlp_path = ytdlp_path
        logger.info("MediaDownloader initialized (Anonymous Mode - No cookies)")

    def detect_platform(self, url: str) -> str:
        """Detect platform from URL"""
        url_lower = url.lower()
        for domain, platform in PLATFORM_MAP.items():
            if domain in url_lower:
                return platform
        return "other"

    def verify_ytdlp(self) -> bool:
        """Verify yt-dlp is installed"""
        try:
            result = subprocess.run(
                [self.ytdlp_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                logger.info(f"yt-dlp verified: {result.stdout.strip()}")
                return True
            return False
        except Exception as e:
            logger.error(f"yt-dlp not found: {e}")
            return False

    def _run_apify_actor(self, actor_id: str, input_data: dict) -> Optional[list]:
        """Run an Apify actor synchronously and return the dataset items"""
        import os
        api_token = os.environ.get("APIFY_API_TOKEN")
        if not api_token:
            token_path = Path(__file__).parent.parent / "apify_token.txt"
            if token_path.exists():
                try:
                    api_token = token_path.read_text().strip()
                except Exception as e:
                    logger.error(f"Failed to read apify_token.txt: {e}")
        
        if not api_token:
            logger.error("Apify API Token not found! Please set APIFY_API_TOKEN environment variable or create apify_token.txt.")
            return None
        actor_id_clean = actor_id.replace("/", "~")
        url = f"https://api.apify.com/v2/acts/{actor_id_clean}/run-sync-get-dataset-items?token={api_token}"
        
        req = urllib.request.Request(
            url,
            data=json.dumps(input_data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            logger.info(f"Triggering Apify actor {actor_id}...")
            with urllib.request.urlopen(req, timeout=90) as response:
                items = json.loads(response.read().decode("utf-8"))
                logger.info(f"Apify actor {actor_id} run completed. Got {len(items)} items.")
                return items
        except Exception as e:
            logger.error(f"Apify actor {actor_id} failed: {e}")
            return None

    def get_info_and_formats(self, url: str) -> Dict[str, Any]:
        """
        Fetch video info + all available formats from URL.

        Returns:
            Dict with title, thumbnail, duration, uploader, platform,
            video_formats list, audio_formats list
        """
        platform = self.detect_platform(url)

        # YouTube intercept using 3-layer fallback
        if platform == "youtube":
            title = None
            uploader = None
            thumbnail = None

            # Layer 1: YouTube native oEmbed
            try:
                oembed_url = f"https://www.youtube.com/oembed?url={urllib.parse.quote(url)}&format=json"
                req = urllib.request.Request(oembed_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    title = data.get("title")
                    uploader = data.get("author_name")
                    thumbnail = data.get("thumbnail_url")
                    logger.info("YouTube metadata: native oEmbed succeeded")
            except Exception as e:
                logger.warning(f"YouTube native oEmbed failed: {e}")

            # Layer 2: noembed.com (third-party proxy)
            if not title:
                try:
                    noembed_url = f"https://noembed.com/embed?url={urllib.parse.quote(url)}"
                    req = urllib.request.Request(noembed_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=10) as response:
                        data = json.loads(response.read().decode("utf-8"))
                        title = data.get("title")
                        uploader = data.get("author_name")
                        thumbnail = data.get("thumbnail_url")
                        logger.info("YouTube metadata: noembed.com succeeded")
                except Exception as e:
                    logger.warning(f"YouTube noembed.com failed: {e}")

            # Layer 3: Manual extraction from video ID
            if not title:
                try:
                    video_id_match = re.search(r"(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})", url)
                    if video_id_match:
                        video_id = video_id_match.group(1)
                        title = "YouTube Video"
                        uploader = "YouTube Creator"
                        thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                        logger.info(f"YouTube metadata: manual extraction for video ID {video_id}")
                except Exception as e:
                    logger.warning(f"YouTube manual extraction failed: {e}")

            if title:
                return {
                    "success": True,
                    "title": title,
                    "thumbnail": thumbnail or "",
                    "duration": 0,
                    "uploader": uploader or "YouTube Creator",
                    "platform": "youtube",
                    "video_formats": [
                        {"format_id": "apify-youtube-1080", "label": "1080p MP4 (Apify)", "ext": "mp4", "resolution": "1920x1080", "height": 1080, "filesize": 0, "filesize_approx": "Ukuran tidak diketahui"},
                        {"format_id": "apify-youtube-720", "label": "720p MP4 (Apify)", "ext": "mp4", "resolution": "1280x720", "height": 720, "filesize": 0, "filesize_approx": "Ukuran tidak diketahui"},
                        {"format_id": "apify-youtube-480", "label": "480p MP4 (Apify)", "ext": "mp4", "resolution": "854x480", "height": 480, "filesize": 0, "filesize_approx": "Ukuran tidak diketahui"},
                        {"format_id": "apify-youtube-360", "label": "360p MP4 (Apify)", "ext": "mp4", "resolution": "640x360", "height": 360, "filesize": 0, "filesize_approx": "Ukuran tidak diketahui"},
                    ],
                    "audio_formats": [
                        {"format_id": "apify-youtube-audio", "label": "MP3 Audio (Apify)", "ext": "mp3", "filesize": 0, "filesize_approx": "Ukuran tidak diketahui"}
                    ]
                }
            else:
                return {"success": False, "error": "URL YouTube tidak valid atau video tidak ditemukan."}

        try:
            cmd = [
                self.ytdlp_path,
                "--no-warnings",
                "--dump-json",
                "--no-playlist",
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "--add-header", "Sec-Ch-Ua:\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
                "--add-header", "Sec-Ch-Ua-Mobile:?0",
                "--add-header", "Sec-Ch-Ua-Platform:\"Windows\"",
                "--add-header", "Sec-Fetch-Dest:empty",
                "--add-header", "Sec-Fetch-Mode:cors",
                "--add-header", "Sec-Fetch-Site:same-origin",
                "--no-check-certificate",
                "--geo-bypass",
                "--extractor-args", "youtube:player_client=android",
                url,
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding="utf-8",
                errors="replace",
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                # Map yt-dlp errors to user-friendly messages
                err_lower = error_msg.lower()

                # Check if it is Instagram. If so, fall back to Apify scraper!
                if platform == "instagram":
                    logger.info("Instagram yt-dlp failed, falling back to Apify...")
                    apify_res = self._run_apify_actor(
                        "apify/instagram-scraper",
                        {
                            "directUrls": [url],
                            "resultsType": "details"
                        }
                    )
                    if apify_res and len(apify_res) > 0:
                        item = apify_res[0]
                        title = item.get("caption") or "Instagram Post"
                        if len(title) > 60:
                            title = title[:60] + "..."
                        thumbnail = item.get("displayUrl") or ""
                        uploader = item.get("ownerUsername") or "Instagram User"
                        video_url = item.get("videoUrl")
                        
                        if video_url:
                            return {
                                "success": True,
                                "title": title,
                                "thumbnail": thumbnail,
                                "duration": 0,
                                "uploader": uploader,
                                "platform": "instagram",
                                "video_formats": [
                                    {
                                        "format_id": f"apify-direct-{video_url}",
                                        "label": "Kualitas Terbaik (Apify)",
                                        "ext": "mp4",
                                        "resolution": "Auto",
                                        "height": 720,
                                        "filesize": 0,
                                        "filesize_approx": "Ukuran tidak diketahui"
                                    }
                                ],
                                "audio_formats": []
                            }

                if "unsupported url" in err_lower or "not supported" in err_lower:
                    platform_guess = self.detect_platform(url)
                    if platform_guess == "threads":
                        error_msg = (
                            "Maaf, video dari Threads belum bisa didownload untuk saat ini "
                            "karena pembatasan dari pihak platform tersebut."
                        )
                    elif platform_guess == "spotify":
                        error_msg = "Maaf, lagu dari Spotify tidak bisa didownload langsung. Silakan gunakan platform video/audio lainnya."
                    else:
                        error_msg = (
                            "Maaf, platform ini belum didukung atau link yang kamu masukkan salah. "
                            "Pastikan link video bersifat publik."
                        )
                elif "private" in err_lower:
                    error_msg = "Video ini bersifat privat (hanya bisa dilihat pemiliknya). Pastikan video diset ke 'Publik'."
                elif "removed" in err_lower or "unavailable" in err_lower:
                    error_msg = "Yah, videonya sudah dihapus atau sudah tidak tersedia lagi."
                elif "attempting impersonation" in err_lower:
                    error_msg = "Maaf, platform ini memiliki proteksi tinggi (Cloudflare) yang belum bisa ditembus oleh sistem."
                elif "facebook" in err_lower and "403" in error_msg:
                    error_msg = "Facebook memblokir akses otomatis ke video ini. Coba pastikan video ini bisa dibuka tanpa login."
                elif "403" in error_msg and "kick" in url.lower():
                    error_msg = "Kick memblokir akses pengunduh otomatis. Silakan coba video dari platform lain."
                if "403" in error_msg or "login" in err_lower or "privat" in error_msg.lower():
                    error_msg += " (Website ini mungkin memblokir akses anonim atau video bersifat privat)."
                    
                return {"success": False, "error": error_msg}

            info = json.loads(result.stdout)
            platform = self.detect_platform(url)

            # Build video formats list (deduplicated by resolution)
            video_formats = []
            seen_resolutions = set()
            raw_formats = info.get("formats", [])

            # Sort by quality (highest first)
            quality_formats = [
                f for f in raw_formats
                if f.get("vcodec") not in (None, "none")
                and f.get("ext") in ("mp4", "webm", "mkv")
            ]
            quality_formats.sort(key=lambda f: f.get("height", 0), reverse=True)

            for fmt in quality_formats:
                height = fmt.get("height")
                if not height or height in seen_resolutions:
                    continue
                seen_resolutions.add(height)

                filesize = fmt.get("filesize") or fmt.get("filesize_approx", 0)
                filesize_str = self._format_bytes(filesize) if filesize else "Ukuran tidak diketahui"

                # Build best combined format (video+audio)
                fmt_id = fmt.get("format_id", "best")
                # Try to merge with best audio
                if fmt.get("acodec") in (None, "none"):
                    fmt_id = f"{fmt_id}+bestaudio[ext=m4a]/bestvideo[height<={height}]+bestaudio/best[height<={height}]"

                video_formats.append({
                    "format_id": fmt_id,
                    "label": f"{height}p {fmt.get('ext', 'mp4').upper()}",
                    "ext": fmt.get("ext", "mp4"),
                    "resolution": f"{fmt.get('width', '?')}x{height}",
                    "height": height,
                    "filesize": filesize,
                    "filesize_approx": filesize_str,
                    "vcodec": fmt.get("vcodec", ""),
                })

            # Fallback if no specific formats found
            if not video_formats:
                video_formats = [
                    {"format_id": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "label": "Kualitas Terbaik (Auto)", "ext": "mp4", "resolution": "Auto", "height": 9999, "filesize": 0, "filesize_approx": "Ukuran tidak diketahui"},
                    {"format_id": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]", "label": "720p MP4", "ext": "mp4", "resolution": "Auto 720p", "height": 720, "filesize": 0, "filesize_approx": "Ukuran tidak diketahui"},
                    {"format_id": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]", "label": "480p MP4", "ext": "mp4", "resolution": "Auto 480p", "height": 480, "filesize": 0, "filesize_approx": "Ukuran tidak diketahui"},
                ]

            # Audio formats
            audio_formats = [
                {"format_id": "bestaudio/best", "label": "MP3 (Kualitas Terbaik)", "ext": "mp3", "abr": 192, "filesize_approx": "Estimasi ~5-15 MB"},
                {"format_id": "bestaudio[abr<=128]/bestaudio", "label": "MP3 (Standar 128kbps)", "ext": "mp3", "abr": 128, "filesize_approx": "Estimasi ~3-10 MB"},
                {"format_id": "bestaudio/best", "label": "M4A (Kualitas Terbaik)", "ext": "m4a", "abr": 192, "filesize_approx": "Estimasi ~5-15 MB"},
            ]

            # Platforms where CDN video URLs are session/cookie-locked — proxy returns 403
            PREVIEW_UNSUPPORTED = {"tiktok", "instagram", "facebook", "twitter", "x"}

            preview_url = None
            preview_note = None

            if platform in PREVIEW_UNSUPPORTED:
                preview_note = f"Preview tidak tersedia untuk {platform.capitalize()} (URL CDN terlindungi)"
            else:
                # Look for combined (video+audio) mp4 formats — closest to 480p for efficiency
                combined_mp4s = [
                    f for f in raw_formats
                    if f.get("vcodec") not in (None, "none")
                    and f.get("acodec") not in (None, "none")
                    and f.get("ext") == "mp4"
                    and f.get("url")
                ]
                if combined_mp4s:
                    combined_mp4s.sort(key=lambda f: abs(f.get("height", 0) - 480))
                    raw_preview = combined_mp4s[0].get("url")
                else:
                    raw_preview = info.get("url")

                if raw_preview:
                    import urllib.parse
                    preview_url = f"/proxy-video?url={urllib.parse.quote(raw_preview, safe='')}"


            duration = info.get("duration", 0)

            return {
                "success": True,
                "title": info.get("title", "Untitled"),
                "thumbnail": info.get("thumbnail", ""),
                "duration": int(duration) if duration else 0,
                "uploader": info.get("uploader") or info.get("channel", "Unknown"),
                "view_count": info.get("view_count"),
                "platform": platform,
                "webpage_url": info.get("webpage_url", url),
                "preview_url": preview_url,
                "preview_note": preview_note,
                "video_formats": video_formats,
                "audio_formats": audio_formats,
            }

        except json.JSONDecodeError:
            return {"success": False, "error": "Gagal membaca data video dari yt-dlp."}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout: Koneksi ke platform terlalu lama."}
        except Exception as e:
            logger.error(f"Error getting info for {url}: {e}")
            return {"success": False, "error": str(e)[:200]}

    def get_output_dir(self, platform: str) -> Path:
        """Get the temporary output directory for server-side downloads"""
        import tempfile
        # Create a temp directory for downloads that will be cleaned up later
        base_tmp = Path(tempfile.gettempdir()) / "MediaDownloader"
        output_dir = base_tmp / platform.capitalize()
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def download_with_progress(
        self,
        url: str,
        format_id: str,
        output_type: str,  # "video" or "audio"
        output_ext: str,
        platform: str = "other",
        custom_output_dir: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
        use_cookies: bool = False,
    ) -> Dict[str, Any]:
        """
        Download video/audio with real-time progress reporting.

        Args:
            url: Media URL
            format_id: yt-dlp format string
            output_type: "video" or "audio"
            output_ext: Output file extension (mp4, mp3, m4a)
            platform: Detected platform name
            custom_output_dir: User-chosen folder path (overrides default)
            progress_callback: Called with (percent, speed, eta, file_size) during download

        Returns:
            Dict with success, file_path, file_size, error
        """
        try:
            # Apify format overrides
            if format_id.startswith("apify-youtube-"):
                logger.info("Downloading YouTube video via Apify actor...")
                if progress_callback:
                    progress_callback(10, "0 B/s", "00:15", "Menghubungkan ke Apify (membutuhkan waktu 30-40 detik)...")

                apify_res = self._run_apify_actor(
                    "streamers/youtube-video-downloader",
                    {"videos": [{"url": url}]}
                )

                if not apify_res or len(apify_res) == 0:
                    return {"success": False, "error": "Gagal mendapatkan link download dari Apify."}

                item = apify_res[0]
                direct_url = item.get("audioOnlyUrl") if output_type == "audio" else item.get("downloadedFileUrl")
                if not direct_url:
                    direct_url = item.get("downloadedFileUrl") or item.get("videoOnlyUrl") or item.get("audioOnlyUrl")

                if not direct_url:
                    return {"success": False, "error": "Link video/audio tidak ditemukan dalam response Apify."}

                logger.info(f"Apify returned direct URL: {direct_url[:100]}...")
                if progress_callback:
                    progress_callback(30, "0 B/s", "00:05", "Mengunduh file dari CDN...")

                url = direct_url
                format_id = "best"

            elif format_id.startswith("apify-direct-"):
                direct_url = format_id.replace("apify-direct-", "")
                logger.info(f"Downloading direct URL: {direct_url[:100]}...")
                url = direct_url
                format_id = "best"

            # Use custom dir if provided, else use default structured dir
            if custom_output_dir:
                output_dir = Path(custom_output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
            else:
                output_dir = self.get_output_dir(platform)
            # Use resolution/quality in filename to avoid overwriting when downloading
            # same video at different quality (e.g. 1080p vs 720p)
            if output_type == "audio":
                output_template = str(output_dir / "%(title).60B_%(abr)skbps.%(ext)s")
            else:
                output_template = str(output_dir / "%(title).60B_%(height)sp.%(ext)s")

            cmd = [
                self.ytdlp_path,
                "--no-warnings",
                "--newline",
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "--add-header", f"Referer:{url}",
                "--add-header", "Sec-Ch-Ua:\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
                "--add-header", "Sec-Ch-Ua-Mobile:?0",
                "--add-header", "Sec-Ch-Ua-Platform:\"Windows\"",
                "--no-check-certificate",
                "--restrict-filenames",   # ← Sanitize karakter invalid (emoji, spesial) di nama file
                "--trim-filenames", "150", # ← Potong nama file maks 150 char (Windows limit 260)
                "--extractor-args", "youtube:player_client=android",
                "-f", format_id,
                "-o", output_template,
                "--no-playlist",
            ]
            if output_type == "audio":
                cmd.extend([
                    "-x",
                    "--audio-format", output_ext,
                    "--audio-quality", "0",
                ])
            else:
                # Merge video+audio into mp4
                cmd.extend([
                    "--merge-output-format", "mp4",
                ])

            cmd.append(url)

            logger.info(f"Starting download: {url} (format: {format_id})")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )

            stderr_lines = []

            def track_stderr():
                for line in process.stderr:
                    if line.strip():
                        stderr_lines.append(line.strip())
                        logger.error(f"yt-dlp stderr: {line.strip()}")

            import threading
            threading.Thread(target=track_stderr, daemon=True).start()

            downloaded_file = None
            last_percent = 0

            for line in process.stdout:
                line = line.strip()
                if not line:
                    continue

                logger.debug(f"yt-dlp: {line}")

                # Parse progress
                match = PROGRESS_REGEX.search(line)
                if match and progress_callback:
                    percent = float(match.group(1))
                    file_size_str = match.group(2)
                    speed = match.group(3)
                    eta = match.group(4)
                    if percent > last_percent:
                        last_percent = percent
                        progress_callback(int(percent), speed, eta, file_size_str)

                # Track final file destination
                if line.startswith("[download] Destination:"):
                    downloaded_file = line.replace("[download] Destination:", "").strip()
                elif "[Merger]" in line and "Merging formats into" in line:
                    # After merging, the file path changes
                    merged = re.search(r'"(.+?)"', line)
                    if merged:
                        downloaded_file = merged.group(1)

            process.wait(timeout=3600)

            if process.returncode != 0:
                err_msg = " ".join(stderr_lines[-2:]) if stderr_lines else "Unknown error"
                logger.error(f"Download failed with code {process.returncode}: {err_msg}")
                


                # FB/IG Fallback: retry with 'best' using correct param order
                if ("facebook" in url or "instagram" in url) and format_id != "best":
                    logger.info("Retrying with fallback 'best' format...")
                    return self.download_with_progress(
                        url, "best", output_type, output_ext, platform, str(output_dir), progress_callback
                    )
                
                err_friendly = (
                    "Nama file terlalu panjang atau mengandung karakter tidak valid."
                    if "Errno 22" in err_msg
                    else f"yt-dlp error (code {process.returncode}): {err_msg[:200]}"
                )
                return {"success": False, "error": err_friendly}

            if process.returncode == 0:
                # Find the most recently modified file in output dir
                if not downloaded_file or not Path(downloaded_file).exists():
                    files = sorted(output_dir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
                    if files:
                        downloaded_file = str(files[0])

                if downloaded_file and Path(downloaded_file).exists():
                    file_size = Path(downloaded_file).stat().st_size
                    logger.info(f"Download complete: {downloaded_file} ({self._format_bytes(file_size)})")

                    if progress_callback:
                        progress_callback(100, "0 B/s", "00:00", self._format_bytes(file_size))

                    return {
                        "success": True,
                        "file_path": str(downloaded_file),
                        "file_size": file_size,
                        "file_size_str": self._format_bytes(file_size),
                        "error": None,
                    }
                else:
                    return {"success": False, "file_path": None, "file_size": 0, "error": "File tidak ditemukan setelah download selesai."}

        except subprocess.TimeoutExpired:
            if 'process' in locals():
                process.kill()
            return {"success": False, "file_path": None, "file_size": 0, "error": "Download timeout (>1 jam)."}
        except Exception as e:
            logger.error(f"Download error: {e}")
            return {"success": False, "file_path": None, "file_size": 0, "error": str(e)[:300]}

    @staticmethod
    def _format_bytes(size_bytes: int) -> str:
        """Convert bytes to human readable string"""
        if not size_bytes or size_bytes <= 0:
            return "Ukuran tidak diketahui"
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


