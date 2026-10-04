import { api, cachedGet, invalidateCache } from ".";
import { exampleShop, type OpenRange, type Shop, type ShopWithOpenRange } from "./types";

export default class ShopApi {
    async get(id: number): Promise<ShopWithOpenRange> {
        if (id === -1) {
            return exampleShop as ShopWithOpenRange;
        }
        const result = await cachedGet<ShopWithOpenRange>(`/shops/${id}/get`);
        return result;
    }

    async list(): Promise<Shop[]> {
        const result = await cachedGet<Shop[]>("/shops/list");
        return result;
    }

    async create(shop: Shop): Promise<ShopWithOpenRange> {
        const result = await api.post("/shops/create", shop);
        invalidateCache();
        return result.data;
    }

    async update(shop: Shop): Promise<ShopWithOpenRange> {
        const result = await api.put("/shops/update", shop);
        invalidateCache();
        return result.data;
    }

    async delete(id: number): Promise<void> {
        const result = await api.delete(`/shops/${id}/delete`);
        invalidateCache();
        return result.data;
    }

    async addOpenRange(shopId: number, openRange: OpenRange): Promise<ShopWithOpenRange> {
        const result = await api.post(`/timeranges/${shopId}/create`, openRange);
        return result.data;
    }

    async deleteOpenRange(id: number): Promise<ShopWithOpenRange> {
        const result = await api.delete(`/timeranges/${id}/delete`);
        return result.data;
    }

    async updateOpenRange(openRange: OpenRange): Promise<ShopWithOpenRange> {
        const result = await api.put(`/timeranges/${openRange.id}/update`, openRange);
        return result.data;
    }

}