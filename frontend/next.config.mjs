/** @type {import('next').NextConfig} */
const nextConfig = {
  // Output standalone for Docker deployment
  output: "standalone",
  
  // Enable React strict mode
  reactStrictMode: true,
  
  // Image optimization settings
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
      {
        protocol: "http",
        hostname: "**",
      },
    ],
  },
  
  // Environment variables available on client
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:3005",
  },

  // Proxy image/file requests to backend so Next.js Image optimizer
  // can reach the backend from inside the Docker network.
  async rewrites() {
    return [
      {
        source: '/api/proxy/v1/:path*',
        destination: `${process.env.INTERNAL_API_URL || 'http://backend:3001'}/api/v1/:path*`,
      },
    ];
  },
  
  // Next.js 14 supports path aliases from tsconfig.json natively
  // No webpack customization needed
};

export default nextConfig;
