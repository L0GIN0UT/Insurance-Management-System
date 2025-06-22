import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from 'path';

export default defineConfig({
  root: "../frontend",
  base: "./",
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "../frontend/src"),
      "@/components": path.resolve(__dirname, "../frontend/src/components"),
      "@/services": path.resolve(__dirname, "../frontend/src/services"),
      "@/hooks": path.resolve(__dirname, "../frontend/src/hooks"),
      "@/pages": path.resolve(__dirname, "../frontend/src/pages"),
      "@/types": path.resolve(__dirname, "../frontend/src/types"),
      "@/utils": path.resolve(__dirname, "../frontend/src/utils")
    }
  },
  build: {
    outDir: "../desktop/dist/renderer",
    emptyOutDir: true
  },
  server: {
    port: 5173
  }
}); 