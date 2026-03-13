/** @type {import('next').NextConfig} */
const nextConfig = {
  /**
   * Proxy /api/* → FastAPI backend in development.
   * This eliminates cross-origin issues during local dev.
   * In production, point NEXT_PUBLIC_API_BASE_URL at the real backend host.
   */
  async rewrites() {
    const backendUrl =
      process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
      "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
