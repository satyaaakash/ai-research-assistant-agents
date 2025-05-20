# cloud/Dockerfiles/query_agent.Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy query agent code
COPY agents/query_agent/ /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port and start app
EXPOSE 8080
CMD ["python3", "main.py"]