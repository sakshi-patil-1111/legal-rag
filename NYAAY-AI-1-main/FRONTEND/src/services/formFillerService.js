import api from './api';

const authHeaders = (token) => {
    // If we're missing token entirely, provide the fallback mock-token here for dev
    const activeToken = token || localStorage.getItem('token') || 'mock-token';
    return { Authorization: `Bearer ${activeToken}` };
};

export const startFormSession = async (token, formId, language = 'en') => {
    try {
        const response = await api.post('/form-filler/start', {
            form_id: formId,
            language
        }, { headers: authHeaders(token) });
        return response.data;
    } catch (error) {
        throw error;
    }
};

import { detectQueryLang } from '../utils/detectQueryLang';

export const sendFormAnswer = async (token, payload, language = 'en') => {
    try {
        const enrichedPayload = {
            ...payload,
            language,
            detected_lang: payload.user_answer ? detectQueryLang(payload.user_answer) : 'en'
        };
        const response = await api.post('/form-filler/chat', enrichedPayload, { headers: authHeaders(token) });
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getFormTemplate = async (token, formId) => {
    try {
        const response = await api.get(`/form-filler/templates/${formId}`, { headers: authHeaders(token) });
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const downloadPdf = async (token, content) => {
    try {
        const response = await api.post('/form-filler/download/pdf', { content }, {
            headers: authHeaders(token),
            responseType: 'blob'
        });
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const downloadDocx = async (token, content) => {
    try {
        const response = await api.post('/form-filler/download/docx', { content }, {
            headers: authHeaders(token),
            responseType: 'blob'
        });
        return response.data;
    } catch (error) {
        throw error;
    }
};

