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
  }
})
