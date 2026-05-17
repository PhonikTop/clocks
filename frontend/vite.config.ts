import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import eslint from 'vite-plugin-eslint'
import path from 'path'

export default defineConfig({
  plugins: [vue(),tailwindcss(),eslint()],
    resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    proxy: {
      '/api/v1': {
        target: 'http://watchy:8000',
        changeOrigin: true,
        secure: false,
      },
      '/ws': {
        target: 'ws://watchy:8000',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
    }
  }
})
