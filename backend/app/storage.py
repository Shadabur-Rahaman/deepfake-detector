# # app/storage.py
# import os
# import shutil
# import uuid
# import aiofiles
# from fastapi import UploadFile
# from typing import Optional 

# # Directory to store uploaded videos (relative to project root, or set an absolute path)
# UPLOAD_DIR = "uploaded_videos"
# if not os.path.exists(UPLOAD_DIR):
#     os.makedirs(UPLOAD_DIR)

# async def save_uploaded_video(file: UploadFile) -> str:
#     """
#     Saves an uploaded video file to a temporary location and returns its ID.
#     """
#     # Generate a unique ID for the video
#     video_id = str(uuid.uuid4())
#     # Use the original file extension
#     file_extension = os.path.splitext(file.filename)[1]
#     file_path = os.path.join(UPLOAD_DIR, f"{video_id}{file_extension}")

#     # Asynchronously write the file in chunks
#     async with aiofiles.open(file_path, "wb") as out_file:
#         while content := await file.read(1024 * 1024):  # read in 1MB chunks
#             await out_file.write(content)

#     return video_id, file_path

# def get_video_path(video_id: str) -> Optional[str]:
#     """
#     Retrieves the path of a video given its ID.
#     (In a real app, this would query a database)
#     For this demo, we'll assume a consistent naming convention or a lookup table.
#     """
#     # This is a simplified lookup. In a real application, you'd store video_id
#     # to path mapping in a database. For now, we'll iterate or assume extension.
#     for fname in os.listdir(UPLOAD_DIR):
#         if fname.startswith(video_id):
#             return os.path.join(UPLOAD_DIR, fname)
#     return None

# def delete_video_file(file_path: str):
#     """
#     Deletes a video file from the storage.
#     """
#     if os.path.exists(file_path):
#         os.remove(file_path)
#         print(f"Deleted file: {file_path}")

# app/storage.py
import os
import uuid
import aiofiles
from fastapi import UploadFile

UPLOAD_DIR = "uploaded_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_uploaded_video(video_file: UploadFile):
    """Save uploaded video and return video_id and path"""
    video_id = str(uuid.uuid4())
    filename = f"{video_id}_{video_file.filename}"
    video_path = os.path.join(UPLOAD_DIR, filename)
    
    async with aiofiles.open(video_path, 'wb') as f:
        content = await video_file.read()
        await f.write(content)
    
    return video_id, video_path

def delete_video_file(video_path: str):
    """Delete the video file after processing"""
    try:
        if os.path.exists(video_path):
            os.remove(video_path)
    except Exception as e:
        print(f"Failed to delete {video_path}: {e}")
