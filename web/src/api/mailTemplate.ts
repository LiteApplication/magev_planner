import { api } from ".";
import type { MailTemplate } from "./types";

export default class MailTemplateApi {
    async list(): Promise<MailTemplate[]> {
        const result = await api.get('/mail_templates/list');
        return result.data;
    }

    async get(name: string): Promise<MailTemplate> {
        const result = await api.get(`/mail_templates/${name}`);
        return result.data;
    }

    async update(name: string, content: string, subject: string): Promise<MailTemplate> {
        const result = await api.put(`/mail_templates/${name}`, { content, subject });
        return result.data;
    }

    async reset(name: string): Promise<MailTemplate> {
        const result = await api.post(`/mail_templates/${name}/reset`);
        return result.data;
    }

    async test(name: string): Promise<void> {
        await api.post(`/mail_templates/${name}/test`);
    }
}
