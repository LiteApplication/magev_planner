import { api, forgetToken, invalidateCache, setToken } from ".";
import type { User } from "./types";



export default class AuthApi {
  async login(email: string, password: string): Promise<void> {
    const bodyFormData = new FormData();
    bodyFormData.append('username', email);
    bodyFormData.append('password', password);
    const response = await api.post("/auth/login", bodyFormData);
    setToken(response.data);

  }

  async register(email: string, first_name: string, last_name: string, phone: string, enterprise: string, accepted_terms: boolean): Promise<void> {
    const bodyFormData = new FormData();
    bodyFormData.append('email', email);
    bodyFormData.append('first_name', first_name);
    bodyFormData.append('last_name', last_name);
    bodyFormData.append('phone', phone);
    bodyFormData.append('enterprise', enterprise);
    bodyFormData.append('accepted_terms', accepted_terms ? 'true' : 'false');
    await api.post("/auth/register", bodyFormData);
  }

  async forgotPassword(email: string): Promise<void> {
    const bodyFormData = new FormData();
    bodyFormData.append('email', email);
    await api.post("/auth/forgot_password", bodyFormData);
  }

  async me(): Promise<User> {
    return api.get("/auth/me").then(response => response.data);
  }

  async logout(): Promise<void> {
    try {
      await api.post("/auth/logout");
    } catch (e: any) {
      if (e.response?.status !== 401) {
        console.log(e)
      }
    }
    invalidateCache();
    forgetToken();
  }
}