import type { NextConfig } from "next";

const nextConfig: any = {
  output: 'standalone',
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;

