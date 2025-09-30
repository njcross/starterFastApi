FROM node:22-alpine
WORKDIR /app

# Always install dev deps in this image
ENV NODE_ENV=development

# Install deps
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci || npm install --include=dev

# Copy only the parts we need at build (so node_modules is baked into image)
COPY frontend ./

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "--port", "5173"]
