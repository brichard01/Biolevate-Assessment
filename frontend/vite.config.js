import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Read the .env at the root of the project (shared with the backend and docker compose).
  // The '' prefix also loads variables without VITE_, like FRONTEND_PORT, for this file only.
  const env = loadEnv(mode, '..', '')

  return {
    plugins: [react()],
    envDir: '..',
    server: {
      port: Number(env.FRONTEND_PORT ?? 5173),
      // Fail instead of switching to another port: the backend only allows this one (CORS).
      strictPort: true,
    },
  }
})
