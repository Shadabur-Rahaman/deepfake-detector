const DEFAULT_API = "";

const apiFromEnv = import.meta.env.VITE_API_URL as string | undefined;
const wsFromEnv = import.meta.env.VITE_WS_URL as string | undefined;

function _defaultWsBase(): string {
  if (typeof window === "undefined") return "";
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${window.location.host}`;
}

export const API_CONFIG = {
  BASE_URL: apiFromEnv ?? DEFAULT_API,
  WS_URL: wsFromEnv ?? _defaultWsBase(),
  HEALTH_ENDPOINT: "/api/health",
};

export const getApiUrl = (): string => API_CONFIG.BASE_URL;
export const getWebSocketUrl = (): string => API_CONFIG.WS_URL;

export const API_BASE_URL = getApiUrl();
export const WS_URL = getWebSocketUrl();
