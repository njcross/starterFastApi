# dev frontend.Dockerfile
FROM node:22-alpine
WORKDIR /app

# Always install dev deps in this image
ENV NODE_ENV=development

# Install deps
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci || npm install --include=dev

# Do NOT copy the whole src here for dev; we'll mount it at runtime
# Keeps node_modules inside the container for reliability/perf
EXPOSE 5173

# Helpful for file watching on Docker Desktop (macOS/Windows)
ENV CHOKIDAR_USEPOLLING=1
ENV WATCHPACK_POLLING=true

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
