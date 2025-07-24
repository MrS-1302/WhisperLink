import yt_dlp
import json
import os
import requests
from PIL import Image
from io import BytesIO

from app.utils.database_structure import db

class QuietLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

class DownloadStatus:
    def __init__(self):
        self.progress = 0.0
        self.status = 'pending'
        self.filename = None
        self.total_bytes = None
        self.downloaded_bytes = 0
        self.speed = None
        self.eta = None
        self.link_id = None

    def update(self, d):
        self.status = d.get('status', self.status)
        self.filename = d.get('filename', self.filename)
        self.total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        self.downloaded_bytes = d.get('downloaded_bytes', 0)
        self.speed = d.get('speed')
        self.eta = d.get('eta')

        if self.total_bytes:
            self.progress = self.downloaded_bytes / self.total_bytes * 100

class Downloader:
    def __init__(self, url, storage_dir='./storage'):
        self.url = url
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.status = DownloadStatus()
        self.info = {}

    def _hook(self, d):
        self.status.update(d)

    def download(self):
        db.execute("INSERT INTO links (Link, Title) VALUES (?, ?)", (self.url, ''))
        row = db.fetch_one("SELECT LinkID FROM links ORDER BY LinkID DESC LIMIT 1")
        self.link_id = row[0] if row else None

        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': os.path.join(self.storage_dir, str(self.link_id)+'.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'logger': QuietLogger(),
            'progress_hooks': [self._hook],
            'rate_limit': 512 * 1024,  # 512 KB/s
        }
    
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            self.info = ydl.extract_info(self.url, download=False)
            db.execute("UPDATE links SET Title = ? WHERE LinkID = ?", (self.info.get('title'), self.link_id))
            self._download_thumbnail()

    def _download_thumbnail(self):
        thumb_url = self.info.get('thumbnail')
        if not thumb_url:
            return

        try:
            response = requests.get(thumb_url, stream=True)
            response.raise_for_status()

            image = Image.open(BytesIO(response.content)).convert('RGB')
            thumb_filename = f"{self.link_id}.webp"
            thumb_path = os.path.join(self.storage_dir, thumb_filename)
            image.save(thumb_path, 'WEBP', quality=85)

            self.info['thumbnail_file'] = thumb_filename
        except Exception as e:
            print(f"Hiba a thumbnail letöltésekor: {e}")
            self.info['thumbnail_file'] = None

    def get_title(self):
        return self.info.get('title')

    def get_result_json(self):
        return json.dumps({
            'title': self.info.get('title'),
            'id': self.info.get('id'),
            'audio_file': f"{self.info.get('title')} - {self.info.get('id')}.mp3",
            'thumbnail_file': self.info.get('thumbnail_file')
        }, indent=4)

    def get_status(self):
        return {
            'status': self.status.status,
            'progress': round(self.status.progress, 2),
            'filename': self.status.filename,
            'speed': self._format_speed(self.status.speed),
            'eta': self._format_eta(self.status.eta)
        }

    @staticmethod
    def _format_speed(speed):
        if not speed:
            return None
        # Byte/sec -> MB/s
        return f"{speed / 1024 / 1024:.2f} MB/s"

    @staticmethod
    def _format_eta(eta):
        if not eta:
            return None
        mins, secs = divmod(int(eta), 60)
        return f"{mins:02d}:{secs:02d}"
