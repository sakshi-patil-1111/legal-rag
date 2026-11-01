import api from './api';

export const getConversations = async (token, featureType = null, query = null) => {
  try {
    const params = {};
    if (featureType) params.feature_type = featureType;
    if (query) params.query = query;
    
    const response = await api.get('/chat/conversations', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      params
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching conversations:', error);
    throw error;
  }
};

export const renameConversation = async (token, conversationId, title) => {
  try {
    const response = await api.put(`/chat/conversations/${conversationId}/rename`, 
      { title },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data;
  } catch (error) {
    console.error(`Error renaming conversation ${conversationId}:`, error);
    throw error;
  }
};

export const pinConversation = async (token, conversationId, isPinned) => {
  try {
    const response = await api.put(`/chat/conversations/${conversationId}/pin`, 
      { is_pinned: isPinned },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data;
  } catch (error) {
    console.error(`Error pinning conversation ${conversationId}:`, error);
    throw error;
  }
};

export const getMessages = async (token, conversationId) => {
  try {
    const response = await api.get(`/chat/conversations/${conversationId}/messages`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching messages for conversation ${conversationId}:`, error);
    throw error;
  }
};

export const deleteConversation = async (token, conversationId) => {
  try {
    const response = await api.delete(`/chat/conversations/${conversationId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error(`Error deleting conversation ${conversationId}:`, error);
    throw error;
  }
};
