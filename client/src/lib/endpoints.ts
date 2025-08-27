// Read base URL from environment (like Vite’s import.meta.env)
export const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Auth endpoints
export const AUTH_ENDPOINTS = {
  OAUTH_URL: (provider: string) => `/auth/authorize/${provider}`,
  EXCHANGE_CODE: "/auth/exchange/",
  LOGOUT: "/auth/logout",
  ME: "/auth/me",
  REFRESH: "/auth/refresh",
};

// Chat endpoints
export const CHAT_ENDPOINTS = {
  NEW_CHAT: `/chat/new`,
  GET_CHAT: (chatId: string) => `/chat/${chatId}`,
  UPLOAD_PDF: (chatId: string) => `/chat/${chatId}/upload`,
  SEND_MESSAGE: (chatId: string) => `/chat/${chatId}/message`,
};
