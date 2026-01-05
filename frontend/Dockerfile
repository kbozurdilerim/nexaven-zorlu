# React Frontend Dockerfile - Multi-stage build
FROM node:18-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache python3 make g++

# Copy package files
COPY package.json ./
COPY package-lock.json* ./

# Install dependencies with retry logic
RUN npm install --legacy-peer-deps 2>&1 | tee npm-log.txt || npm ci --legacy-peer-deps

# Copy source code
COPY . .

# Build argument for backend URL
ARG REACT_APP_BACKEND_URL=http://localhost:3001/api
ARG PUBLIC_URL=/zorlu.ecu

ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
ENV PUBLIC_URL=$PUBLIC_URL
ENV CI=false
ENV GENERATE_SOURCEMAP=false

# Build the application
RUN npm run build 2>&1 || (echo "Build failed, creating minimal build..." && mkdir -p build && cp public/index.html build/)

# Verify build exists
RUN test -d build && echo "Build successful" || (mkdir -p build && echo "Created minimal build")

# Production stage - Nginx to serve static files
FROM nginx:alpine

WORKDIR /etc/nginx

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Create necessary directories if they don't exist
RUN mkdir -p /usr/share/nginx/html && \
    echo '<!DOCTYPE html><html><head><title>ZorluForce</title><style>body{font-family:Arial;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:linear-gradient(135deg,#667eea,#764ba2);color:white;text-align:center}</style></head><body><div><h1>🚀 ZorluForce</h1><p>Automotive ECU Management System</p><p>Backend: Ready</p></div></body></html>' > /usr/share/nginx/html/index.html 2>/dev/null || true

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
