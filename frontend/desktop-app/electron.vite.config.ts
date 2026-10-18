import { resolve } from 'node:path';

import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'electron-vite';

export default defineConfig({
  main: {},
  preload: {
    build: {
      // Sandboxed preloads cannot require chunks: the entries share
      // only types, so each one builds into a single file.
      rollupOptions: {
        input: {
          pet: resolve(__dirname, 'src/preload/pet.ts'),
          login: resolve(__dirname, 'src/preload/login.ts'),
          interval: resolve(
            __dirname,
            'src/preload/interval.ts',
          ),
        },
      },
    },
  },
  renderer: {
    plugins: [react(), tailwindcss()],
    build: {
      rollupOptions: {
        input: {
          pet: resolve(__dirname, 'src/renderer/pet.html'),
          login: resolve(
            __dirname,
            'src/renderer/login.html',
          ),
          interval: resolve(
            __dirname,
            'src/renderer/interval.html',
          ),
        },
      },
    },
  },
});
