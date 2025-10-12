import os
import uuid
import re
import logging
import time
from pathlib import Path
from typing import Tuple, Dict

logger = logging.getLogger(__name__)

# Try to import yt-dlp
try:
    import yt_dlp
    YOUTUBE_AVAILABLE = True
    print("[OK] yt-dlp imported successfully")
except ImportError:
    YOUTUBE_AVAILABLE = False
    print("[WARNING] yt-dlp not available")

class YouTubeDownloader:
    """OPTIMIZED: Fast YouTube video downloader with minimal delays"""
    
    def __init__(self):
        self.download_dir = Path("downloaded_videos")
        self.download_dir.mkdir(exist_ok=True)
        print(f"[OK] YouTubeDownloader initialized, download_dir: {self.download_dir}")

    def extract_video_id(self, url: str) -> str:
        """Extract YouTube video ID from ALL possible URL formats"""
        url = url.strip()
        
        patterns = [
            r"(?:https?://)?(?:www\.|m\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
            r"(?:https?://)?(?:www\.|m\.)?youtube\.com/watch\?(?:.*&)?v=([a-zA-Z0-9_-]{11})",
            r"(?:https?://)?(?:www\.|m\.)?youtube\.com/live/([a-zA-Z0-9_-]{11})",
            r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})",
            r"(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})",
            r"(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})",
            r"[?&]v=([a-zA-Z0-9_-]{11})",
            r"^([a-zA-Z0-9_-]{11})$"
        ]

        for i, pattern in enumerate(patterns):
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                video_id = match.group(1)
                if len(video_id) == 11:
                    return video_id

        raise ValueError(f"Could not extract valid video ID from URL: {url}")

    def validate_youtube_url(self, url: str) -> bool:
        """Enhanced validation for YouTube URLs including Shorts"""
        youtube_domains = [
            'youtube.com', 'www.youtube.com', 'm.youtube.com',
            'youtu.be', 'www.youtu.be'
        ]
        
        url_lower = url.lower()
        
        # Check if URL contains any YouTube domain
        has_youtube_domain = any(domain in url_lower for domain in youtube_domains)
        
        # Check for video ID pattern
        has_video_id = bool(re.search(r'[a-zA-Z0-9_-]{11}', url))
        
        return has_youtube_domain and has_video_id

    def get_fast_ydl_opts(self, video_id: str) -> dict:
        """OPTIMIZED: Fast download options with minimal delays"""
        
        safe_template = f"{video_id}_%(title).50s.%(ext)s"
        
        return {
            # OPTIMIZED: Flexible format selection for speed
            'format': 'best[height<=720]+bestaudio/best[height<=720]/bestvideo+bestaudio/best/worst',
            'outtmpl': str(self.download_dir / safe_template),
            'max_filesize': 75 * 1024 * 1024,  # Balanced for quality and speed
            'extract_flat': False,
            'writeinfojson': False,
            'writethumbnail': False,
            'noplaylist': True,
            'ignoreerrors': True,
            'no_warnings': True,  # Suppress warnings for speed
            'quiet': True,  # Quiet mode for speed
            'skip_unavailable_fragments': True,
            'restrictfilenames': True,
            'retries': 1,  # Minimal retries for speed
            'socket_timeout': 10,  # Faster timeout
            'fragment_retries': 1,  # Minimal fragment retries
            'file_access_retries': 1,
            # OPTIMIZED: Fast headers
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            # OPTIMIZED: Disable unnecessary features
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writeannotations': False,
            'writedescriptions': False,
            'writecomments': False,
            'writeinfojson': False,
            'writethumbnail': False,
            'writedescription': False,
            'writeannotations': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writecomments': False,
            'writethumbnail': False,
            'writedescription': False,
            'writeannotations': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writecomments': False,
            # OPTIMIZED: Minimal sleep times
            'sleep_interval': 0,
            'max_sleep_interval': 0,
            'sleep_interval_requests': 0,
            'sleep_interval_subtitles': 0,
            'sleep_interval_requests': 0,
            'sleep_interval_subtitles': 0,
        }

    async def download_video(self, youtube_url: str) -> Tuple[str, str, Dict]:
        """OPTIMIZED: Fast download with minimal API calls and delays"""
        
        if not YOUTUBE_AVAILABLE:
            raise ImportError("yt-dlp not installed. Install with: pip install yt-dlp")

        video_id = str(uuid.uuid4())
        
        try:
            # Fast URL processing
            original_url = youtube_url.strip()
            if not self.validate_youtube_url(original_url):
                raise ValueError("Invalid YouTube URL format")
            
            yt_video_id = self.extract_video_id(original_url)
            clean_url = f"https://www.youtube.com/watch?v={yt_video_id}"
            
            # OPTIMIZED: Fast download options
            ydl_opts = self.get_fast_ydl_opts(video_id)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=True)
                
                # Fallback if format not available
                if not info:
                    fallback_opts = ydl_opts.copy()
                    fallback_opts['format'] = 'best/worst'
                    with yt_dlp.YoutubeDL(fallback_opts) as fallback_ydl:
                        info = fallback_ydl.extract_info(clean_url, download=True)
                        if not info:
                            raise Exception("No video information extracted with any format")
                
                # Fast validation
                availability = info.get('availability', 'public')
                if availability in ['private', 'premium_only', 'subscriber_only', 'needs_auth']:
                    raise ValueError(f"Video is {availability} and cannot be accessed")

                duration = info.get('duration', 0)
                if duration and duration > 300:
                    raise ValueError("Video too long. Please use videos or Shorts under 5 minutes.")

                # Detect if it's a YouTube Short
                is_short = '/shorts/' in clean_url or (info.get('duration', 0) <= 60)

                # Fast download - video is already downloaded from extract_info above
                video_title = info.get('title', 'Unknown')
                
                # Find the downloaded file
                downloaded_file = None
                for file_path in self.download_dir.glob(f"{video_id}_*"):
                    if file_path.is_file() and file_path.stat().st_size > 1000:  # At least 1KB
                        downloaded_file = file_path
                        break
                
                if not downloaded_file:
                    raise Exception("Download completed but no valid file found")
                
                # Prepare metadata
                metadata = {
                    'title': info.get('title', 'Unknown'),
                    'description': info.get('description', ''),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'upload_date': info.get('upload_date', ''),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'is_short': is_short,
                    'webpage_url': info.get('webpage_url', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'format_id': info.get('format_id', 'unknown'),
                    'filesize': downloaded_file.stat().st_size
                }
                
                return video_id, downloaded_file, metadata
                
        except Exception as e:
            logger.error(f"YouTube processing error: {e}")
            
            # Provide helpful error messages with suggestions
            error_str = str(e)
            if "403" in error_str or "Forbidden" in error_str:
                raise ValueError("YouTube is blocking access to this video. This may be due to geographic restrictions, age restrictions, or YouTube's anti-bot measures. Please try a different video or try again later. Consider updating yt-dlp with: pip install -U yt-dlp")
            elif "fragment" in error_str.lower():
                raise ValueError("Video fragment download failed. This may be due to network issues or YouTube's video delivery changes. Please try again later or update yt-dlp with: pip install -U yt-dlp")
            elif "Private video" in error_str:
                raise ValueError("This video is private and cannot be accessed.")
            elif "Video unavailable" in error_str:
                raise ValueError("This video is unavailable. It may have been deleted or made private.")
            else:
                raise ValueError(f"Failed to download YouTube content: {error_str}. Consider updating yt-dlp with: pip install -U yt-dlp")

    def cleanup_video(self, video_path: str):
        """Delete downloaded video file after processing"""
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                logger.info(f"🧹 Cleaned up: {video_path}")
        except Exception as e:
            logger.error(f"[ERROR] Cleanup failed: {e}")

# Global singleton
if YOUTUBE_AVAILABLE:
    youtube_downloader = YouTubeDownloader()
    print("[OK] YouTube downloader instance created with fast optimization")
else:
    youtube_downloader = None
    print("[WARNING] YouTube downloader not available")
