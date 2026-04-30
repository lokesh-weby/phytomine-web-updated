FROM python:3.13-slim

# Prevents Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Shows logs directly in terminal
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean

# Copy requirements first for better Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose Django/Gunicorn port
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "project.wsgi:application"]