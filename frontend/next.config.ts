import type { NextConfig } from 'next';

const BACKEND_ORIGIN =
  process.env.BACKEND_ORIGIN ?? 'http://localhost:8080';

const nextConfig: NextConfig = {
  /* config options here */
  cacheComponents: true,
  partialPrefetching: true,
  reactCompiler: true,
  // Proxy API calls to the backend so the browser sees same-origin requests:
  // no CORS preflight is involved and the refresh-token cookie just works.
  rewrites: () => [
    {
      source: '/api/v1/:path*',
      destination: `${BACKEND_ORIGIN}/api/v1/:path*`,
    },
  ],
  turbopack: {
    rules: {
      '*.css': {
        loaders: ['@tailwindcss/turbopack'],
        as: '*.css',
      },
    },
  },
};

export default nextConfig;
