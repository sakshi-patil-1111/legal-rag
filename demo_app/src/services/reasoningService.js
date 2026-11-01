import api from './api';

import { detectQueryLang } from '../utils/detectQueryLang';

export const generateReasoning = async (token, userFacts, conversationId = null, signal, language = 'en') => {
  try {
    const payload = {
      user_facts: userFacts,
      tenant_id: "global",
      language,
      detected_lang: detectQueryLang(userFacts)
    };
    if (conversationId) {
      payload.conversation_id = conversationId;
    }
    const response = await api.post('/reasoning/generate', payload, {
      headers: {
        Authorization: `Bearer ${token}`
      },
      signal
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};
