import { api } from ".";
import type { Document } from "./types";

export default class DocumentApi {
    async list(): Promise<Document[]> {
        const result = await api.get('/documents/list');
        return result.data;
    }

    async upload(file: File): Promise<Document> {
        const form = new FormData();
        form.append('file', file);
        const result = await api.post('/documents/upload', form);
        return result.data;
    }

    async delete(id: number): Promise<void> {
        await api.delete(`/documents/${id}/delete`);
    }
}
