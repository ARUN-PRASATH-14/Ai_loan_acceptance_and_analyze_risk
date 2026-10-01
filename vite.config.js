import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
      },
      '/bank_bg_1.png': 'http://127.0.0.1:5000',
      '/bank_bg_2.png': 'http://127.0.0.1:5000',
      '/bank_emblem.png': 'http://127.0.0.1:5000',
      '/loan_iq_logo.gif': 'http://127.0.0.1:5000',
      '/loan_iq_logo.png': 'http://127.0.0.1:5000',
      '/demo_images': 'http://127.0.0.1:5000',
    }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  }
})
