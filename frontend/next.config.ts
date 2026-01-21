import type { NextConfig } from "next";

const nextConfig: NextConfig = {
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
};

export default nextConfig;
