export async function apiFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Request failed");
        }

        return await response.json();
    } catch (error) {
        console.error(error);
        alert(error.message);
        throw error;
    }
}