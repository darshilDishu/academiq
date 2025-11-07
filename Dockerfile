# Use a small Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required by MySQL connector
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc default-libmysqlclient-dev build-essential netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files into the container
COPY . .

# Make the entrypoint script executable
RUN chmod +x ./docker-entrypoint.sh

# Expose port 5000 for Flask
EXPOSE 5000

# Command to run when the container starts
CMD ["./docker-entrypoint.sh"]

