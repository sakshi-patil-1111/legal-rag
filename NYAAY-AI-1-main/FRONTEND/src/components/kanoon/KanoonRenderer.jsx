import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Gavel, Info, BookOpen, ShieldCheck, Scale, ExternalLink } from 'lucide-react';
import ExpandableSource from './ExpandableSource';
import StreamingText from '../common/StreamingText';
import CitationPill from '../common/CitationPill';
import { useTranslation } from 'react-i18next';

const KanoonRenderer = ({ content }) => {
  const { t } = useTranslation();
  let parsed = null;
  try {
    if (typeof content === 'string') {
      let cleanedContent = content.trim();
      const startIndex = cleanedContent.indexOf('{');
      const endIndex = cleanedContent.lastIndexOf('}');
      if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
        cleanedContent = cleanedContent.substring(startIndex, endIndex + 1);
      }
      cleanedContent = cleanedContent.replace(/,\s*([}\]])/g, '$1');
      parsed = JSON.parse(cleanedContent);
    } else {
      parsed = content;
    }
  } catch (e) {
    return (
      <div className="prose prose-stone max-w-none text-ink text-sm leading-relaxed p-4 bg-white border border-rule rounded-[4px]">
        <StreamingText content={typeof content === 'string' ? content : ''} />
      </div>
    );
  }

  if (!parsed || (!parsed.answer && !parsed.summary)) return null;

  return (
    <div className="space-y-6 text-ink">
      {/* 1. Domain Badge & Status */}
      {parsed.legal_domain && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="bg-accent/10 text-accent-text text-xs font-mono font-bold px-3 py-1 rounded-[2px] border border-accent/25 uppercase tracking-wider">
            {parsed.legal_domain}
          </span>
          <span className="text-[12px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-[2px] font-bold flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
            <span>{t('kanoon.groundedStatuteAnalysis', 'GROUNDED STATUTE ANALYSIS')}</span>
          </span>
        </div>
      )}
      
      {/* 2. Executive Summary */}
      {parsed.summary && (
        <div className="bg-white border border-rule rounded-[4px] p-5 shadow-2xs space-y-2">
          <div className="flex items-center justify-between border-b border-rule pb-2">
            <h4 className="font-serif font-bold text-ink text-base flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-accent" />
              <span>{t('kanoon.executiveSummary', 'Executive Summary')}</span>
            </h4>
            <span className="text-[11px] font-mono text-ink-muted">{t('kanoon.sub500ms', 'SUB-500ms TTFT')}</span>
          </div>
          <div className="text-xs sm:text-sm text-ink-secondary leading-relaxed font-sans pt-1">
            <StreamingText content={parsed.summary} speed={24} />
          </div>
        </div>
      )}
      
      {/* 3. Detailed Analysis with Streaming */}
      {parsed.answer && (
        <div className="bg-white border border-rule rounded-[4px] p-5 shadow-2xs space-y-3">
          <h4 className="font-serif font-bold text-ink text-base border-b border-rule pb-2">
            {t('kanoon.detailedStatutoryAnalysis', 'Detailed Statutory Analysis')}
          </h4>
          <div className="text-xs sm:text-sm text-ink leading-relaxed font-sans space-y-2">
            <StreamingText content={parsed.answer} speed={20} />
          </div>
        </div>
      )}
      
      {/* 4. Key Provisions & Sections */}
      {parsed.key_clauses && parsed.key_clauses.length > 0 && (
        <div className="bg-paper border border-rule rounded-[4px] p-5 space-y-3 shadow-2xs">
          <h4 className="font-serif font-bold text-ink text-sm flex items-center gap-2 border-b border-rule pb-2">
            <Gavel className="w-4 h-4 text-accent" />
            <span>{t('kanoon.keyProvisions', 'Key Provisions & Sections')}</span>
          </h4>
          <div className="space-y-2">
            {parsed.key_clauses.map((clause, i) => (
              <div key={i} className="flex items-start gap-2.5 bg-white p-3 rounded-[3px] border border-rule">
                <span className="font-mono text-[11px] font-bold text-accent px-1.5 py-0.5 bg-paper rounded shrink-0 mt-0.5">
                  §{i + 1}
                </span>
                <span className="text-xs sm:text-sm text-ink leading-relaxed font-sans">
                  {clause}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* 5. Precedents */}
      {parsed.similar_cases && (
        <div className="bg-white border border-rule rounded-[4px] p-5 space-y-2 shadow-2xs">
          <h4 className="font-serif font-bold text-ink text-base border-b border-rule pb-2">
            {t('kanoon.relevantPrecedents', 'Relevant Precedents & Judicial Rulings')}
          </h4>
          <div className="text-xs sm:text-sm text-ink-secondary leading-relaxed font-sans pt-1">
            <ReactMarkdown>{parsed.similar_cases}</ReactMarkdown>
          </div>
        </div>
      )}
      
      {/* 6. Sources */}
      {parsed.sources && parsed.sources.length > 0 && (
        <div className="bg-paper border border-rule rounded-[4px] p-5 space-y-3 shadow-2xs">
          <h4 className="font-serif font-bold text-ink text-sm border-b border-rule pb-2 flex items-center justify-between">
            <span>{t('kanoon.sourcesAndAuthorities', 'Sources & Statutory Authorities')}</span>
            <span className="font-mono text-[11px] text-ink-muted">{t('kanoon.sourcesCited', { count: parsed.sources.length, defaultValue: `${parsed.sources.length} SOURCES CITED` })}</span>
          </h4>
          <div className="space-y-2">
            {parsed.sources.map((source, idx) => (
              <ExpandableSource key={idx} source={source} />
            ))}
          </div>
        </div>
      )}
      
      {/* 7. Disclaimer */}
      {parsed.disclaimer && (
        <div className="bg-amber-50 p-4 rounded-[4px] border border-amber-300 flex gap-3 text-xs text-amber-900 shadow-2xs">
          <Info className="text-accent shrink-0 mt-0.5 w-4 h-4" />
          <p className="leading-relaxed font-sans">
            <strong className="font-bold">{t('kanoon.statutoryDisclaimer', 'Statutory Disclaimer:')}</strong> {parsed.disclaimer}
          </p>
        </div>
      )}
    </div>
  );
};

export default KanoonRenderer;
