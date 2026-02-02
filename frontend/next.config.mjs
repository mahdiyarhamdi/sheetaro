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
        hostname: "localhost",
      },
    ],
  },
  
  // Environment variables available on client
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:3005",
  },
  
  // Next.js 14 supports path aliases from tsconfig.json natively
  // No webpack customization needed
};

export default nextConfig;
