import { api } from ".";
import type { User } from "./types";

export default class UsersApi {
    async create(email: string, first_name: string, last_name: string, phone: string, password: string, group: string, admin: boolean): Promise<User> {
        const result = await api.post('/users/create', { email, first_name, last_name, phone, password, group, admin });
        return result.data;
    }

    async list(): Promise<User[]> {
        const result = await api.get('/users/list');
        return result.data;
    }

    async get(id: number): Promise<User> {
        const result = await api.get(`/users/get/${id}`);
        return result.data;
    }

    async delete(id: number): Promise<void> {
        await api.delete(`/users/delete/${id}`);
    }

    async update(user: User): Promise<User> {
        const result = await api.put(`/users/update`, user);
        return result.data;
    }

    async me(): Promise<User> {
        const result = await api.get('/users/me');
        return result.data;
    }

    async updateMe(current_password: string, user_data: User): Promise<User> {
        const result = await api.put('/users/me', { current_password, user_data });
        return result.data;
    }

    async requestPasswordReset(email: string): Promise<void> {
        await api.post('/users/request_password_reset', { email });
    }

    async resetPassword(token: string, password: string): Promise<void> {
        await api.post('/users/reset_password', { token, password });
    }
}

