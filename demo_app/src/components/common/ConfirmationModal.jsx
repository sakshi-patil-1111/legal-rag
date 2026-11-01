import React, { useEffect, useRef, useId } from 'react';
import Button from './Button';
import { useTranslation } from 'react-i18next';

/**
 * ConfirmationModal.
 *
 * Was `rounded-2xl` with `text-zinc-900` / `bg-zinc-50` / `border-zinc-100` —
 * default-Tailwind grey in a warm-paper product with 2-6px radii. Restyled.
 *
 * Also added the behaviour a dialog is expected to have and did not have:
 * Escape to cancel, backdrop click to cancel, background scroll lock, initial
 * focus on the confirm action, and aria-labelledby/describedby wiring.
 */
export default function ConfirmationModal({
  isOpen,
  title,
  body,
  onConfirm,
  onCancel,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  isDestructive = false,
  loading = false,
}) {
  const { t } = useTranslation();
  const confirmRef = useRef(null);
  const id = useId();

  const actualConfirmText = confirmText === 'Confirm' ? t('confirmationModal.confirm') : confirmText;
  const actualCancelText = cancelText === 'Cancel' ? t('confirmationModal.cancel') : cancelText;

  /* Escape to cancel + scroll lock */
  useEffect(() => {
    if (!isOpen) return;

    const onKeyDown = (e) => {
      if (e.key === 'Escape' && !loading) onCancel?.();
    };
    document.addEventListener('keydown', onKeyDown);

    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    confirmRef.current?.focus();

    return () => {
      document.removeEventListener('keydown', onKeyDown);
      document.body.style.overflow = prevOverflow;
    };
  }, [isOpen, loading, onCancel]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-dark/60 backdrop-blur-[2px]"
      onClick={() => !loading && onCancel?.()}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={`${id}-title`}
        aria-describedby={body ? `${id}-body` : undefined}
        onClick={(e) => e.stopPropagation()}
        className="bg-[#FFFFFF] border border-rule rounded-[6px] shadow-modal w-full max-w-md overflow-hidden animate-stamp"
      >
        {/* Accent edge — matches the stamped-document language */}
        <div className={`h-[3px] ${isDestructive ? 'bg-[#B42318]' : 'bg-accent'}`} />

        <div className="p-6">
          <h2
            id={`${id}-title`}
            className="font-serif text-lg font-bold text-ink leading-snug"
          >
            {title}
          </h2>
          {body && (
            <p id={`${id}-body`} className="mt-2 text-[14px] text-ink-secondary leading-relaxed">
              {body}
            </p>
          )}
        </div>

        <div className="bg-paper-sunken px-6 py-4 flex items-center justify-end gap-3 border-t border-rule">
          <Button variant="ghost" size="sm" onClick={onCancel} disabled={loading}>
            {actualCancelText}
          </Button>
          <Button
            ref={confirmRef}
            variant={isDestructive ? 'danger' : 'primary'}
            size="sm"
            onClick={onConfirm}
            loading={loading}
          >
            {actualConfirmText}
          </Button>
        </div>
      </div>
    </div>
  );
}
