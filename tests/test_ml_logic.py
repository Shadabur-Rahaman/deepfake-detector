# tests/test_ml_logic.py
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from pathlib import Path
import os
import cv2

# Import the functions to be tested
from app.services.video_processor import extract_faces_from_video
from app.services.deepfake_detector import detect_deepfake_in_frames

# Define paths for test artifacts
TEST_VIDEO_PATH = Path(__file__).parent.parent / "data" / "sample_video.mp4"
HAARCASCADE_XML_PATH = Path(__file__).parent.parent / "ml_artifacts" / "haarcascade_frontalface_default.xml"

# Ensure test prerequisites exist
if not TEST_VIDEO_PATH.exists():
    pytest.skip(f"Skipping ML logic tests: {TEST_VIDEO_PATH} not found.", allow_module_level=True)
if not HAARCASCADE_XML_PATH.exists():
    pytest.skip(f"Skipping ML logic tests: {HAARCASCADE_XML_PATH} not found.", allow_module_level=True)


def create_dummy_image(width=100, height=100, channels=3):
    """Creates a dummy black image for testing."""
    return np.zeros((height, width, channels), dtype=np.uint8)

def create_dummy_video(path, frames=5, fps=10, width=640, height=480):
    """Creates a dummy video file for testing."""
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec for .mp4
    out = cv2.VideoWriter(str(path), fourcc, fps, (width, height))
    if not out.isOpened():
        raise IOError(f"Could not open video writer for {path}")
    for _ in range(frames):
        img = create_dummy_image(width, height)
        out.write(img)
    out.release()
    print(f"Created dummy video: {path}")


# --- Tests for video_processor.py ---

@pytest.fixture(scope="module")
def sample_video_fixture():
    """Fixture to ensure a sample video exists for testing."""
    if not TEST_VIDEO_PATH.exists():
        # Fallback to creating a dummy video if sample_video.mp4 is missing
        print(f"Warning: {TEST_VIDEO_PATH} not found. Creating a dummy video for tests.")
        create_dummy_video(TEST_VIDEO_PATH)
    return str(TEST_VIDEO_PATH)


@pytest.mark.skipif(not TEST_VIDEO_PATH.exists(), reason="Requires sample_video.mp4 in data/ for video processing tests")
@pytest.mark.skipif(not HAARCASCADE_XML_PATH.exists(), reason="Requires haarcascade_frontalface_default.xml in ml_artifacts/ for video processing tests")
def test_extract_faces_from_video_basic(sample_video_fixture):
    """Test if faces can be extracted from a video."""
    faces = extract_faces_from_video(sample_video_fixture, frames_to_process=1)
    assert isinstance(faces, list)
    # Haar Cascade might not detect faces in a random video, so check if list is not empty,
    # or ensure you use a video with guaranteed faces for robust testing.
    # For a real video with faces, you'd expect len(faces) > 0
    # For now, we'll just check if it ran without error and returned a list.
    assert all(isinstance(face, np.ndarray) for face in faces)
    if faces:
        assert faces[0].shape == (224, 224, 3) # Check target size and channels
        assert faces[0].dtype == np.float32 # Check normalization type

def test_extract_faces_from_video_no_file():
    """Test error handling for non-existent video file."""
    with pytest.raises(FileNotFoundError):
        extract_faces_from_video("non_existent_video.mp4")

# --- Tests for deepfake_detector.py (Mock) ---

@pytest.mark.asyncio
async def test_detect_deepfake_in_frames_no_faces():
    """Test mock detection with no faces."""
    result, confidence = await detect_deepfake_in_frames([])
    assert result == "No Faces Detected"
    assert confidence == 0.0

@pytest.mark.asyncio
async def test_detect_deepfake_in_frames_mock_logic():
    """Test mock detection with some faces, checking output format."""
    dummy_faces = [create_dummy_image() for _ in range(5)] # 5 dummy faces
    result, confidence = await detect_deepfake_in_frames(dummy_faces)
    
    assert result in ["Deepfake Detected", "Real Video"]
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0

# You could add more specific tests here if your mock logic had more branches
# For example, testing scenarios that are more likely to yield "Deepfake Detected"
# or "Real Video" if your mock logic was more deterministic.