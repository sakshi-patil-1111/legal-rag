import React from 'react';
import { useTranslation } from 'react-i18next';

/**
 * LoadingSpinner.
 *
 * `md` previously used `border-3`, which Tailwind does not generate (only
 * 0/2/4/8 plus the 1px default). That size rendered with no border width at
 * all — an invisible spinner. Arbitrary values used instead.
 */
export default function LoadingSpinner({ size = 'md', className = '', label }) {
  const { t } = useTranslation();
  const finalLabel = label || t('loadingSpinner.loading', 'Loading');

  const sizeClasses = {
    xs: 'w-3 h-3 border-[1.5px]',
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-[3px]',
    lg: 'w-12 h-12 border-4',
  };

  return (
    <div
      className={`relative flex items-center justify-center ${className}`}
      role="status"
      aria-label={finalLabel}
    >
      <div
        className={`${sizeClasses[size] || sizeClasses.md} border-current opacity-25 rounded-full absolute`}
      />
      <div
        className={`${sizeClasses[size] || sizeClasses.md} border-transparent border-t-current rounded-full animate-spin`}
      />
    </div>
  );
}
