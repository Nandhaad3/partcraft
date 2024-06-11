# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /partscraft

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /partscraft/
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

ENV NAME PARTSCRAFT

# Copy project
COPY . /partscraft/


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]