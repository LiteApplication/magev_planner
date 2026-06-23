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

  async register(email: string, full_name: string, enterprise: string, accepted_terms: boolean): Promise<void> {
    const bodyFormData = new FormData();
    bodyFormData.append('email', email);
    bodyFormData.append('full_name', full_name);
    bodyFormData.append('enterprise', enterprise);
    bodyFormData.append('accepted_terms', accepted_terms ? 'true' : 'false');
    await api.post("/auth/register", bodyFormData);
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