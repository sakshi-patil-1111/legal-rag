import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// Check if valid Firebase API key is provided
const isConfigValid = 
  firebaseConfig.apiKey && 
  !firebaseConfig.apiKey.startsWith('mock-') && 
  firebaseConfig.apiKey.length > 15;

let app = null;
let auth = null;

if (isConfigValid) {
  try {
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
  } catch (error) {
    console.warn('Firebase SDK initialization failed:', error.message);
  }
} else {
  console.warn('Firebase API key is mock or missing. Auth will run in local simulator mode until real credentials are provided in .env.');
}

export { app, auth };
export default app;
