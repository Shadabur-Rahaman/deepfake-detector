# app/services/youtube_service.py - COMPLETE 403 FIX SOLUTION

import os
import uuid
import re
import logging
import subprocess
import time
import random
from pathlib import Path
from typing import Tuple, Dict

logger = logging.getLogger(__name__)

try:
    import yt_dlp
    YOUTUBE_AVAILABLE = True
    print("✅ yt-dlp imported successfully")
except ImportError:
    YOUTUBE_AVAILABLE = False
    print("⚠️ yt-dlp not available")

class YouTubeDownloader:
    """ULTIMATE: Anti-403 YouTube downloader with advanced blocking workarounds"""
    
    def __init__(self):
        self.download_dir = Path("downloaded_videos")
        self.download_dir.mkdir(exist_ok=True)
        
        # Clear yt-dlp cache on startup to prevent 403 errors
        self._clear_yt_dlp_cache()
        print(f"✅ YouTubeDownloader initialized, download_dir: {self.download_dir}")

    def _clear_yt_dlp_cache(self):
        """Clear yt-dlp cache to prevent 403 errors"""
        try:
            if YOUTUBE_AVAILABLE:
                # Clear cache using yt-dlp command
                subprocess.run(['yt-dlp', '--rm-cache-dir'], 
                             capture_output=True, text=True, check=False)
                logger.info("🧹 Cleared yt-dlp cache to prevent 403 errors")
        except Exception as e:
            logger.debug(f"Cache clear attempt: {e}")

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
                    logger.info(f"✅ Extracted video ID: {video_id} using pattern {i+1}")
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

    def get_anti_403_ydl_opts(self, video_id: str) -> list:
        """ANTI-403: Multiple yt-dlp configurations to bypass YouTube blocking"""
        
        safe_template = f"{video_id}_%(title).50s.%(ext)s"
        
        # Base configuration with anti-blocking measures
        base_config = {
            'outtmpl': str(self.download_dir / safe_template),
            'max_filesize': 200 * 1024 * 1024,  # 200MB
            'extract_flat': False,
            'writeinfojson': False,
            'writethumbnail': False,
            'noplaylist': True,
            'ignoreerrors': True,
            'no_warnings': True,
            'quiet': False,
            'skip_unavailable_fragments': True,
            'restrictfilenames': True,
            'retries': 10,  # More retries for 403 errors
            'socket_timeout': 60,
            'prefer_free_formats': True,
            
            # ANTI-403: Advanced headers rotation
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            },
            
            # ANTI-403: Anti-bot detection
            'sleep_interval': random.uniform(1, 3),
            'max_sleep_interval': 5,
            'sleep_interval_subtitles': 1,
        }

        # Strategy configurations in order of preference
        strategies = [
            # Strategy 1: Ultra-safe single format
            {
                **base_config,
                'format': 'worst[ext=mp4]/worst',  # Least demanding format
                'description': 'Ultra-safe lowest quality',
            },
            
            # Strategy 2: Web client simulation
            {
                **base_config,
                'format': 'best[height<=480][ext=mp4]/best[height<=360]',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web'],
                        'player_skip': ['dash', 'hls']
                    }
                },
                'description': 'Web client 480p max',
            },
            
            # Strategy 3: Android client simulation
            {
                **base_config,
                'format': 'best[height<=720]',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                    }
                },
                'description': 'Android client',
            },
            
            # Strategy 4: iOS client simulation
            {
                **base_config,
                'format': 'best',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios'],
                    }
                },
                'description': 'iOS client',
            },
            
            # Strategy 5: Mediaconnect fallback
            {
                **base_config,
                'format': 'best',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['mediaconnect'],
                    }
                },
                'description': 'MediaConnect client',
            }
        ]
        
        return strategies

    async def download_video(self, youtube_url: str) -> Tuple[str, str, Dict]:
        """ANTI-403: Download with advanced blocking workarounds"""
        
        if not YOUTUBE_AVAILABLE:
            raise ImportError("yt-dlp not installed. Install with: pip install yt-dlp")

        video_id = str(uuid.uuid4())
        
        try:
            # Clear cache before each download
            self._clear_yt_dlp_cache()
            
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            # URL processing
            original_url = youtube_url.strip()
            logger.info(f"🔍 Processing URL: {original_url}")
            
            if not self.validate_youtube_url(original_url):
                raise ValueError("Invalid YouTube URL format")
            
            yt_video_id = self.extract_video_id(original_url)
            normalized_url = self.normalize_url(original_url)
            clean_url = self.create_clean_url(yt_video_id)
            
            logger.info(f"📝 Original URL: {original_url}")
            logger.info(f"📝 Normalized URL: {normalized_url}")
            logger.info(f"📝 Clean URL: {clean_url}")
            logger.info(f"📝 Video ID: {yt_video_id}")
            
            # Get anti-403 strategies
            strategies = self.get_anti_403_ydl_opts(video_id)
            
            info = None
            downloaded_file = None
            successful_strategy = None
            
            # Try each strategy
            for strategy_idx, strategy in enumerate(strategies):
                logger.info(f"🎯 Strategy {strategy_idx + 1}/{len(strategies)}: {strategy.get('description')}")
                
                try:
                    # Clean strategy options
                    ydl_opts = {k: v for k, v in strategy.items() if k != 'description'}
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        # Try extract info first
                        try:
                            logger.info(f"📊 Extracting info with strategy {strategy_idx + 1}")
                            info = ydl.extract_info(clean_url, download=False)
                            
                            if not info:
                                continue
                                
                            # Check video availability
                            availability = info.get('availability', 'public')
                            if availability in ['private', 'premium_only', 'subscriber_only', 'needs_auth']:
                                logger.warning(f"Video is {availability}")
                                continue
                                
                            # Check for geo-blocking
                            if 'not available' in str(info.get('title', '')).lower():
                                logger.warning("Video appears to be geo-blocked")
                                continue
                                
                        except Exception as extract_error:
                            logger.warning(f"Extract failed for strategy {strategy_idx + 1}: {extract_error}")
                            continue
                        
                        # Try download
                        try:
                            logger.info(f"📥 Downloading with strategy {strategy_idx + 1}")
                            ydl.extract_info(clean_url, download=True)
                            
                            # Find downloaded file
                            for file in self.download_dir.glob(f"{video_id}_*"):
                                if file.is_file() and file.suffix.lower() in ('.mp4', '.webm', '.mkv', '.m4a', '.avi', '.mov'):
                                    downloaded_file = str(file)
                                    successful_strategy = strategy_idx + 1
                                    logger.info(f"✅ SUCCESS with strategy {successful_strategy}")
                                    break
                            
                            if downloaded_file:
                                break
                                
                        except Exception as download_error:
                            error_str = str(download_error).lower()
                            if '403' in error_str or 'forbidden' in error_str:
                                logger.warning(f"403 error with strategy {strategy_idx + 1}, trying next...")
                                time.sleep(random.uniform(2, 5))  # Longer delay after 403
                                continue
                            else:
                                logger.warning(f"Download failed for strategy {strategy_idx + 1}: {download_error}")
                                continue
                                
                except Exception as strategy_error:
                    logger.warning(f"Strategy {strategy_idx + 1} completely failed: {strategy_error}")
                    continue
            
            # Check if we succeeded
            if not downloaded_file or not info:
                # Final emergency attempt with subprocess
                logger.info("🚨 All strategies failed, trying emergency subprocess method")
                try:
                    emergency_file = await self._emergency_download(clean_url, video_id)
                    if emergency_file:
                        downloaded_file = emergency_file
                        # Get basic info for emergency download
                        info = {
                            'title': 'Emergency Download',
                            'duration': 60,
                            'uploader': 'Unknown',
                            'view_count': 0,
                            'upload_date': 'Unknown'
                        }
                except Exception as emergency_error:
                    logger.error(f"Emergency download failed: {emergency_error}")
            
            if not downloaded_file:
                raise ValueError("All download strategies failed. Video may be geo-blocked, private, or YouTube is blocking all requests.")

            # Verify file can be opened by OpenCV
            import cv2
            cap = cv2.VideoCapture(downloaded_file)
            if not cap.isOpened():
                cap.release()
                raise ValueError(f"Downloaded video file cannot be processed: {downloaded_file}")
            cap.release()

            # Create metadata
            duration = info.get('duration', 0)
            is_short = ('/shorts/' in original_url.lower() or (duration and duration <= 60))

            metadata = {
                'title': info.get('title', 'Unknown'),
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
                'description': (info.get('description', '') or '')[:200] + '...' if info.get('description') else '',
                'thumbnail': info.get('thumbnail', ''),
                'format': info.get('format_id', 'unknown'),
                'resolution': f"{info.get('width', 'unknown')}x{info.get('height', 'unknown')}",
                'successful_strategy': successful_strategy or 'emergency'
            }

            content_type = "YouTube Short" if is_short else "YouTube video"
            logger.info(f"✅ Successfully downloaded: {video_id} - {content_type}: {metadata['title']}")
            
            return video_id, downloaded_file, metadata
                
        except Exception as e:
            logger.error(f"YouTube processing error: {e}")
            raise ValueError(f"Failed to download YouTube content: {str(e)}")

    async def _emergency_download(self, url: str, video_id: str) -> str:
        """Emergency download using subprocess with minimal options"""
        try:
            output_path = self.download_dir / f"{video_id}_emergency.%(ext)s"
            
            cmd = [
                'yt-dlp',
                '--no-check-certificate',
                '--no-warnings',
                '--ignore-errors',
                '--format', 'worst',
                '--output', str(output_path),
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            # Find the downloaded file
            for file in self.download_dir.glob(f"{video_id}_emergency.*"):
                if file.is_file():
                    return str(file)
                    
            return None
            
        except Exception as e:
            logger.error(f"Emergency download failed: {e}")
            return None

    def cleanup_video(self, video_path: str):
        """Delete downloaded video file after processing"""
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                logger.info(f"🧹 Cleaned up: {video_path}")
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")

# Global singleton
if YOUTUBE_AVAILABLE:
    youtube_downloader = YouTubeDownloader()
    print("✅ YouTube downloader instance created with advanced anti-403 protection")
else:
    youtube_downloader = None
    print("⚠️ YouTube downloader not available")
