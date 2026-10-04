import { api, cachedGet, invalidateCache } from ".";
import type { Setting } from "./types";

export default class SettingsApi {


    async list(): Promise<Setting[]> {
        const result = await api.get('/settings/s/');
        return result.data;
    }

    async get(key: string): Promise<Setting> {
        return await cachedGet(`/settings/s/${key}`);
    }

    async update(key: string, value: string): Promise<Setting> {
        const result = await api.patch(`/settings/s/${key}`, value);
        invalidateCache();
        return result.data;
    }

    async cleanupDb(): Promise<{
        message: string; deleted_tokens: number; deleted_password_resets: number
        deleted_reminders: number;
        deleted_notifications: number;
        deleted_notifications_admin: number;
    }> {
        const result = await api.post('/settings/cleanup_db');
        return result.data;
    }

}

