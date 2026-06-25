import { api } from ".";

export type PlanningRange = "week" | "fortnight" | "all";

export default class ExportApi {
    /** Download the planning workbook (ODS) for the given range and trigger a save. */
    async downloadPlanning(range: PlanningRange): Promise<void> {
        const result = await api.get(`/export/planning/${range}`, { responseType: "blob" });

        const disposition = (result.headers["content-disposition"] as string) || "";
        const match = /filename="?([^";]+)"?/.exec(disposition);
        const filename = match ? match[1] : `planning_${range}.ods`;

        const url = window.URL.createObjectURL(result.data as Blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
    }
}
