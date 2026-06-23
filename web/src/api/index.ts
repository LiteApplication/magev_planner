import axios from "axios";
import type { AxiosInstance } from "axios";
import type { TokenResponse, User } from "./types";

const CACHE_TIMEOUT = 1000 * 30; // 30 seconds

const api: AxiosInstance = axios.create({
    baseURL: import.meta.env.DEV ? 'http://localhost:8000/api' : '/api',
    headers: {
        "accept": "application/json",
    },
});

api.interceptors.request.use(
    config => {
        if (localStorage.getItem('access_token') !== null && (new Date(localStorage.getItem('expires_at') || '0') > new Date())) {
            config.headers['Authorization'] = `Bearer ${localStorage.getItem('access_token')}`;
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);


function setToken(token: TokenResponse) {
    localStorage.setItem("access_token", token.access_token);
    localStorage.setItem("expires_at", token.expires_at.toString());
}

function forgetToken() {
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('loginChecked');
    localStorage.removeItem("access_token");
    localStorage.removeItem("expires_at");
}


function saveUserToSession(user: User) {
    sessionStorage.setItem('user', JSON.stringify(user));
    sessionStorage.setItem('loginChecked', Date.now().toString());
}

function loadUserFromSession(): User | null {
    if (localStorage.getItem('access_token') === null) {
        return null;
    }
    if (new Date(localStorage.getItem('expires_at') || '0') < new Date()) {
        return null;
    }
    if (Date.now() - parseInt(sessionStorage.getItem('loginChecked') || '0') > CACHE_TIMEOUT) {
        return null;
    }
    const user_data = sessionStorage.getItem('user');
    if (user_data) {
        return JSON.parse(user_data);
    }
    return null;
}

function cachedGet<T>(url: string): Promise<T> {
    const cached = sessionStorage.getItem("cache_data" + url);
    if (cached) {
        const cache_time = parseInt(sessionStorage.getItem("cache_time" + url) || '0');
        if (Date.now() - cache_time < CACHE_TIMEOUT) {
            return Promise.resolve(JSON.parse(cached));
        }
    }
    return api.get(url).then(response => {
        sessionStorage.setItem("cache_time" + url, Date.now().toString());
        sessionStorage.setItem("cache_data" + url, JSON.stringify(response.data));
        return response.data;
    });
}

function invalidateCache() {
    if (!sessionStorage) {
        return;
    }
    sessionStorage.clear();
}

export { api, setToken, forgetToken, saveUserToSession, loadUserFromSession, cachedGet, invalidateCache };