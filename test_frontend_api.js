const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";
console.log("API_URL:", API_URL);

async function testRecoveryPlanAPI() {
    try {
        const response = await fetch(`${API_URL}/api/v1/recovery-plan/generate`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ prediction_id: "test123" }),
        });
        
        console.log("Response status:", response.status);
        console.log("Response headers:", Object.fromEntries(response.headers.entries()));
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error("Error response:", errorText);
            return null;
        }
        
        const data = await response.json();
        console.log("Success response:", data);
        return data;
    } catch (error) {
        console.error("Network error:", error);
        return null;
    }
}

testRecoveryPlanAPI();
