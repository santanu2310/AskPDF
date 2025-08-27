import { authRequest } from "./api";
import { AUTH_ENDPOINTS } from "./endpoints";

export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
  profile_pic_url?: string;
}

class AuthService {
  // Get OAuth authorization URL and redirect
  async initiateOAuth(provider: "google" | "github") {
    try {
      const response = await authRequest({
        method: "get",
        url: AUTH_ENDPOINTS.OAUTH_URL(provider),
      });
      if (response.status === 200) window.location.href = response.data.url;
    } catch {
      console.error("OAuth initiation failed");
    }
  }

  // Handle OAuth callback (extract code/state)
  async handleCallback(
    provider: "google" | "github"
  ): Promise<AuthUser | null> {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");
    const state = urlParams.get("state");

    if (!code) return null;

    try {
      const data = { code: code, state: state };
      const response = await authRequest({
        method: "post",
        url: AUTH_ENDPOINTS.EXCHANGE_CODE,
        data: data,
      });

      console.log("response:", response);
      if (response.status === 200 || response.status === 201) {
        return response.data;
      }
    } catch (error) {
      console.error("OAuth callback failed:", error);
    }

    return null;
  }

  // Check current auth status
  async getCurrentUser(): Promise<AuthUser | null> {
    try {
      const response = await authRequest({
        method: "get",
        url: AUTH_ENDPOINTS.ME,
      });
      return response.status === 200 ? response.data : null;
    } catch {
      return null;
    }
  }

  // Logout
  async logout(): Promise<void> {
    try {
      await authRequest({
        method: "post",
        url: AUTH_ENDPOINTS.LOGOUT,
      });
    } catch (error) {
      console.error("Logout failed:", error);
    }
  }

  // Refresh token
  async refreshToken(): Promise<boolean> {
    try {
      const response = await authRequest({
        method: "post",
        url: AUTH_ENDPOINTS.REFRESH,
      });
      return response.status === 200;
    } catch {
      return false;
    }
  }
}

export const authService = new AuthService();
