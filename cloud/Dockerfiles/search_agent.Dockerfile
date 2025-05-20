# Use Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy code
COPY agents/search_agent/ /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port Cloud Run expects
EXPOSE 8080

# Start the app
CMD ["python3", "main.py"]