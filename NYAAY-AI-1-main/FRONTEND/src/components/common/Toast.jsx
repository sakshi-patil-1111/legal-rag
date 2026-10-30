import React, { useEffect } from 'react';
import { CheckCircle2, AlertTriangle, Info, X } from 'lucide-react';
import { useTranslation } from 'react-i18next';

/**
 * Toast.
 *
 * Was `rounded-xl bg-primary-hover text-emerald-400` — a 12px-radius pill with
 * an emerald tick, in a product whose radii are 2-4px and whose only accent is
 * rust. Restyled to the system and given variants so it can carry errors, not
 * just successes (there was previously no non-blocking way to report failure,
 * which is why `alert()` was still in the codebase).
 *
 * Backwards compatible: existing `<Toast isOpen message onClose />` callers
 * keep working and default to `variant="success"`.
 */

const VARIANTS = {
  success: { Icon: CheckCircle2,   iconClass: 'text-[#4ADE80]' },
  error:   { Icon: AlertTriangle,  iconClass: 'text-[#FCA5A5]' },
  info:    { Icon: Info,           iconClass: 'text-slate' },
};

export default function Toast({
  isOpen,
  message,
  onClose,
  duration = 3000,
  variant = 'success',
  dismissible = false,
}) {
  const { t } = useTranslation();
  useEffect(() => {
    // duration === 0 pins the toast open (use with dismissible for errors).
    if (isOpen && duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [isOpen, onClose, duration]);

  if (!isOpen) return null;

  const { Icon, iconClass } = VARIANTS[variant] || VARIANTS.success;

  return (
    <div
      className="fixed bottom-5 left-1/2 -translate-x-1/2 z-50 px-4 w-full max-w-md animate-stamp"
      role="status"
      aria-live={variant === 'error' ? 'assertive' : 'polite'}
    >
      <div className="bg-dark text-paper border-l-2 border-accent px-4 py-3 rounded-[3px] shadow-modal flex items-start gap-3 text-[13px] font-sans font-medium leading-relaxed">
        <Icon aria-hidden="true" className={`w-4 h-4 mt-0.5 shrink-0 ${iconClass}`} />
        <span className="flex-1">{message}</span>
        {dismissible && (
          <button
            type="button"
            onClick={onClose}
            aria-label={t('toast.dismiss')}
            className="shrink-0 -mr-1 -mt-0.5 p-1 rounded text-slate hover:text-paper transition-colors focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none"
          >
            <X aria-hidden="true" className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </div>
  );
}
