import api from './api';

const authService = {
  /**
   * Fetch current user profile from the database using their Firebase ID token.
   * @param {string} token - Firebase ID token
   */
  fetchCurrentUser: async (token) => {
    const response = await api.get('/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  /**
   * Synchronize the user profile with the database using their Firebase ID token.
   * @param {string} token - Firebase ID token
   * @param {string} name - User's display name
   * @param {string} role - Selected role: citizen, student, or lawyer
   */
  syncUserProfile: async (token, name, role) => {
    const response = await api.post(
      '/auth/sync',
      { name, role },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },
};

export default authService;
