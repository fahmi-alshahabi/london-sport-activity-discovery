import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Builds the OPTIONAL enhancement bundle into the server's static dir.
// The SSR core works with this bundle absent (ADR-0001, no-JS core).
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "../server/static/enhanced",
    emptyOutDir: true,
    rollupOptions: {
      input: "src/enhance.ts",
      output: { entryFileNames: "enhance.js", chunkFileNames: "[name].js", assetFileNames: "[name][extname]" },
    },
  },
});
