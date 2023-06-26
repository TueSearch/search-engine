# Dockerfile for starting the express server in a container

# Use the official Node.js 16 image.
FROM node:16-alpine

# Copy local code to the container image.
COPY . . 

# Install production dependencies.
RUN npm ci

# Build the app for production.
RUN npm run build:ci

# Run the web service on container startup.
CMD [ "npm" , "start" ]
