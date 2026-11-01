import React, { createContext, useContext, useState } from 'react';
import i18n from '../i18n';

/**
 * LanguageContext — single source of truth for the selected UI language.
 *
 * Persists to localStorage ('nyaay_lang') so selection survives page navigation.
 * setLanguage() also calls i18n.changeLanguage() for instant Layer 1 string swap.
 *
 * What setLanguage does NOT do:
 *   - Does not trigger any Groq/translation API call.
 *   - Does not re-translate existing on-screen responses.
 *   - The backend language param is sent only on the next query submission.
 */

export const LANGUAGES = [
  { code: 'en', label: 'EN', fullName: 'English', nativeName: 'English' },
  { code: 'hi', label: 'HI', fullName: 'Hindi', nativeName: 'हिन्दी' },
  { code: 'bn', label: 'BN', fullName: 'Bengali', nativeName: 'বাংলা' },
  { code: 'ta', label: 'TA', fullName: 'Tamil', nativeName: 'தமிழ்' },
];

const LanguageContext = createContext({
  language: 'en',
  setLanguage: () => {},
  LANGUAGES,
});

export function LanguageProvider({ children }) {
  const [language, setLanguageState] = useState(
    () => localStorage.getItem('nyaay_lang') || 'en'
  );

  const setLanguage = (code) => {
    setLanguageState(code);
    localStorage.setItem('nyaay_lang', code);
    i18n.changeLanguage(code);  // instant Layer 1 string swap — no network call
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, LANGUAGES }}>
      {children}
    </LanguageContext.Provider>
  );
}

export const useLanguage = () => useContext(LanguageContext);

export default LanguageContext;
