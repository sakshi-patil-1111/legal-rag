import React from 'react';

/**
 * Shared idle / empty state component.
 *
 * Consistent across Kanoon Q&A, Legal Reasoning, Doc Chat.
 *
 * Props:
 *   icon      — React element (rendered inside the icon box)
 *   eyebrow   — small all-caps monospace label (e.g. "KANOON Q&A")
 *   title     — JSX or string headline
 *   subtitle  — one-line description string
 *   actions   — array of { label, onClick } quick-action buttons
 *   className — extra classes for outer wrapper
 */
export default function EmptyState({ icon, eyebrow, title, subtitle, actions = [], className = '' }) {
  return (
    <div className={`h-full flex flex-col items-center justify-center text-center max-w-md mx-auto px-6 py-10 ${className}`}>
      {/* Icon box — 14×14 cream square with single subtle border */}
      {icon && (
        <div className="w-14 h-14 bg-paper border border-paper-rule rounded-[4px] flex items-center justify-center mb-6 shadow-[0_1px_3px_rgba(26,24,20,0.06)]">
          {icon}
        </div>
      )}

      {/* Eyebrow */}
      {eyebrow && (
        <span className="text-[12px] font-bold uppercase tracking-[0.12em] text-ink-muted mb-3 block">
          {eyebrow}
        </span>
      )}

      {/* Title */}
      {title && (
        <h2
          className="text-[22px] font-bold text-ink mb-2 leading-tight"
          style={{ fontFamily: 'Newsreader, Georgia, serif' }}
        >
          {title}
        </h2>
      )}

      {/* Subtitle — one-line max */}
      {subtitle && (
        <p className="text-[13px] text-ink-muted mb-7 leading-relaxed">
          {subtitle}
        </p>
      )}

      {/* Quick action buttons */}
      {actions.length > 0 && (
        <div className="flex flex-col gap-2 w-full max-w-[300px]">
          {actions.map((action, i) => (
            <button
              key={i}
              onClick={action.onClick}
              className="text-[13px] bg-paper hover:bg-paper-warm border border-paper-rule px-4 py-2.5 rounded-[4px] text-ink-muted hover:text-ink text-left transition-colors focus:outline-none focus-visible:ring-1 focus-visible:ring-accent"
            >
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
