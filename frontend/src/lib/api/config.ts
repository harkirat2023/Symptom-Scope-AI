const DEFAULT_DEV_API_URL = "http://localhost:8080";
const DEFAULT_PROD_API_URL = "https://symptom-scope-ai.onrender.com";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  (process.env.NODE_ENV === "production"
    ? DEFAULT_PROD_API_URL
    : DEFAULT_DEV_API_URL);