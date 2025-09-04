FROM node:alpine

# Install http-server globally
RUN npm install -g http-server

# Set working directory
WORKDIR /app

# Copy UI files
COPY . /app

# Expose port
EXPOSE 8080

# Start http-server
CMD ["http-server", "--cors", "-p", "8080"]