# Use an official Python runtime as a parent image
FROM python:3.13.5-slim

# Set the working directory in the container to a project-specific directory
WORKDIR /usr/src/app

# Copy the entire project into the container
COPY . .

# Expose port 8000 for your FastAPI application
EXPOSE 8000

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]