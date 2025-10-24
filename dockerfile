# Use small official python image
FROM python:3.11-slim

# Set working dir
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app.py .

ENV PORT=5000

# Expose port
EXPOSE 5000

# Run with gunicorn for production-like
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--workers", "2"]
