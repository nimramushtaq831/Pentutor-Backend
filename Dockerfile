FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python packages
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Use Daphne for ASGI server instead of Django development server
CMD ["/bin/bash", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 videochat.asgi:application"]