FROM python:3.9.21-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install the Python dependencies without caching pip’s files
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

EXPOSE 8000
# Set the default command to run Uvicorn with auto-reload enabled
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

