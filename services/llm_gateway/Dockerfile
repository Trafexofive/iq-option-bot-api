FROM python:3.11

# Set the working directory
WORKDIR /app

# Add the application directory to the Python path
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

USER app

# Expose the port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "api_gateway:app", "--host", "0.0.0.0", "--port", "8001"]
