// Debug API URL Configuration
// Add this to admin-ui/pages/api-debug.ts to see what API URL the frontend is using

import type { NextApiRequest, NextApiResponse } from "next";

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  res.status(200).json({
    api_url: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    environment: process.env.NODE_ENV,
    deployment_info: {
      frontend_url: "https://nurturing-exploration-production.up.railway.app",
      expected_backend_url: "https://edubot-production-cf26.up.railway.app",
      configured_in_railway: process.env.NEXT_PUBLIC_API_URL ? "YES - Ready for API calls" : "NO - Defaulting to localhost",
    },
  });
}
