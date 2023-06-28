# Use the official Python base image
FROM python:3.10.6-slim

# Add user
RUN useradd -ms /bin/bash tuesearch

# Set the working directory in the container
WORKDIR /app

# Change ownership of the /app directory to the tuesearch user
RUN chown -R tuesearch:tuesearch /app

# Switch user
USER tuesearch

RUN mkdir -p /app/opt/tuesearch/log /app/opt/tuesearch/data

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the project dependencies
RUN python3 -m pip install -r requirements.txt

# Expose the port on which your Flask app will run
EXPOSE 5000