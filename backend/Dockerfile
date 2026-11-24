FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:/app/backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

COPY backend/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir torch==2.15.0+cpu torchvision==0.29.2+cpu \
      --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir ultralytics==8.4.216

COPY backend/ /app/backend/

COPY data/processed/yolo_runs/baseline_v1/weights/best.pt \
     /app/data/processed/yolo_runs/baseline_v1/weights/best.pt

RUN mkdir -p /app/backend/uploads /app/backend/processed

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
