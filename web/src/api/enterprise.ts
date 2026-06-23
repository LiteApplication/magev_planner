import { api } from ".";
import type { Enterprise, EnterprisePublic } from "./types";

export default class EnterpriseApi {
    // Public list for the registration form (no auth required).
    async listPublic(): Promise<EnterprisePublic[]> {
        const result = await api.get('/enterprises/public');
        return result.data;
    }

    async list(): Promise<Enterprise[]> {
        const result = await api.get('/enterprises/list');
        return result.data;
    }

    async create(data: Omit<Enterprise, 'id'>): Promise<Enterprise> {
        const result = await api.post('/enterprises/create', data);
        return result.data;
    }

    async update(id: number, data: Omit<Enterprise, 'id'>): Promise<Enterprise> {
        const result = await api.put(`/enterprises/${id}/update`, data);
        return result.data;
    }

    async delete(id: number): Promise<void> {
        await api.delete(`/enterprises/${id}/delete`);
    }
}
