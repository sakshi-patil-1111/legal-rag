import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Globe, ChevronDown, Check } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';

/**
 * LanguageSelector — Restyled case-file language selector.
 *
 * Trigger: Compact icon + 2-letter uppercase monospace code + custom rotating chevron.
 * Menu: Cream/paper surface, 1px hairline border, 8px radius, soft elevation shadow,
 *       left orange accent bar and light orange wash for selected item, checkmark icon.
 */
export default function LanguageSelector({ className = '' }) {
  const { language, setLanguage, LANGUAGES } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const currentLang = LANGUAGES.find((l) => l.code === language) || LANGUAGES[0];

  // Close dropdown on outside click or Escape key
  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleOutsideClick);
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  const handleSelect = (code) => {
    setLanguage(code);
    setIsOpen(false);
  };

  return (
    <div className={`relative shrink-0 ${className}`} ref={dropdownRef}>
      {/* ── Trigger Button ── */}
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label={`Select language (Current: ${currentLang.fullName})`}
        className={`group flex items-center space-x-1.5 h-8 px-2.5 py-1.5 rounded-lg border text-[13px] font-sans font-medium transition-all duration-150 shadow-xs focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none cursor-pointer select-none ${
          isOpen
            ? 'bg-accent/10 border-accent text-paper'
            : 'bg-dark-raised/80 hover:bg-accent/10 border-rule-dark hover:border-accent text-slate hover:text-paper'
        }`}
      >
        {/* Globe icon (16px) */}
        <Globe
          aria-hidden="true"
          className={`w-4 h-4 shrink-0 transition-colors duration-150 ${
            isOpen ? 'text-accent' : 'text-slate-muted group-hover:text-slate'
          }`}
        />

        {/* 2-letter uppercase monospace code */}
        <span className="font-mono text-xs font-semibold tracking-wider text-slate group-hover:text-paper">
          {currentLang.label || currentLang.code.toUpperCase()}
        </span>

        {/* Custom Chevron with 180° rotation on open */}
        <ChevronDown
          aria-hidden="true"
          className={`w-3.5 h-3.5 shrink-0 transition-transform duration-200 ease-out ${
            isOpen ? 'rotate-180 text-accent' : 'text-slate-muted group-hover:text-slate'
          }`}
        />
      </button>

      {/* ── Dropdown Panel (Case File Aesthetic) ── */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -6, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.98 }}
            transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
            role="listbox"
            aria-label="Supported Languages"
            className="absolute right-0 top-full mt-2 w-60 bg-paper-raised border border-rule rounded-lg shadow-lifted py-1.5 z-50 overflow-hidden"
            style={{
              boxShadow: '0 12px 32px rgba(18, 24, 32, 0.12), 0 2px 8px rgba(18, 24, 32, 0.06)',
            }}
          >
            {/* Header label */}
            <div className="px-3 py-1.5 mb-1 border-b border-rule/60 flex items-center justify-between text-[11px] font-mono uppercase tracking-wider text-ink-muted">
              <span>Language // भाषा</span>
              <span className="text-[10px] text-accent-text font-bold">4 LOCALES</span>
            </div>

            {/* Language list */}
            <div className="flex flex-col space-y-0.5 px-1">
              {LANGUAGES.map((lang) => {
                const isSelected = language === lang.code;
                return (
                  <button
                    key={lang.code}
                    type="button"
                    role="option"
                    aria-selected={isSelected}
                    onClick={() => handleSelect(lang.code)}
                    className={`w-full flex items-center justify-between px-2.5 py-2 text-left text-sm rounded transition-colors duration-150 cursor-pointer ${
                      isSelected
                        ? 'bg-accent-wash/90 border-l-[3px] border-accent text-ink-primary font-medium pl-2'
                        : 'border-l-[3px] border-transparent text-ink-primary hover:bg-accent-wash/40 hover:border-l-accent/40 font-normal pl-2'
                    }`}
                  >
                    {/* Left: Monospace code pill + Name + Native Script */}
                    <div className="flex items-center space-x-2 min-w-0">
                      <span
                        className={`font-mono text-[10px] font-semibold px-1.5 py-0.5 rounded shrink-0 ${
                          isSelected
                            ? 'bg-accent/15 text-accent-text border border-accent/30'
                            : 'bg-paper-sunken text-ink-muted border border-rule/70'
                        }`}
                      >
                        {lang.label || lang.code.toUpperCase()}
                      </span>
                      <div className="flex items-baseline space-x-1.5 truncate">
                        <span className="text-[13px] font-sans text-ink-primary">
                          {lang.fullName}
                        </span>
                        {lang.nativeName && lang.nativeName !== lang.fullName && (
                          <span className="text-xs font-sans text-ink-tertiary">
                            ({lang.nativeName})
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Right: Orange checkmark on active */}
                    {isSelected && (
                      <Check
                        aria-hidden="true"
                        className="w-4 h-4 text-accent shrink-0 ml-2"
                      />
                    )}
                  </button>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
