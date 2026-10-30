/**
 * Formats Firebase Auth errors into friendly, user-facing error messages.
 */
export function formatAuthError(error) {
  if (!error) return '';
  const code = error.code || '';
  const message = error.message || '';

  switch (code) {
    case 'auth/invalid-api-key':
    case 'auth/api-key-not-valid':
      return 'Invalid Firebase API Key. Please verify your VITE_FIREBASE_API_KEY in .env file.';
    case 'auth/invalid-credential':
    case 'auth/wrong-password':
    case 'auth/user-not-found':
      return 'Invalid email or password. Please check your credentials.';
    case 'auth/email-already-in-use':
      return 'An account with this email address already exists. Try signing in instead.';
    case 'auth/weak-password':
      return 'Password is too weak. Please use at least 6 characters.';
    case 'auth/invalid-email':
      return 'Please enter a valid email address.';
    case 'auth/popup-closed-by-user':
      return 'Google sign-in was canceled before completing.';
    case 'auth/popup-blocked':
      return 'Sign-in popup was blocked by your browser. Please allow popups for this site.';
    case 'auth/cancelled-popup-request':
      return 'Sign-in popup request was canceled.';
    case 'auth/account-exists-with-different-credential':
      return 'An account already exists with the same email using a different sign-in method.';
    case 'auth/operation-not-allowed':
      return 'Sign-in method is not enabled in Firebase Console (Authentication -> Sign-in method).';
    case 'auth/network-request-failed':
      return 'Network request failed. Please check your internet connection.';
    default:
      if (message.includes('api-key-not-valid')) {
        return 'Invalid Firebase API Key. Please verify VITE_FIREBASE_API_KEY in your .env file.';
      }
      return message.replace(/^Firebase:\s*Error\s*\([^)]+\):\s*/i, '');
  }
}
