import api from './api';
import { detectQueryLang } from '../utils/detectQueryLang';

const authHeaders = (token) => ({ Authorization: `Bearer ${token}` });

export const generateDraft = async (token, userFacts, providedFields = null, language = 'en') => {
  try {
    const response = await api.post('/drafting/generate', {
      user_facts: userFacts,
      provided_fields: providedFields,
      language,
      detected_lang: detectQueryLang(userFacts)
    }, { headers: authHeaders(token) });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const editDraft = async (token, documentObject, editInstructions, language = 'en') => {
  try {
    const response = await api.post('/drafting/edit', {
      document_object: documentObject,
      edit_instructions: editInstructions,
      language,
      detected_lang: detectQueryLang(editInstructions)
    }, { headers: authHeaders(token) });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const downloadPdf = async (token, documentObject) => {
  try {
    const response = await api.post('/drafting/download/pdf', documentObject, {
      responseType: 'blob',
      headers: authHeaders(token)
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const downloadDocx = async (token, documentObject) => {
  try {
    const response = await api.post('/drafting/download/docx', documentObject, {
      responseType: 'blob',
      headers: authHeaders(token)
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};
