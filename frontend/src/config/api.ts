const DEFAULT_API = "http://127.0.0.1:8000";

const apiFromEnv = import.meta.env.VITE_API_URL as string | undefined;
const wsFromEnv = import.meta.env.VITE_WS_URL as string | undefined;

export const API_CONFIG = {
  BASE_URL: apiFromEnv || DEFAULT_API,
  WS_URL: wsFromEnv || (apiFromEnv
    ? apiFromEnv.replace(/^http/, "ws") + "/ws/admin"
    : "ws://127.0.0.1:8000/ws/admin"),
  HEALTH_ENDPOINT: "/health",
};

export const getApiUrl = (): string => API_CONFIG.BASE_URL;
export const getWebSocketUrl = (): string => API_CONFIG.WS_URL;

export const API_BASE_URL = getApiUrl();
export const WS_URL = getWebSocketUrl();
