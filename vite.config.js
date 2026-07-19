import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Tauri expects a relative base and a fixed port for dev.
export default defineConfig({
  plugins: [react()],
  base: "./",
  server: {
    port: 1420,
    strictPort: true,
    host: "127.0.0.1",
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
