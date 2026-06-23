import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// When the dev server runs behind a reverse proxy (nginx) on a different
// port, the HMR websocket client must target the proxy's port. Set via
// HMR_CLIENT_PORT in the container; unset for plain `npm run dev`.
const hmrClientPort = process.env.HMR_CLIENT_PORT
  ? Number(process.env.HMR_CLIENT_PORT)
  : undefined

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
  server: {
    host: true,
    ...(hmrClientPort ? { hmr: { clientPort: hmrClientPort } } : {}),
  },
  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler'
      }
    }
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
