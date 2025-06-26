FROM python:3.11-slim



WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    django==4.2.7 \
    djangorestframework==3.14.0 \
    channels==4.0.0 \
    channels-redis==4.1.0 \
    redis==4.6.0 \
    django-redis==5.3.0 \
    daphne 

COPY . .

EXPOSE 8000

CMD ["/bin/bash", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]