import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In Docker Compose, the Flask service is named "web" (port 8000).
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      // all /api/* → Flask
      "/api": {
        target: "http://web:8000",
        changeOrigin: true
      }
    }
  }
});
