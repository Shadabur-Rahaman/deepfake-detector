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
    """Enhanced YouTube video downloader with comprehensive Shorts and URL format support"""
    
    def __init__(self):
        self.download_dir = Path("downloaded_videos")
        self.download_dir.mkdir(exist_ok=True)
        print(f"[OK] YouTubeDownloader initialized, download_dir: {self.download_dir}")
        
        # Clear yt-dlp cache on initialization to avoid stale data
        self._clear_ytdlp_cache()
    
    def _clear_ytdlp_cache(self):
        """Clear yt-dlp cache to avoid issues with stale data"""
        try:
            if YOUTUBE_AVAILABLE:
                import yt_dlp
                # ✅ FIX: Use proper cache clearing method for newer yt-dlp versions
                try:
                    # Try the newer method first
                    cache_dir = yt_dlp.utils.get_cache_dir()
                    if cache_dir and os.path.exists(cache_dir):
                        import shutil
                        shutil.rmtree(cache_dir, ignore_errors=True)
                        logger.info("[OK] Cleared yt-dlp cache")
                except AttributeError:
                    # Fallback for older versions or if get_cache_dir doesn't exist
                    try:
                        # Try alternative cache clearing
                        import tempfile
                        import glob
                        temp_dir = tempfile.gettempdir()
                        cache_patterns = [
                            os.path.join(temp_dir, "yt-dlp-*"),
                            os.path.join(temp_dir, ".yt-dlp-*"),
                            os.path.join(os.path.expanduser("~"), ".cache", "yt-dlp", "*"),
                            os.path.join(os.path.expanduser("~"), ".local", "share", "yt-dlp", "*")
                        ]
                        
                        for pattern in cache_patterns:
                            for cache_path in glob.glob(pattern):
                                if os.path.isdir(cache_path):
                                    shutil.rmtree(cache_path, ignore_errors=True)
                        
                        logger.info("[OK] Cleared yt-dlp cache using fallback method")
                    except Exception:
                        logger.debug("[INFO] yt-dlp cache clearing not needed or not available")
        except Exception as e:
            logger.debug(f"[INFO] yt-dlp cache management: {e}")

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
                    logger.info(f"[OK] Extracted video ID: {video_id} using pattern {i+1}")
                    return video_id

        raise ValueError(f"Could not extract valid video ID from URL: {url}")

    def validate_youtube_url(self, url: str) -> bool:
        """Enhanced validation for YouTube URLs including Shorts"""
        youtube_domains = [
            'youtube.com', 'www.youtube.com', 'm.youtube.com',
            'youtu.be', 'www.youtu.be'
        ]
        
        url_lower = url.lower().strip()
        
        for domain in youtube_domains:
            if domain in url_lower:
                return True
        
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url.strip()):
            return True
            
        return False

    def create_clean_url(self, video_id: str) -> str:
        """Create a canonical YouTube video URL for yt-dlp."""
        return f"https://www.youtube.com/watch?v={video_id}"

    def normalize_url(self, url: str) -> str:
        """Normalize various YouTube URL formats for processing"""
        url = url.strip()
        
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return f"https://www.youtube.com/watch?v={url}"
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        if 'youtu.be/' in url:
            video_id_match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
            if video_id_match:
                return f"https://www.youtube.com/watch?v={video_id_match.group(1)}"
        
        if '/shorts/' in url:
            video_id_match = re.search(r'/shorts/([a-zA-Z0-9_-]{11})', url)
            if video_id_match:
                return f"https://www.youtube.com/watch?v={video_id_match.group(1)}"
        
        if '/live/' in url:
            video_id_match = re.search(r'/live/([a-zA-Z0-9_-]{11})', url)
            if video_id_match:
                return f"https://www.youtube.com/watch?v={video_id_match.group(1)}"
        
        return url

    def get_fast_ydl_opts(self, video_id: str) -> dict:
        """OPTIMIZED: Fast download options with minimal delays"""
        
        safe_template = f"{video_id}_%(title).50s.%(ext)s"
        
        return {
            # OPTIMIZED: Single format selection for speed
            'format': 'best[height<=480]/worst',
            'outtmpl': str(self.download_dir / safe_template),
            'max_filesize': 50 * 1024 * 1024,  # Reduced for faster download
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

    def get_ydl_opts_with_fallback(self, video_id: str) -> dict:
        """ENHANCED: Comprehensive format fallback options with better error handling"""
        
        safe_template = f"{video_id}_%(title).50s.%(ext)s"
        
        return {
            # CRITICAL: Updated format selection for 2024 YouTube changes - more flexible
            'format': (
                'bestvideo[height<=720]+bestaudio/best[height<=720]/bestvideo+bestaudio/best/worst'
            ),
            'outtmpl': str(self.download_dir / safe_template),
            'max_filesize': 100 * 1024 * 1024,
            'extract_flat': False,
            'writeinfojson': False,
            'writethumbnail': False,
            'noplaylist': True,
            'ignoreerrors': True,
            'no_warnings': False,
            'quiet': False,
            'skip_unavailable_fragments': True,
            'restrictfilenames': True,
            'retries': 3,  # Reduced retries to avoid rate limiting
            'socket_timeout': 30,
            'fragment_retries': 3,
            'file_access_retries': 3,
            
            # CRITICAL: Updated headers for 2024 YouTube compatibility
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Ch-Ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            },
            
            # Additional compatibility options for 2024
            'cookiefile': None,
            'prefer_free_formats': True,
            'merge_output_format': 'mp4',
            
            # CRITICAL: YouTube-specific extractor options - more permissive
            'extractor_args': {
                'youtube': {
                    'skip': ['translated_subs', 'automatic_captions', 'subtitles', 'comments'],
                    'player_skip': ['configs', 'webpage'],
                    'comment_sort': ['top'],
                    'max_comments': [0],
                    'player_client': ['android', 'web']
                }
            },
            
            # Additional options to handle rate limiting
            'sleep_interval': 1,
            'max_sleep_interval': 5,
            'sleep_interval_subtitles': 1,
            'sleep_interval_requests': 1
        }

    def _check_ytdlp_version(self):
        """Check if yt-dlp is up to date and suggest update if needed"""
        try:
            if YOUTUBE_AVAILABLE:
                import yt_dlp
                version = yt_dlp.version.__version__
                logger.info(f"[INFO] Using yt-dlp version: {version}")
                
                # Check if version is recent (basic check)
                version_parts = version.split('.')
                if len(version_parts) >= 2:
                    major = int(version_parts[0])
                    minor = int(version_parts[1])
                    if major < 2024 or (major == 2024 and minor < 1):
                        logger.warning("[WARNING] yt-dlp version may be outdated. Consider updating with: pip install -U yt-dlp")
        except Exception as e:
            logger.warning(f"[WARNING] Could not check yt-dlp version: {e}")

    async def download_video(self, youtube_url: str) -> Tuple[str, str, Dict]:
        """OPTIMIZED: Fast download with minimal API calls and delays"""
        
        if not YOUTUBE_AVAILABLE:
            raise ImportError("yt-dlp not installed. Install with: pip install yt-dlp")
        
        video_id = str(uuid.uuid4())
        
        try:
            # Fast URL processing
            original_url = youtube_url.strip()
            logger.info(f"🔍 Processing URL: {original_url}")
            
            if not self.validate_youtube_url(original_url):
                raise ValueError("Invalid YouTube URL format")
            
            yt_video_id = self.extract_video_id(original_url)
            clean_url = f"https://www.youtube.com/watch?v={yt_video_id}"
            
            logger.info(f"📝 Video ID: {yt_video_id}")
            
            # OPTIMIZED: Fast download options
            ydl_opts = self.get_fast_ydl_opts(video_id)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info("[DATA] Extracting video information...")
                
                # OPTIMIZED: Single fast extraction attempt
                logger.info("[LOADING] Fast extraction...")
                info = ydl.extract_info(clean_url, download=True)
                if not info:
                    raise Exception("No video information extracted")
                
                # OPTIMIZED: Fast success path - no complex fallbacks
                logger.info(f"[OK] Successfully extracted info on attempt 1.1")
                
                # Fast validation
                availability = info.get('availability', 'public')
                if availability in ['private', 'premium_only', 'subscriber_only', 'needs_auth']:
                    raise ValueError(f"Video is {availability} and cannot be accessed")

                duration = info.get('duration', 0)
                if duration and duration > 300:
                    raise ValueError("Video too long. Please use videos or Shorts under 5 minutes.")

                # Detect if it's a YouTube Short
                is_short = '/shorts/' in clean_url or (info.get('duration', 0) <= 60)
                if is_short:
                    logger.info("[INFO] Detected YouTube Short")

                # Fast download - video is already downloaded from extract_info above
                video_title = info.get('title', 'Unknown')
                logger.info(f"📥 Downloading {'YouTube Short' if is_short else 'YouTube video'}: {video_title}")
                
                # Find the downloaded file
                downloaded_file = None
                for file_path in self.download_dir.glob(f"{video_id}_*"):
                    if file_path.is_file() and file_path.stat().st_size > 1000:  # At least 1KB
                        downloaded_file = file_path
                        break
                
                if not downloaded_file:
                    raise Exception("Download completed but no valid file found")
                
                logger.info(f"[OK] Valid downloaded file found: {downloaded_file}")
                
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
                
                content_type = "YouTube Short" if is_short else "YouTube video"
                logger.info(f"[OK] Successfully downloaded: {video_id} - {content_type}: {metadata['title']}")
                
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
                    if info:
                        break
                    
                    # Add delay between different option sets to avoid rate limiting
                    if opt_index > 0:
                        delay = 2 * opt_index  # Increasing delay: 2s, 4s, 6s, etc.
                        logger.info(f"[LOADING] Waiting {delay}s before trying different options...")
                        time.sleep(delay)
                        
                    with yt_dlp.YoutubeDL(current_opts) as current_ydl:
                        for i, url_attempt in enumerate(urls_to_try):
                            try:
                                logger.info(f"[LOADING] Attempt {opt_index+1}.{i+1}: {url_attempt}")
                                info = current_ydl.extract_info(url_attempt, download=False)
                                if info:
                                    logger.info(f"[OK] Successfully extracted info on attempt {opt_index+1}.{i+1}")
                                    break
                            except Exception as e:
                                last_error = e
                                error_msg = str(e)
                                logger.warning(f"[WARNING] Attempt {opt_index+1}.{i+1} failed: {error_msg}")
                                
                                # Ensure we always have a meaningful error message
                                if not error_msg or error_msg.strip() == "":
                                    last_error = Exception("Unknown extraction error - no specific error message provided")
                                    error_msg = str(last_error)
                                
                                # Check for specific blocking errors
                                if "403" in error_msg or "Forbidden" in error_msg:
                                    logger.error(f"[ERROR] YouTube is blocking access (403 Forbidden) for {url_attempt}")
                                    # Add progressive delay for 403 errors
                                    delay = min(5 + opt_index * 2, 15)  # 5s, 7s, 9s, 11s, 13s, 15s max
                                    if opt_index < len(ydl_options_to_try) - 1 or i < len(urls_to_try) - 1:
                                        logger.info(f"[LOADING] Adding {delay}s delay due to 403 error...")
                                        time.sleep(delay)
                                    if opt_index == len(ydl_options_to_try) - 1 and i == len(urls_to_try) - 1:
                                        # Last attempt failed
                                        raise ValueError("YouTube is blocking access to this video. This may be due to geographic restrictions, age restrictions, or YouTube's anti-bot measures. Please try a different video or try again later.")
                                elif "fragment" in error_msg.lower() and "not found" in error_msg.lower():
                                    logger.warning(f"[WARNING] Fragment download error: {error_msg}")
                                    # Add delay for fragment errors
                                    if opt_index < len(ydl_options_to_try) - 1 or i < len(urls_to_try) - 1:
                                        logger.info("[LOADING] Adding delay due to fragment error...")
                                        time.sleep(2)
                                continue
                
                if not info:
                    # Try one final attempt with format listing to understand what's available
                    try:
                        logger.info("[LOADING] Final attempt - checking available formats...")
                        list_opts = {
                            'quiet': False,
                            'no_warnings': False,
                            'extract_flat': False,
                            'listformats': True,
                            'http_headers': {
                                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
                            },
                            'extractor_args': {
                                'youtube': {
                                    'player_client': ['android'],
                                    'skip': ['translated_subs', 'automatic_captions', 'subtitles', 'comments']
                                }
                            }
                        }
                        with yt_dlp.YoutubeDL(list_opts) as list_ydl:
                            list_ydl.extract_info(clean_url, download=False)
                        logger.info("[INFO] Format listing completed - check output above for available formats")
                    except Exception as list_e:
                        logger.warning(f"[WARNING] Format listing also failed: {list_e}")
                    
                    # Handle the case where last_error is None
                    if last_error is None:
                        error_msg = "Unable to extract video information from any URL format. This may be due to YouTube's anti-bot measures, geographic restrictions, or the video being unavailable."
                        logger.error(f"[ERROR] YouTube download failed: {error_msg}")
                        raise ValueError("YouTube is blocking access to this video. This may be due to geographic restrictions, age restrictions, YouTube's anti-bot measures, or the video being unavailable. Please try a different video or try again later.")
                    else:
                        error_msg = f"Unable to extract video information from any URL format. Last error: {last_error}"
                        logger.error(f"[ERROR] YouTube download failed: {error_msg}")
                        
                        # Provide more helpful error messages based on the last error
                        if "403" in str(last_error) or "Forbidden" in str(last_error):
                            raise ValueError("YouTube is blocking access to this video. This may be due to geographic restrictions, age restrictions, or YouTube's anti-bot measures. Please try a different video or try again later.")
                        elif "Private video" in str(last_error):
                            raise ValueError("This video is private and cannot be accessed.")
                        elif "Video unavailable" in str(last_error):
                            raise ValueError("This video is unavailable. It may have been deleted or made private.")
                        else:
                            raise ValueError(f"Unable to access video: {error_msg}")
                
                # Validation and download
                availability = info.get('availability', 'public')
                if availability in ['private', 'premium_only', 'subscriber_only', 'needs_auth']:
                    raise ValueError(f"Video is {availability} and cannot be accessed")

                duration = info.get('duration', 0)
                if duration and duration > 300:
                    raise ValueError("Video too long. Please use videos or Shorts under 5 minutes.")

                # Detect if it's a YouTube Short
                is_short = False
                original_webpage_url = info.get('webpage_url', '')
                if ('/shorts/' in original_url.lower() or 
                    '/shorts/' in original_webpage_url.lower() or 
                    (duration and duration <= 60)):
                    is_short = True

                # Log available formats for debugging
                try:
                    formats = info.get('formats', [])
                    if formats:
                        logger.info(f"[DATA] Available formats: {len(formats)}")
                        for fmt in formats[:5]:  # Show first 5 formats
                            logger.info(f"  Format {fmt.get('format_id', 'unknown')}: {fmt.get('ext', 'unknown')} {fmt.get('resolution', 'unknown')} {fmt.get('filesize', 'unknown')} bytes")
                    else:
                        logger.warning("[WARNING] No format information available")
                except Exception as e:
                    logger.warning(f"[WARNING] Could not log format info: {e}")
                
                # Download with multiple attempts and enhanced error handling
                video_title = info.get('title', 'Unknown')
                logger.info(f"📥 Downloading {'YouTube Short' if is_short else 'YouTube video'}: {video_title}")
                
                downloaded = False
                last_download_error = None
                
                # Enhanced download options for better compatibility
                enhanced_opts = ydl_opts.copy()
                enhanced_opts.update({
                    'format': 'bestvideo+bestaudio/best/worst',  # More flexible format
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
                    },
                    'extractor_args': {
                        'youtube': {
                            'skip': ['translated_subs', 'automatic_captions', 'subtitles', 'comments'],
                            'player_skip': ['configs', 'webpage'],
                        }
                    },
                    # Add fragment handling options
                    'skip_unavailable_fragments': True,
                    'fragment_retries': 5,
                    'file_access_retries': 3
                })
                
                for i, url_attempt in enumerate(urls_to_try):
                    try:
                        logger.info(f"📥 Download attempt {i+1}: {url_attempt}")
                        
                        # Try with enhanced options first
                        with yt_dlp.YoutubeDL(enhanced_opts) as enhanced_ydl:
                            enhanced_ydl.extract_info(url_attempt, download=True)
                            # Verify the file was actually downloaded
                            downloaded_file = None
                            for file in self.download_dir.glob(f"{video_id}_*"):
                                if file.is_file() and file.suffix.lower() in ('.mp4', '.webm', '.mkv', '.m4a'):
                                    downloaded_file = str(file)
                                    break
                            
                            if downloaded_file and os.path.exists(downloaded_file) and os.path.getsize(downloaded_file) > 0:
                                downloaded = True
                                logger.info(f"[OK] Enhanced download successful on attempt {i+1}")
                                break
                            else:
                                logger.warning(f"[WARNING] Enhanced download reported success but no valid file found")
                                raise Exception("Download reported success but no valid file found")
                            
                    except Exception as e:
                        last_download_error = e
                        error_msg = str(e)
                        logger.warning(f"[WARNING] Enhanced download attempt {i+1} failed: {error_msg}")
                        
                        # Try with original options as fallback
                        try:
                            logger.info(f"📥 Trying original options for attempt {i+1}...")
                            ydl.extract_info(url_attempt, download=True)
                            # Verify the file was actually downloaded
                            downloaded_file = None
                            for file in self.download_dir.glob(f"{video_id}_*"):
                                if file.is_file() and file.suffix.lower() in ('.mp4', '.webm', '.mkv', '.m4a'):
                                    downloaded_file = str(file)
                                    break
                            
                            if downloaded_file and os.path.exists(downloaded_file) and os.path.getsize(downloaded_file) > 0:
                                downloaded = True
                                logger.info(f"[OK] Original options download successful on attempt {i+1}")
                                break
                            else:
                                logger.warning(f"[WARNING] Original options reported success but no valid file found")
                                raise Exception("Original options reported success but no valid file found")
                        except Exception as fallback_e:
                            logger.warning(f"[WARNING] Original options also failed: {fallback_e}")
                        
                        # Check for specific errors and provide helpful messages
                        if "403" in error_msg or "Forbidden" in error_msg:
                            logger.error("[ERROR] YouTube is blocking the download (403 Forbidden). This video may be restricted or YouTube is blocking automated access.")
                            if i == len(urls_to_try) - 1:  # Last attempt
                                raise Exception("YouTube access blocked. Please try again later or use a different video.")
                        elif "Requested format is not available" in error_msg or "fragment" in error_msg.lower():
                            logger.warning("[LOADING] Format/fragment issue, trying with different format options...")
                            # Try with more permissive format and fragment handling
                            try:
                                fallback_opts = ydl_opts.copy()
                                fallback_opts.update({
                                    'format': 'bestvideo+bestaudio/best/worst',
                                    'skip_unavailable_fragments': True,
                                    'fragment_retries': 10,
                                    'file_access_retries': 5,
                                    'http_headers': {
                                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
                                    }
                                })
                                with yt_dlp.YoutubeDL(fallback_opts) as fallback_ydl:
                                    fallback_ydl.extract_info(url_attempt, download=True)
                                    # Verify the file was actually downloaded
                                    downloaded_file = None
                                    for file in self.download_dir.glob(f"{video_id}_*"):
                                        if file.is_file() and file.suffix.lower() in ('.mp4', '.webm', '.mkv', '.m4a'):
                                            downloaded_file = str(file)
                                            break
                                    
                                    if downloaded_file and os.path.exists(downloaded_file) and os.path.getsize(downloaded_file) > 0:
                                        downloaded = True
                                        logger.info(f"[OK] Fallback format download successful")
                                        break
                                    else:
                                        logger.warning(f"[WARNING] Fallback format reported success but no valid file found")
                                        raise Exception("Fallback format reported success but no valid file found")
                            except Exception as fallback_e:
                                logger.warning(f"[WARNING] Fallback format also failed: {fallback_e}")
                        continue

                if not downloaded:
                    error_msg = f"Failed to download video with any URL format. Last error: {last_download_error}"
                    logger.error(f"[ERROR] {error_msg}")
                    
                    # Provide specific suggestions based on the error
                    if last_download_error and "403" in str(last_download_error):
                        raise Exception("YouTube is blocking access to this video. This may be due to geographic restrictions, age restrictions, or YouTube's anti-bot measures. Please try a different video or try again later. Consider updating yt-dlp with: pip install -U yt-dlp")
                    elif last_download_error and "fragment" in str(last_download_error).lower():
                        raise Exception("Video fragment download failed. This may be due to network issues or YouTube's video delivery changes. Please try again later or update yt-dlp with: pip install -U yt-dlp")
                    else:
                        raise Exception(f"{error_msg}. Consider updating yt-dlp with: pip install -U yt-dlp")

                # Find downloaded file with robust validation
                downloaded_file = None
                logger.info(f"[LOADING] Looking for downloaded files with pattern: {video_id}_*")
                
                for file in self.download_dir.glob(f"{video_id}_*"):
                    if file.is_file() and file.suffix.lower() in ('.mp4', '.webm', '.mkv', '.m4a'):
                        file_size = os.path.getsize(file)
                        logger.info(f"[LOADING] Found potential file: {file.name} (size: {file_size} bytes)")
                        if file_size > 0:  # Ensure file has content
                            downloaded_file = str(file)
                            logger.info(f"[OK] Valid downloaded file found: {downloaded_file}")
                            break
                        else:
                            logger.warning(f"[WARNING] File {file.name} exists but is empty (0 bytes)")

                if not downloaded_file or not os.path.exists(downloaded_file):
                    logger.error(f"[ERROR] No valid downloaded file found for video_id: {video_id}")
                    logger.error(f"[ERROR] Files in download directory:")
                    for file in self.download_dir.glob(f"{video_id}_*"):
                        logger.error(f"  - {file.name} (exists: {file.exists()}, size: {os.path.getsize(file) if file.exists() else 'N/A'})")
                    raise FileNotFoundError("Downloaded video file not found or is empty")

                # Create enhanced metadata with comprehensive information
                metadata = {
                    'title': video_title,
                    'duration': duration,
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', 'Unknown'),
                    'original_url': original_url,
                    'normalized_url': normalized_url,
                    'cleaned_url': clean_url,
                    'video_id': yt_video_id,
                    'is_short': is_short,
                    'file_size_mb': round(os.path.getsize(downloaded_file) / (1024 * 1024), 2),
                    'description': (info.get('description', '') or '')[:500] + '...' if info.get('description') else '',  # Extended description
                    'thumbnail': info.get('thumbnail', ''),
                    'format': info.get('format_id', 'unknown'),
                    'resolution': f"{info.get('width', 'unknown')}x{info.get('height', 'unknown')}",
                    # Enhanced metadata for bias detection
                    'tags': info.get('tags', []),
                    'category': info.get('category', 'Unknown'),
                    'uploader_id': info.get('uploader_id', ''),
                    'channel': info.get('channel', ''),
                    'channel_id': info.get('channel_id', ''),
                    'like_count': info.get('like_count', 0),
                    'dislike_count': info.get('dislike_count', 0),
                    'comment_count': info.get('comment_count', 0),
                    'age_limit': info.get('age_limit', 0),
                    'is_live': info.get('is_live', False),
                    'was_live': info.get('was_live', False),
                    'live_status': info.get('live_status', 'not_live'),
                    'availability': info.get('availability', 'public'),
                    'license': info.get('license', ''),
                    'subtitles': info.get('subtitles', {}),
                    'automatic_captions': info.get('automatic_captions', {}),
                    'chapters': info.get('chapters', []),
                    'heatmap': info.get('heatmap', {}),
                    'webpage_url': info.get('webpage_url', ''),
                    'original_url': original_url
                }

                content_type = "YouTube Short" if is_short else "YouTube video"
                logger.info(f"[OK] Successfully downloaded: {video_id} - {content_type}: {metadata['title']}")
                
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
    print("[OK] YouTube downloader instance created with comprehensive Shorts support")
else:
    youtube_downloader = None
    print("[WARNING] YouTube downloader not available")
