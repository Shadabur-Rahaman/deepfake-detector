const TOKEN_KEY = "ifake_access_token";
const REFRESH_KEY = "ifake_refresh_token";
const USER_KEY = "ifake_current_user";

function apiBase() {
  return import.meta.env.VITE_API_URL ?? "";
}

class AuthService {
  constructor() {
    this.currentUser = this.getCurrentUser();
  }

  getCurrentUser() {
    try {
      const raw = localStorage.getItem(USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  setSession({ user, access_token, refresh_token }) {
    if (access_token) localStorage.setItem(TOKEN_KEY, access_token);
    if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token);
    if (user) {
      const normalized = {
        id: user.id,
        email: user.email,
        username: user.username,
        fullName: user.full_name || user.fullName,
        full_name: user.full_name || user.fullName,
        roles: user.roles || ["user"],
        permissions: user.permissions || [],
      };
      localStorage.setItem(USER_KEY, JSON.stringify(normalized));
      this.currentUser = normalized;
    }
  }

  clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
    this.currentUser = null;
  }

  accessToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  authHeaders() {
    const token = this.accessToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async request(path, options = {}) {
    const headers = {
      "Content-Type": "application/json",
      ...this.authHeaders(),
      ...(options.headers || {}),
    };
    const paths =
      path.startsWith("/v1/auth")
        ? [path, path.replace("/v1/auth", "/api/auth")]
        : path.startsWith("/api/auth")
          ? [path, path.replace("/api/auth", "/v1/auth")]
          : [path];
    let lastErr = null;
    for (const p of paths) {
      const res = await fetch(`${apiBase()}${p}`, { ...options, headers });
      let data = null;
      try {
        data = await res.json();
      } catch {
        data = {};
      }
      if (res.status === 404 && paths.length > 1 && p !== paths[paths.length - 1]) {
        continue;
      }
      if (!res.ok) {
        const detail = data.detail;
        const message =
          typeof detail === "string"
            ? detail
            : Array.isArray(detail)
              ? detail.map((d) => d.msg || d).join(", ")
              : data.message || `Request failed (${res.status})`;
        lastErr = new Error(message);
        lastErr.status = res.status;
        if (res.status === 404 && p !== paths[paths.length - 1]) continue;
        throw lastErr;
      }
      return data;
    }
    throw lastErr || new Error("Request failed");
  }

  isAuthenticated() {
    return Boolean(this.accessToken() && this.currentUser);
  }

  getCurrentUserInfo() {
    return this.currentUser;
  }

  async authPolicy() {
    try {
      return await this.request("/v1/auth/policy");
    } catch {
      return {
        min_length: 12,
        max_length: 72,
        email_ready: false,
        sms_ready: false,
      };
    }
  }

  async register(userData) {
    const data = await this.request("/v1/auth/register", {
      method: "POST",
      body: JSON.stringify({
        email: userData.email,
        password: userData.password,
        full_name: userData.fullName || userData.full_name,
        username: userData.username,
        phone: userData.phone || null,
      }),
    });
    if (data.needs_verification && data.signup_id) {
      return { success: true, needs_verification: true, ...data };
    }
    if (data.access_token) {
      throw new Error(
        "The API still created the account without email verification. Stop the process on port 8000 and start a new uvicorn so the Gmail OTP routes load."
      );
    }
    throw new Error(data.detail || data.message || "Registration did not start email verification.");
  }

  async verifyRegister({ signup_id, email_code, sms_code }) {
    const data = await this.request("/v1/auth/register/verify", {
      method: "POST",
      body: JSON.stringify({ signup_id, email_code, sms_code: sms_code || null }),
    });
    this.setSession(data);
    return { success: true, user: this.currentUser, message: "Email verified" };
  }

  async resendOtp({ signup_id, channel }) {
    return this.request("/v1/auth/register/resend", {
      method: "POST",
      body: JSON.stringify({ signup_id, channel }),
    });
  }

  async login(email, password, phone) {
    const data = await this.request("/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: email || null, phone: phone || null, password }),
    });
    if (data.needs_verification && (data.challenge_id || data.signup_id)) {
      return { success: true, needs_verification: true, ...data };
    }
    if (data.access_token) {
      throw new Error(
        "The API signed you in without a Gmail code. Restart uvicorn so login verification loads."
      );
    }
    throw new Error(data.detail || data.message || "Sign-in did not start email verification.");
  }

  async verifyLogin({ challenge_id, signup_id, email_code, sms_code }) {
    const data = await this.request("/v1/auth/login/verify", {
      method: "POST",
      body: JSON.stringify({
        challenge_id: challenge_id || signup_id,
        signup_id: signup_id || challenge_id,
        email_code,
        sms_code: sms_code || null,
      }),
    });
    this.setSession(data);
    return { success: true, user: this.currentUser, message: "Signed in" };
  }

  async resendLoginOtp({ challenge_id, signup_id, channel }) {
    return this.request("/v1/auth/login/resend", {
      method: "POST",
      body: JSON.stringify({
        challenge_id: challenge_id || signup_id,
        signup_id: signup_id || challenge_id,
        channel,
      }),
    });
  }

  async forgotPassword(email) {
    return this.request("/v1/auth/password/forgot", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
  }

  async resetPassword({ reset_id, code, new_password }) {
    return this.request("/v1/auth/password/reset", {
      method: "POST",
      body: JSON.stringify({ reset_id, code, new_password }),
    });
  }

  async refresh() {
    const refresh_token = localStorage.getItem(REFRESH_KEY);
    if (!refresh_token) throw new Error("No refresh token");
    const data = await this.request("/v1/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token }),
    });
    this.setSession(data);
    return data;
  }

  async restore() {
    if (!this.accessToken()) {
      this.clearSession();
      return null;
    }
    try {
      const user = await this.request("/v1/auth/me");
      this.setSession({ user, access_token: this.accessToken() });
      return this.currentUser;
    } catch (e) {
      if (e.status === 401) {
        try {
          await this.refresh();
          return this.currentUser;
        } catch {
          this.clearSession();
          return null;
        }
      }
      return this.currentUser;
    }
  }

  async logout() {
    const refresh_token = localStorage.getItem(REFRESH_KEY);
    try {
      await this.request("/v1/auth/logout", {
        method: "POST",
        body: JSON.stringify({ refresh_token }),
      });
    } catch {
      /* still clear locally */
    }
    this.clearSession();
    return { success: true, message: "Signed out" };
  }

  async createApiKey(name = "default") {
    return this.request("/v1/auth/api-keys", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
  }

  async listApiKeys() {
    return this.request("/v1/auth/api-keys");
  }

  async deleteApiKey(id) {
    return this.request(`/v1/auth/api-keys/${id}`, { method: "DELETE" });
  }

  async updateProfile() {
    return { success: false, message: "Use the account page after re-login" };
  }

  async changePassword() {
    return { success: false, message: "Password change is not enabled yet" };
  }
}

const authService = new AuthService();
export default authService;
