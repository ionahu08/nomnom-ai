import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [tsconfigPaths(), react()],
  test: {
    environment: 'jsdom',
    alias: {
      'server-only': '/Users/ionahu/sources/NomNom/learning_lab/phase_1/11a_Claude_Code_lab_uigen/__mocks__/server-only.js',
    },
  },
})