import { detectQueryLang } from '../utils/detectQueryLang';
import api from './api';

export const askCivicStream = async (payload, onMessage, onComplete, onError, language = 'en') => {
    const enrichedPayload = {
        ...payload,
        language,
        detected_lang: payload.question ? detectQueryLang(payload.question) : 'en'
    };
    try {
        let token = localStorage.getItem('token');
        if (!token) {
            console.warn("No token found, falling back to mock-token for development");
            token = "mock-token";
        }

        const baseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';
        const response = await fetch(`${baseUrl}/kanoon/query-stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(enrichedPayload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let done = false;

        let accumulatedText = "";
        let buffer = "";
        
        while (!done) {
            const { value, done: doneReading } = await reader.read();
            done = doneReading;
            
            if (value) {
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Keep the last incomplete line in the buffer
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.substring(6));
                            if (data.type === 'status') {
                                onMessage({ type: 'status', text: data.data });
                            } else if (data.type === 'chunk') {
                                accumulatedText += data.data;
                                onMessage({ type: 'content', text: accumulatedText });
                            } else if (data.type === 'complete') {
                                onComplete({
                                    text: accumulatedText,
                                    citations: data.citations,
                                    metrics: data.metrics
                                });
                            } else if (data.type === 'error') {
                                onError(data.data);
                            } else if (data.type === 'metadata') {
                                onMessage({ type: 'metadata', conversation_id: data.conversation_id });
                            }
                        } catch (e) {
                            console.error("Failed to parse SSE data:", e, "Line:", line);
                        }
                    }
                }
            }
        }
    } catch (err) {
        console.error("Civic stream error:", err);
        onError(err.message || "Connection failed");
    }
};
