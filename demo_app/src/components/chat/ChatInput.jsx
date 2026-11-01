import React, { useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const ChatInput = ({ value, onChange, onSubmit, isLoading, placeholder }) => {
  const { t } = useTranslation();
  const actualPlaceholder = placeholder || t('chatInput.placeholder');
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [value]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !isLoading) {
        onSubmit(e);
      }
    }
  };

  return (
    <div className="relative max-w-4xl mx-auto w-full">
      <div className="relative flex items-end border border-paper-rule bg-paper rounded-card overflow-hidden focus-within:ring-1 focus-within:ring-amber focus-within:border-amber transition-all shadow-stamp">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={onChange}
          onKeyDown={handleKeyDown}
          placeholder={actualPlaceholder}
          disabled={isLoading}
          rows={1}
          className="w-full max-h-[200px] py-3.5 pl-4 pr-14 bg-transparent text-ink text-[14px] placeholder-ink-fog focus:outline-none resize-none"
        />
        <div className="absolute right-2.5 bottom-2.5">
          <button
            onClick={onSubmit}
            disabled={!value.trim() || isLoading}
            className={`p-2 rounded-button flex items-center justify-center transition-all ${
              value.trim() && !isLoading
                ? 'bg-ink text-paper hover:bg-ink-soft shadow-stamp'
                : 'bg-paper-warm text-ink-fog cursor-not-allowed border border-paper-rule'
            }`}
          >
            {isLoading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
          </button>
        </div>
      </div>
      <div className="text-center mt-2">
        <p className="text-[12px] text-ink-fog uppercase tracking-wider">
          {t('chatInput.footerDisclaimer')}
        </p>
      </div>
    </div>
  );
};

export default ChatInput;
