import react from '@vitejs/plugin-react-swc';
import { defineConfig } from 'vite';
import tsconfigPaths from 'vite-tsconfig-paths';

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    host: 'localhost',
    port: import.meta.env.VITE_FRONTEND_PORT,
  },
  build: {
    outDir: 'build',
  },

  plugins: [react(), tsconfigPaths()],
});
