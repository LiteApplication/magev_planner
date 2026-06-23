
function handleError(toast: any, translator: any, unknown: string = "error.unknown", infos: object = {}) {
    return ((error: any) => {
        error.stack = undefined;
        let toast_data = { severity: 'error', summary: translator('error.title'), detail: translator(unknown), life: 10000 };
        if (error.response !== undefined) {
            if (error.response?.status === 500) {
                toast_data = { severity: 'error', summary: translator('error.title'), detail: translator("error.server"), life: 5000 };
                console.error(error);
            }
            else if (error.response?.status === 401) {
                if (error.response.data.detail === "Not authenticated")
                    toast_data = { severity: 'info', summary: translator('message.info'), detail: translator("error.token.not_authenticated"), life: 30000 }; // 30 seconds
                else
                    toast_data = { severity: 'info', summary: translator('message.info'), detail: translator(error.response.data.detail, infos), life: 5000 };
            } else if (error.response?.data) {
                // Check if detail is a string
                if (typeof error.response.data.detail === 'string') {
                    toast_data = { severity: 'error', summary: translator('error.title'), detail: translator(error.response.data.detail, infos), life: 10000 };
                } else {
                    console.error(error.response.data);
                }
            } else {
                console.error(error);
            }
        } else {
            console.error(error);
        }
        toast.add(toast_data);
    });

}

export default handleError;