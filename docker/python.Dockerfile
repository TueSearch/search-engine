# Use the official Python base image
FROM python:3.10.6-slim

# Add user
RUN useradd -ms /bin/bash tuesearch

# Switch user
USER tuesearch

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.prod.txt .

# Install the project dependencies
RUN python3 -m pip install -r requirements.prod.txt

# Download data for nltk
RUN python3 -c "import nltk; nltk.download('stopwords')"

# Expose the port on which your Flask app will run
EXPOSE 5000