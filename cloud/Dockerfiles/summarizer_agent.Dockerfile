# Dockerfile for SummarizerAgent (Gemini 2.5)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y gcc curl gnupg && apt-get clean

# Copy only the SummarizerAgent code
COPY agents/summarizer_agent/ /app/

# Copy shared dependencies
COPY agents/summarizer_agent/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Health check route + port
EXPOSE 8080

CMD ["python", "main.py"]