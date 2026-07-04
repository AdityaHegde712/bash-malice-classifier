import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    include: ['tests/**/*.test.ts'],
    globals: false,
    environment: 'node',
  },
  resolve: {
    alias: {
      '@malice': path.resolve(__dirname, '..', 'typescript', 'src'),
    },
  },
});
