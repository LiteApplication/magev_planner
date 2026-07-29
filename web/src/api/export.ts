import { api } from ".";

export type PlanningRange = "week" | "fortnight" | "all";

export type PlanningExportOptions = {
    start?: string;   // "YYYY-MM-DD" — explicit period start
    end?: string;     // "YYYY-MM-DD" — explicit period end
    group?: string;   // limit to a single group (omit for all groups)
};

export default class ExportApi {
    /** Download the planning workbook (ODS) for the given range and trigger a save. */
    async downloadPlanning(range: PlanningRange, options: PlanningExportOptions = {}): Promise<void> {
        const params: Record<string, string> = {};
        if (options.start) params.start = options.start;
        if (options.end) params.end = options.end;
        if (options.group) params.group = options.group;
        const result = await api.get(`/export/planning/${range}`, { responseType: "blob", params });

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
