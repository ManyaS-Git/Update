/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    if (process.env.ENABLE_BACKEND_REWRITE === "true") {
      const raw = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001";
      const backend = raw.replace(/\/+$/, "");
      return [
        { source: "/api/:path*", destination: `${backend}/api/:path*` },
        { source: "/health", destination: `${backend}/health` },
      ];
    }
    return [];
  },
};

export default nextConfig;
