import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  signOut, 
  signInWithPopup, 
  GoogleAuthProvider,
  updateProfile,
  onAuthStateChanged 
} from 'firebase/auth';
import { auth } from '../config/firebase';
import authService from '../services/authService';
import { formatAuthError } from '../utils/authErrors';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fallback simulator state if Firebase auth is null
  const [mockUser, setMockUser] = useState(() => {
    try {
      const saved = localStorage.getItem('nyaay_mock_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  // Load profile from backend when user is available
  const fetchProfile = async (fbUser) => {
    try {
      const token = fbUser.uid === 'mock-uid' ? 'mock-token' : await fbUser.getIdToken();
      const profile = await authService.fetchCurrentUser(token);
      setUserProfile(profile);
      setError(null);
    } catch (err) {
      if (err.response && err.response.status === 404) {
        try {
          const token = fbUser.uid === 'mock-uid' ? 'mock-token' : await fbUser.getIdToken();
          const profile = await authService.syncUserProfile(token, fbUser.displayName || fbUser.email, 'citizen');
          setUserProfile(profile);
          setError(null);
        } catch (syncErr) {
          console.error("Failed to auto-sync profile", syncErr);
        }
      } else {
        console.error('Error fetching backend user profile:', err);
        // Fallback default profile if backend DB isn't initialized
        setUserProfile({
          name: fbUser.displayName || fbUser.email?.split('@')[0] || 'Counselor',
          email: fbUser.email,
          role: 'CITIZEN',
          created_at: new Date().toISOString()
        });
      }
    }
  };

  useEffect(() => {
    if (auth) {
      const unsubscribe = onAuthStateChanged(auth, async (user) => {
        setCurrentUser(user);
        if (user) {
          await fetchProfile(user);
        } else {
          setUserProfile(null);
        }
        setLoading(false);
      });
      return unsubscribe;
    } else {
      // Dev simulator mode
      if (mockUser) {
        const fullMockUser = {
          ...mockUser,
          getIdToken: async () => 'mock-token'
        };
        setCurrentUser(fullMockUser);
        fetchProfile(fullMockUser).finally(() => setLoading(false));
      } else {
        setCurrentUser(null);
        setUserProfile(null);
        setLoading(false);
      }
    }
  }, [mockUser]);

  // Auth Operations
  const signup = async (email, password, name) => {
    setError(null);
    setLoading(true);
    if (auth) {
      try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        await updateProfile(userCredential.user, { displayName: name });
        return userCredential.user;
      } catch (err) {
        const formattedErr = formatAuthError(err);
        setError(formattedErr);
        setLoading(false);
        throw new Error(formattedErr);
      }
    } else {
      // Mock signup mode
      const newUser = { uid: 'mock-uid', email, displayName: name, getIdToken: async () => 'mock-token' };
      localStorage.setItem('nyaay_mock_user', JSON.stringify({ uid: 'mock-uid', email, displayName: name }));
      setMockUser(newUser);
      setCurrentUser(newUser);
      setLoading(false);
      return newUser;
    }
  };

  const login = async (email, password) => {
    setError(null);
    setLoading(true);
    if (auth) {
      try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        return userCredential.user;
      } catch (err) {
        const formattedErr = formatAuthError(err);
        setError(formattedErr);
        setLoading(false);
        throw new Error(formattedErr);
      }
    } else {
      // Mock login mode
      const displayName = email.split('@')[0];
      const loggedUser = { uid: 'mock-uid', email, displayName, getIdToken: async () => 'mock-token' };
      localStorage.setItem('nyaay_mock_user', JSON.stringify({ uid: 'mock-uid', email, displayName }));
      setMockUser(loggedUser);
      setCurrentUser(loggedUser);
      setLoading(false);
      return loggedUser;
    }
  };

  const logout = async () => {
    setError(null);
    setLoading(true);
    if (auth) {
      try {
        await signOut(auth);
        setCurrentUser(null);
        setUserProfile(null);
      } catch (err) {
        setError(formatAuthError(err));
      } finally {
        setLoading(false);
      }
    } else {
      localStorage.removeItem('nyaay_mock_user');
      setMockUser(null);
      setCurrentUser(null);
      setUserProfile(null);
      setLoading(false);
    }
  };

  const signInWithGoogle = async () => {
    setError(null);
    setLoading(true);
    if (auth) {
      try {
        const provider = new GoogleAuthProvider();
        provider.setCustomParameters({ prompt: 'select_account' });
        const result = await signInWithPopup(auth, provider);
        return result.user;
      } catch (err) {
        const formattedErr = formatAuthError(err);
        setError(formattedErr);
        setLoading(false);
        throw new Error(formattedErr);
      }
    } else {
      // Mock Google Login mode
      const googleUser = { uid: 'mock-uid', email: 'google.user@nyaay.ai', displayName: 'Google User', getIdToken: async () => 'mock-token' };
      localStorage.setItem('nyaay_mock_user', JSON.stringify({ uid: 'mock-uid', email: 'google.user@nyaay.ai', displayName: 'Google User' }));
      setMockUser(googleUser);
      setCurrentUser(googleUser);
      setLoading(false);
      return googleUser;
    }
  };

  const syncProfile = async (role) => {
    if (!currentUser) throw new Error('No authenticated user found');
    setError(null);
    try {
      const token = currentUser.uid === 'mock-uid' ? 'mock-token' : await currentUser.getIdToken();
      const profile = await authService.syncUserProfile(token, currentUser.displayName || currentUser.email, role);
      setUserProfile(profile);
      return profile;
    } catch (err) {
      setError('Database synchronization failed.');
      throw err;
    }
  };

  const value = {
    currentUser,
    userProfile,
    loading,
    error,
    signup,
    login,
    logout,
    signInWithGoogle,
    syncProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
