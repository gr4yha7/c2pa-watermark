
# Use an official Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy your FastAPI app
COPY . .

# Run the app with Uvicorn
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]