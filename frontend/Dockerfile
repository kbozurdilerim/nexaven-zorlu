# React Frontend Dockerfile - Multi-stage build
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY yarn.lock* ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Build argument for backend URL
ARG REACT_APP_BACKEND_URL=https://nexaven.com.tr/zorlu.ecu/api
ARG PUBLIC_URL=/zorlu.ecu

ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
ENV PUBLIC_URL=$PUBLIC_URL

# Build the application
RUN yarn build

# Production stage - Nginx to serve static files
FROM nginx:alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
