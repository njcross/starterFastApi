
FROM node:22-alpine
WORKDIR /app

# Ensure dev deps install during build
ENV NODE_ENV=development

# Install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci || npm install --include=dev

# Copy source
COPY frontend ./

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "--port", "5173"]
