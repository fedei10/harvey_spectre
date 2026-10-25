import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1"],
  turbopack: {
    resolveAlias: {
      clsx: "cn",
      "tailwind-merge": "cn",
    },
  },
}

export default nextConfig
