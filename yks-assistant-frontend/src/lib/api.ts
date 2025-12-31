const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function solveQuestion(file: File) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_URL}/solve`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error("Soru çözülemedi.");
    }

    return response.json();
}

export async function measureQuestion(file: File) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_URL}/measure`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error("Ölçüm yapılamadı.");
    }

    return response.json();
}

export async function generateQuestions(topic: string, difficulty: string) {
    const response = await fetch(`${API_URL}/generate`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ topic, difficulty }),
    });

    if (!response.ok) {
        throw new Error("Soru üretilemedi.");
    }

    return response.json();
}

export async function getCoachAdvice(context: any) {
    const response = await fetch(`${API_URL}/coach`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ context }),
    });

    if (!response.ok) {
        throw new Error("Koç tavsiyesi alınamadı.");
    }

    return response.json();
}
export async function sendMessage(message: string, history: any[] = [], context: any = {}) {
    const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message, history, context }),
    });

    if (!response.ok) {
        throw new Error("Mesaj gönderilemedi.");
    }

    const data = await response.json();
    if (data.status === "error") {
        throw new Error(data.message);
    }
    return data.data;
}
