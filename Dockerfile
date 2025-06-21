# deepfake-detector/Dockerfile

# Use a lightweight Python base image
FROM python:3.9-slim-buster

# ✅ Install system-level dependencies for OpenCV
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Ensure the upload folder exists
ENV UPLOAD_DIR="uploaded_videos"
RUN mkdir -p ${UPLOAD_DIR}

# Expose the port for FastAPI
EXPOSE 8000

# Start the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
