FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app

# Install system build deps (if any Python packages need building)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential \
	&& rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Default port (adjust if your app uses a different one)
EXPOSE 8000

# Default command - try to start a FastAPI/ASGI app at app.main:app using uvicorn.
# If your project uses Flask or a different entrypoint, update this accordingly.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

