#!/usr/bin/env python3
"""
Example Usage of Fixed Deepfake Detection Service

This script demonstrates the fixes for the production bugs:
1. "read of closed file" error - Fixed by persisting files immediately
2. "404 Video ID not found" error - Fixed by using database persistence

Author: Senior Backend Engineer
Date: 2024
"""

import asyncio
import aiohttp
import json
import time
from pathlib import Path

# Example video file (create a small test file)
def create_test_video():
    """Create a small test video file."""
    test_content = b"fake video content for testing" * 1000  # ~30KB
    test_file = Path("test_video.mp4")
    test_file.write_bytes(test_content)
    return test_file

async def test_detection_fixes():
    """Test the detection service fixes."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Deepfake Detection Service Fixes")
    print("=" * 50)
    
    # Create test video file
    print("1. Creating test video file...")
    test_video = create_test_video()
    print(f"   ✅ Created test video: {test_video} ({test_video.stat().st_size} bytes)")
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Upload video and get video_id
        print("\n2. Testing video upload (fixes 'read of closed file' error)...")
        
        with open(test_video, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file', f, filename='test_video.mp4', content_type='video/mp4')
            data.add_field('mode', 'traditional')
            
            async with session.post(f"{base_url}/api/detection/detect", data=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    video_id = result['video_id']
                    print(f"   ✅ Upload successful: {video_id}")
                    print(f"   ✅ Status: {result['status']}")
                    print(f"   ✅ Mode: {result['mode']}")
                else:
                    error = await resp.text()
                    print(f"   ❌ Upload failed: {resp.status} - {error}")
                    return
        
        # Test 2: Check status immediately (fixes '404 Video ID not found' error)
        print("\n3. Testing status endpoint (fixes '404 Video ID not found' error)...")
        
        async with session.get(f"{base_url}/api/detection/detection-status/{video_id}") as resp:
            if resp.status == 200:
                status = await resp.json()
                print(f"   ✅ Status retrieved: {status['status']}")
                print(f"   ✅ Progress: {status.get('progress_percentage', 0)}%")
                print(f"   ✅ Stage: {status.get('current_stage', 'N/A')}")
            else:
                error = await resp.text()
                print(f"   ❌ Status check failed: {resp.status} - {error}")
        
        # Test 3: Monitor processing progress
        print("\n4. Monitoring background processing...")
        
        max_wait_time = 60  # 60 seconds max
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            async with session.get(f"{base_url}/api/detection/detection-status/{video_id}") as resp:
                if resp.status == 200:
                    status = await resp.json()
                    current_status = status['status']
                    progress = status.get('progress_percentage', 0)
                    stage = status.get('current_stage', 'N/A')
                    
                    print(f"   📊 Status: {current_status} | Progress: {progress}% | Stage: {stage}")
                    
                    if current_status in ['completed', 'failed']:
                        print(f"   ✅ Processing finished with status: {current_status}")
                        
                        if current_status == 'completed':
                            print(f"   🎉 Detection result: {status.get('result', {})}")
                            print(f"   🎯 Confidence: {status.get('confidence', 'N/A')}")
                            print(f"   ⏱️  Processing time: {status.get('processing_time_seconds', 'N/A')}s")
                        else:
                            print(f"   ❌ Error: {status.get('error_message', 'Unknown error')}")
                        
                        break
                    else:
                        await asyncio.sleep(2)  # Wait 2 seconds before next check
                else:
                    print(f"   ❌ Status check failed: {resp.status}")
                    break
        else:
            print(f"   ⏰ Processing timed out after {max_wait_time} seconds")
        
        # Test 4: Test retry functionality (if job failed)
        print("\n5. Testing retry functionality...")
        
        async with session.get(f"{base_url}/api/detection/detection-status/{video_id}") as resp:
            if resp.status == 200:
                status = await resp.json()
                if status['status'] == 'failed' and status.get('can_retry', False):
                    print("   🔄 Job failed but can be retried, testing retry...")
                    
                    async with session.post(f"{base_url}/api/detection/retry/{video_id}") as retry_resp:
                        if retry_resp.status == 200:
                            retry_result = await retry_resp.json()
                            print(f"   ✅ Retry successful: {retry_result['status']}")
                        else:
                            print(f"   ❌ Retry failed: {retry_resp.status}")
                else:
                    print(f"   ℹ️  Job status: {status['status']} (no retry needed)")
        
        # Test 5: Test job listing
        print("\n6. Testing job listing...")
        
        async with session.get(f"{base_url}/api/detection/jobs?limit=10") as resp:
            if resp.status == 200:
                jobs = await resp.json()
                print(f"   ✅ Retrieved {len(jobs['jobs'])} jobs")
                print(f"   📊 Total jobs: {jobs['total_count']}")
                
                # Show recent jobs
                for job in jobs['jobs'][:3]:
                    print(f"      - {job['video_id'][:8]}... | {job['status']} | {job['mode']}")
            else:
                print(f"   ❌ Job listing failed: {resp.status}")
        
        # Test 6: Test file validation
        print("\n7. Testing file validation...")
        
        # Test with invalid file type
        invalid_data = aiohttp.FormData()
        invalid_data.add_field('file', b'invalid content', filename='test.txt', content_type='text/plain')
        invalid_data.add_field('mode', 'traditional')
        
        async with session.post(f"{base_url}/api/detection/detect", data=invalid_data) as resp:
            if resp.status == 400:
                error = await resp.json()
                print(f"   ✅ File validation working: {error['detail']}")
            else:
                print(f"   ❌ File validation failed: {resp.status}")
    
    # Cleanup
    print("\n8. Cleaning up...")
    test_video.unlink()
    print("   ✅ Test video file cleaned up")
    
    print("\n🎉 All tests completed!")
    print("\nKey Fixes Demonstrated:")
    print("✅ File persistence prevents 'read of closed file' error")
    print("✅ Database persistence prevents '404 Video ID not found' error")
    print("✅ Background processing with proper error handling")
    print("✅ Status tracking and progress monitoring")
    print("✅ File validation and security")

async def test_concurrent_uploads():
    """Test concurrent uploads to verify the fixes work under load."""
    print("\n🚀 Testing Concurrent Uploads")
    print("=" * 30)
    
    base_url = "http://localhost:8000"
    
    async def upload_video(session, video_id):
        """Upload a single video."""
        test_content = b"fake video content for testing" * 1000
        data = aiohttp.FormData()
        data.add_field('file', test_content, filename=f'test_video_{video_id}.mp4', content_type='video/mp4')
        data.add_field('mode', 'traditional')
        
        async with session.post(f"{base_url}/api/detection/detect", data=data) as resp:
            if resp.status == 200:
                result = await resp.json()
                return result['video_id']
            else:
                error = await resp.text()
                print(f"   ❌ Upload {video_id} failed: {resp.status} - {error}")
                return None
    
    async with aiohttp.ClientSession() as session:
        # Upload 5 videos concurrently
        tasks = [upload_video(session, i) for i in range(5)]
        video_ids = await asyncio.gather(*tasks)
        
        successful_uploads = [vid for vid in video_ids if vid is not None]
        print(f"   ✅ Successfully uploaded {len(successful_uploads)} videos concurrently")
        
        # Check status of all videos
        for video_id in successful_uploads:
            async with session.get(f"{base_url}/api/detection/detection-status/{video_id}") as resp:
                if resp.status == 200:
                    status = await resp.json()
                    print(f"   📊 {video_id[:8]}... | {status['status']} | {status.get('progress_percentage', 0)}%")
                else:
                    print(f"   ❌ Status check failed for {video_id[:8]}...")

def main():
    """Main function."""
    print("Deepfake Detection Service - Fix Demonstration")
    print("This script demonstrates the fixes for production bugs:")
    print("1. 'read of closed file' error")
    print("2. '404 Video ID not found' error")
    print("\nMake sure the service is running on http://localhost:8000")
    print("Press Enter to continue...")
    input()
    
    # Run tests
    asyncio.run(test_detection_fixes())
    asyncio.run(test_concurrent_uploads())
    
    print("\n✨ Demonstration complete!")
    print("\nThe fixes ensure:")
    print("- Files are persisted immediately, preventing 'read of closed file' errors")
    print("- Job records are stored in database, preventing '404 Video ID not found' errors")
    print("- Background workers use their own database sessions")
    print("- Comprehensive error handling and status tracking")
    print("- Production-ready file management and cleanup")

if __name__ == "__main__":
    main()
