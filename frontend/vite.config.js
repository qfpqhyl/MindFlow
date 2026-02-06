import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  optimizeDeps: {
    include: ['date-fns'],
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'date-fns': ['date-fns'],
        },
      },
    },
  },
})
