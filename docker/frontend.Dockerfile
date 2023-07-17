# Dockerfile for launching the frontend

# Use an official Node runtime as a parent image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV VITE_API_URL=http://tuesearch.philippalber.de:4000/
ENV VITE_FRONTEND_PORT=5000
ENV VITE_APP_VERSION=1.0.0

# Copy the package.json and package lockfile file into the container at /app
COPY frontend/package*.json ./

# Install the project dependencies
RUN npm ci

# Copy the rest of the code into the container at /app
COPY ./frontend ./

# Build the project
RUN npm run build

# Install serve
RUN npm install -g serve

# Expose the port on which your Frontend will run
EXPOSE 5000

