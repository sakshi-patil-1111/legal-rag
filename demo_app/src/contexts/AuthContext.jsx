import React, { createContext, useContext } from 'react';

// Demo stub — authentication is intentionally omitted for the dissertation demo.
// Provides the same interface the real NYAAY-AI AuthContext exposed so
// downstream components work unmodified.
const demoUser = {
  uid: 'demo-user',
  displayName: 'Guest',
  email: 'guest@nyaay-ai.demo',
  getIdToken: async () => 'demo-token',
};

const AuthContext = createContext({
  currentUser: demoUser,
  userProfile: { tenant_id: 'demo-tenant', display_name: 'Guest' },
  loading: false,
  signup: async () => demoUser,
  login: async () => demoUser,
  loginWithGoogle: async () => demoUser,
  logout: async () => {},
});

export const AuthProvider = ({ children }) => (
  <AuthContext.Provider
    value={{
      currentUser: demoUser,
      userProfile: { tenant_id: 'demo-tenant', display_name: 'Guest' },
      loading: false,
      signup: async () => demoUser,
      login: async () => demoUser,
      loginWithGoogle: async () => demoUser,
      logout: async () => {},
    }}
  >
    {children}
  </AuthContext.Provider>
);

export const useAuth = () => useContext(AuthContext);
