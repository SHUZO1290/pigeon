import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/auth':       { target: 'http://localhost:8000', changeOrigin: true },
      '/users':      { target: 'http://localhost:8000', changeOrigin: true },
      '/points':     { target: 'http://localhost:8000', changeOrigin: true },
      '/tables':     { target: 'http://localhost:8000', changeOrigin: true },
      '/cash-register': { target: 'http://localhost:8000', changeOrigin: true },
      '/dashboard':  { target: 'http://localhost:8000', changeOrigin: true }
    }
  }
})