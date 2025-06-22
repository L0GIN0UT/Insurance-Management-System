# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy workspace root files
COPY package*.json ./

# Copy frontend package.json (только этот файл существует)
COPY frontend/package.json ./frontend/

# Install all workspace dependencies
RUN npm install

# Copy frontend source code
COPY frontend/ ./frontend/

# Build the frontend
WORKDIR /app/frontend
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy build output to nginx
COPY --from=builder /app/frontend/dist /usr/share/nginx/html

# Copy nginx configuration
COPY web/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 (standard nginx port)
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 