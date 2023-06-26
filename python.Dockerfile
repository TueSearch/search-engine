# Use the official Python base image
FROM python:3.11.4-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.prod.txt .

# Install the project dependencies
RUN python3 -m pip install -r requirements.prod.txt

# Expose the port on which your Flask app will run
EXPOSE 5000