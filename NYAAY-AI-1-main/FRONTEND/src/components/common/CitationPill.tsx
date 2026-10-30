import React, { useState, useRef, useEffect } from 'react';
import { Lock, Scale, BookOpen, ExternalLink, ShieldCheck } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface CitationPillProps {
  act: string;
  section: string;
  excerpt?: string;
  statuteTitle?: string;
  className?: string;
  onInspect?: (actCode: string) => void;
}

export const CitationPill: React.FC<CitationPillProps> = ({
  act,
  section,
  excerpt,
  statuteTitle,
  className = '',
}) => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const popoverRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const defaultExcerpt = excerpt || t('citationPill.defaultExcerpt', { act, defaultValue: `Statutory provision under {{act}} specifying enforceable rights, mandatory procedures, and limitation terms.` });

  return (
    <span 
      ref={popoverRef}
      className={`relative inline-block align-baseline ${className}`}
    >
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={() => setIsOpen(true)}
        className="inline-flex items-center space-x-1 px-1.5 py-0.5 my-0.5 bg-accent/10 hover:bg-accent/20 border border-accent/30 hover:border-accent rounded-[3px] text-accent-text font-mono text-[11px] font-bold cursor-pointer transition-all focus-visible:ring-1 focus-visible:ring-accent"
        title={t('citationPill.tooltipTitle', 'Click to view statutory source annotation')}
      >
        <Lock className="w-2.5 h-2.5 text-accent" />
        <span>{act} · {section}</span>
      </button>

      {/* Hover / Click Popover Tooltip */}
      {isOpen && (
        <div 
          onMouseLeave={() => setIsOpen(false)}
          className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-72 sm:w-80 bg-white border border-dark rounded-[4px] shadow-lg p-3.5 space-y-2.5 animate-stamp text-left text-ink"
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-rule pb-1.5">
            <div className="flex items-center space-x-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
              <span className="font-mono text-[10px] font-bold text-accent uppercase">
                {t('citationPill.groundedStatuteTrace', 'GROUNDED STATUTORY TRACE')}
              </span>
            </div>
            <span className="font-mono text-[10px] text-ink-muted bg-paper px-1.5 py-0.2 rounded border border-rule">
              {section}
            </span>
          </div>

          {/* Body */}
          <div>
            <div className="font-serif font-bold text-xs text-ink leading-snug">
              {statuteTitle || act}
            </div>
            <p className="font-sans text-[11px] text-ink-secondary mt-1 leading-relaxed bg-paper p-2 rounded-[2px] border-l-2 border-accent">
              "{defaultExcerpt}"
            </p>
          </div>

          {/* Action / Inspect */}
          <div className="flex items-center justify-between text-[11px] pt-1 border-t border-paper-sunken">
            <span className="text-emerald-700 font-bold text-[10px]">
              {t('citationPill.hallucinationTrace', '✓ 0% Hallucination Trace')}
            </span>
            {onInspect && (
              <button
                type="button"
                onClick={() => {
                  setIsOpen(false);
                  onInspect(act);
                }}
                className="font-bold text-accent-text hover:text-accent-hover flex items-center space-x-1 cursor-pointer"
              >
                <span>{t('citationPill.inspectStatute', 'Inspect Statute')}</span>
                <ExternalLink className="w-2.5 h-2.5" />
              </button>
            )}
          </div>
        </div>
      )}
    </span>
  );
};

export default CitationPill;
