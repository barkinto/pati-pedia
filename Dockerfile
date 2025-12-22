# Python 3.11 base image with CUDA support
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app_resnet50.py .
COPY app.py .
COPY api.py .
COPY predict_resnet50.py .
COPY ensemble_model.py .
COPY transformer_models.py .
COPY augmentation_utils.py .
COPY cat_breed_info.py .
COPY show_classes.py .
# Copy the trained models (Use HF upload for large files if not in git)
COPY runs ./runs
# COPY runs/resnet50_v2/weights/best.pth runs/resnet50_v2/weights/

# Copy cat breed info database
COPY cat_breed_info.json .

# Copy frontend build
COPY frontend/dist ./frontend/dist

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Run app.py (Flask API + React frontend)
CMD ["python", "app.py"]
