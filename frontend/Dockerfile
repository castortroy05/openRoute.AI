# Use Node 20 as base image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY openroute_ai/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy project files
COPY openroute_ai/ .

# Build the app
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
