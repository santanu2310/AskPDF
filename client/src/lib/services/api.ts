import axios from 'axios';

// Read base URL from environment (like Vite’s import.meta.env)
export const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Auth endpoints
export const AUTH_ENDPOINTS = {
	OAUTH_URL: (provider: string) => `/auth/authorize/${provider}`,
	EXCHANGE_CODE: (provider: 'google' | 'github'): string => `/auth/exchange/${provider}`,
	LOGOUT: '/auth/logout',
	ME: '/auth/me',
	REFRESH: '/auth/refresh'
};

// Chat endpoints
export const CONVERSATION_ENDPOINTS = {
	UPLOAD_SESSION: '/document/upload',
	FILE_STATUS: (docId: string): string => `/document/status/${docId}`,
	FILE_URL: (docId: string): string => `/document/url/${docId}`,
	NEW_CHAT: '/conversation/new',
	GET_ALL_CHAT: '/conversation/all',
	GET_CHAT: (convId: string) => `/conversation/${convId}`,
	SEND_MESSAGE: '/conversation/message'
};

export const guestRequest = axios.create({
	baseURL: BASE_URL
});

export const authRequest = axios.create({
	baseURL: BASE_URL,
	withCredentials: true
});

authRequest.interceptors.response.use(
	(response) => response,
	async (error) => {
		const originalRequest = error.config;
		console.log('Interceptor error:', error);
		if (error.response?.status === 422 && !originalRequest._retry) {
			originalRequest._retry = true;
			try {
				await axios({
					method: 'post',
					url: BASE_URL + AUTH_ENDPOINTS.REFRESH,
					withCredentials: true
				});

				return authRequest(originalRequest);
			} catch (refreshError) {
				console.error('Token refresh failed:', refreshError);
				return Promise.reject(refreshError);
			}
		}

		return Promise.reject(error);
	}
);
