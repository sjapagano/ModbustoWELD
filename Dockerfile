FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py .
COPY config.yaml .

# Expose Modbus TCP port
EXPOSE 5020

# Run the application
CMD ["python", "-u", "main.py"]
