# tests/test_api.py (UPDATED)
import pytest
import httpx
from pathlib import Path
import os
import time

# Get the base URL from an environment variable, default to localhost for local testing
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Path to the sample video for testing
SAMPLE_VIDEO_PATH = Path(__file__).parent.parent / "data" / "sample_video.mp4"

# Ensure the sample video exists
if not SAMPLE_VIDEO_PATH.exists():
    pytest.fail(
        f"Sample video not found at {SAMPLE_VIDEO_PATH}. "
        "Please place a small 'sample_video.mp4' in the 'data/' directory to run API tests."
    )

@pytest.mark.asyncio
async def test_health_check():
    """Test the health check endpoint."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        print(f"\nTesting health check at: {BASE_URL}/health") # Debug print
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "message": "Deepfake Detection API is healthy"}

@pytest.mark.asyncio
async def test_upload_and_get_status():
    """
    Tests video upload and subsequent status retrieval.
    This test runs against a live server, not the FastAPI TestClient,
    which is useful for testing the full network stack and background tasks.
    """
    video_id = None
    # Use a longer timeout for upload, especially on CI/CD
    upload_timeout = httpx.Timeout(30.0, connect=5.0) 
    
    try:
        # 1. Test video upload
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=upload_timeout) as client:
            with open(SAMPLE_VIDEO_PATH, "rb") as f:
                files = {"video_file": (SAMPLE_VIDEO_PATH.name, f, "video/mp4")}
                print(f"Attempting to upload {SAMPLE_VIDEO_PATH.name} to {BASE_URL}/upload-video...")
                response = await client.post("/upload-video", files=files)

            assert response.status_code == 200, f"Upload failed: {response.status_code} - {response.text}"
            upload_response = response.json()
            assert "video_id" in upload_response
            assert upload_response["message"].startswith("Video '")
            assert upload_response["status"] == "received"
            video_id = upload_response["video_id"]
            print(f"Video uploaded, video_id: {video_id}")

        # 2. Test status retrieval
        # Poll the status endpoint until detection is completed or fails
        status_checks = 0
        max_status_checks = 20 # Allow more checks for CI/CD latency
        poll_interval = 3 # Wait 3 seconds before polling again
        while status_checks < max_status_checks:
            async with httpx.AsyncClient(base_url=BASE_URL) as client:
                print(f"Checking status for {video_id} at {BASE_URL}/detection-status/{video_id} (attempt {status_checks+1}/{max_status_checks})...")
                status_response = await client.get(f"/detection-status/{video_id}")
                assert status_response.status_code == 200, f"Status check failed: {status_response.status_code} - {status_response.text}"
                status_data = status_response.json()
                print(f"Current status: {status_data['status']}")

                if status_data["status"] == "completed":
                    assert status_data["result"] in ["Deepfake Detected", "Real Video", "No Faces Detected"]
                    assert isinstance(status_data["confidence"], (float, int)) or status_data["confidence"] is None
                    break
                elif status_data["status"] == "failed":
                    pytest.fail(f"Deepfake detection failed: {status_data.get('error', 'No error message')}")
            
            time.sleep(poll_interval)
            status_checks += 1
        else:
            pytest.fail(f"Deepfake detection for {video_id} did not complete within the expected time ({max_status_checks * poll_interval} seconds). Last status: {status_data.get('status', 'N/A')}")

    finally:
        # Optional: Clean up in case of test failure or if video wasn't deleted by app
        # This part assumes the 'uploaded_videos' directory is relative to the project root
        uploaded_videos_dir = Path(__file__).parent.parent / "uploaded_videos"
        if video_id and uploaded_videos_dir.exists():
            for f in uploaded_videos_dir.iterdir():
                if f.name.startswith(video_id):
                    os.remove(f)
                    print(f"Cleaned up {f.name} from local 'uploaded_videos' directory.")
                    break