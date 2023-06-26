import react from '@vitejs/plugin-react-swc';
import tsconfigPaths from 'vite-tsconfig-paths';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    includeSource: ['src/**/*.test.{ts,tsx}'],
    include: ['src/**/*.test.{ts,tsx}'],
    setupFiles: 'dotenv/config',
    outputFile: 'vitest-results.xml',
    reporters: []
  },
  plugins: [react(), tsconfigPaths()],
});
