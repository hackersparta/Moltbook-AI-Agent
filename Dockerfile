FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for curl/healthcheck)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure start scripts are executable
RUN chmod +x start.sh start_render.sh

# Expose the dashboard port
EXPOSE 5000

# Volume for persistence (optional, but good practice)
VOLUME /app

# Command to run the application
CMD ["./start.sh"]
