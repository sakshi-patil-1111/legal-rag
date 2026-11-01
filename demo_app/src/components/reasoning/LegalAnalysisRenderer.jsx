import React, { useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { 
  AlertCircle, 
  Scale, 
  FileText, 
  ShieldAlert, 
  ShieldCheck,
  Gavel, 
  Landmark, 
  Target,
  ArrowRight,
  MessageSquare,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Lock
} from 'lucide-react';
import CitationPill from '../common/CitationPill';
import StreamingText from '../common/StreamingText';

const SECTION_ICONS = {
  executive_summary: <Target className="w-4 h-4 text-accent" />,
  chronological_timeline: <FileText className="w-4 h-4 text-ink-muted" />,
  primary_legal_issues: <Scale className="w-4 h-4 text-accent" />,
  applicable_statutes: <Landmark className="w-4 h-4 text-blue-700" />,
  judicial_precedents: <Gavel className="w-4 h-4 text-ink" />,
  arguments_for: <ShieldCheck className="w-4 h-4 text-emerald-700" />,
  arguments_against: <ShieldAlert className="w-4 h-4 text-amber-700" />,
  evidence_analysis: <FileText className="w-4 h-4 text-ink-muted" />,
  risk_assessment: <AlertCircle className="w-4 h-4 text-amber-700" />,
  litigation_strategy: <Target className="w-4 h-4 text-accent" />,
  confidence_summary: <Scale className="w-4 h-4 text-emerald-700" />,
  cross_module_links: <ArrowRight className="w-4 h-4 text-accent" />
};

const SECTION_TITLES = {
  executive_summary: "Executive Summary",
  chronological_timeline: "Chronological Timeline",
  primary_legal_issues: "Primary Legal Issues",
  applicable_statutes: "Applicable Statutes & Grounded Sections",
  judicial_precedents: "Judicial Precedents & Case Law",
  arguments_for: "Arguments in Favor (Your Position)",
  arguments_against: "Arguments Against (Opposing Position)",
  evidence_analysis: "Evidentiary Analysis (BSA 2023)",
  risk_assessment: "Litigation Risk & Exposure Evaluation",
  litigation_strategy: "Strategic Phased Action Plan",
  confidence_summary: "Confidence & Statutory Grounding Score",
  cross_module_links: "Next Steps & Execution Modules"
};

const renderNestedContent = (content) => {
  if (content === null || content === undefined) return null;
  
  if (typeof content === 'string') {
    return (
      <div className="prose max-w-none text-xs sm:text-[13px] text-ink leading-relaxed font-sans prose-p:my-1.5 prose-headings:font-serif prose-headings:font-bold prose-headings:text-ink">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    );
  }

  if (Array.isArray(content)) {
    if (content.every(item => typeof item === 'string')) {
      return (
        <ul className="list-disc pl-4 space-y-1.5 text-xs sm:text-[13px] text-ink leading-relaxed font-sans">
          {content.map((item, idx) => (
            <li key={idx}><ReactMarkdown>{item}</ReactMarkdown></li>
          ))}
        </ul>
      );
    }
    
    return (
      <div className="space-y-2.5">
        {content.map((item, idx) => (
          <div key={idx} className="bg-paper p-3 rounded-[3px] border border-rule">
            {Object.entries(item).map(([key, val]) => (
              <div key={key} className="mb-2 last:mb-0">
                <h5 className="text-[11px] font-mono font-bold text-accent-text uppercase tracking-wider mb-0.5">
                  {key.replace(/_/g, ' ')}
                </h5>
                <div className="text-ink text-xs sm:text-[13px] leading-relaxed">
                  {typeof val === 'string' ? <ReactMarkdown>{val}</ReactMarkdown> : renderNestedContent(val)}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    );
  }

  if (typeof content === 'object') {
    return (
      <div className="space-y-2.5">
        {Object.entries(content).map(([key, val]) => (
          <div key={key} className="bg-paper p-3 rounded-[3px] border border-rule">
            <h5 className="text-[11px] font-mono font-bold text-accent-text uppercase tracking-wider mb-1">
              {key.replace(/_/g, ' ')}
            </h5>
            <div className="text-ink text-xs sm:text-[13px] leading-relaxed">
               {typeof val === 'string' ? <ReactMarkdown>{val}</ReactMarkdown> : renderNestedContent(val)}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return null;
};

const AnalysisCard = ({ title, icon, content, isCrossModule = false, className = "", defaultOpen = false }) => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(defaultOpen);

  if (!content) return null;

  return (
    <div className={`bg-white rounded-[4px] p-4 border border-rule shadow-2xs transition-all duration-200 w-full ${className}`}>
      <div 
        className="flex items-center justify-between cursor-pointer select-none"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-paper rounded border border-rule">
            {icon}
          </div>
          <h4 className="font-serif font-bold text-sm text-ink">{title}</h4>
        </div>
        <div className="p-1 text-ink-muted hover:text-ink transition-colors">
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </div>
      
      {isOpen && (
        <div className="mt-3 pt-3 border-t border-paper-sunken">
          {isCrossModule ? (
            <div className="space-y-3">
              <p className="text-xs text-ink-secondary">{content}</p>
              <div className="flex flex-wrap gap-2 pt-1">
                <Link to="/know-your-kanoon" className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-dark hover:bg-dark-rule text-white rounded-[2px] text-xs font-bold transition-colors">
                  <Scale className="w-3.5 h-3.5 text-accent" />
                  <span>{t ? t('reasoning.kanoonQA', 'Kanoon Q&A') : 'Kanoon Q&A'}</span>
                </Link>
                <Link to="/dochub" className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-paper hover:bg-paper-sunken text-ink border border-rule rounded-[2px] text-xs font-bold transition-colors">
                  <FileText className="w-3.5 h-3.5 text-accent" />
                  <span>{t ? t('reasoning.draftLegalNotice', 'Draft Legal Notice') : 'Draft Legal Notice'}</span>
                </Link>
                <Link to="/upload-chat" className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-paper hover:bg-paper-sunken text-ink border border-rule rounded-[2px] text-xs font-bold transition-colors">
                  <MessageSquare className="w-3.5 h-3.5 text-accent" />
                  <span>{t ? t('reasoning.chatWithDocuments', 'Chat with Documents') : 'Chat with Documents'}</span>
                </Link>
              </div>
            </div>
          ) : (
            renderNestedContent(content)
          )}
        </div>
      )}
    </div>
  );
};

const LegalAnalysisRenderer = ({ content }) => {
  const { t } = useTranslation();
  const parsedData = useMemo(() => {
    try {
      if (!content) return null;
      
      let cleanedContent = content.trim();
      
      // Try to extract JSON if it's wrapped in a code block or has leading/trailing text
      const startIndex = cleanedContent.indexOf('{');
      const endIndex = cleanedContent.lastIndexOf('}');
      
      if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
        cleanedContent = cleanedContent.substring(startIndex, endIndex + 1);
      }

      // Remove trailing commas which often cause JSON.parse to fail
      cleanedContent = cleanedContent.replace(/,\s*([}\]])/g, '$1');

      // Fix unescaped newlines inside string values (common LLM error)
      cleanedContent = cleanedContent.replace(/"([^"\\]*(?:\\.[^"\\]*)*)"/g, (match, p1) => {
        return '"' + p1.replace(/\n/g, '\\n').replace(/\r/g, '\\r').replace(/\t/g, '\\t') + '"';
      });

      const data = JSON.parse(cleanedContent);
      if (typeof data === 'object' && data !== null) {
        return data;
      }
      return null;
    } catch (e) {
      console.error("Failed to parse JSON in LegalAnalysisRenderer:", e, content);
      return null;
    }
  }, [content]);

  if (!parsedData) {
    return (
      <div className="p-5 bg-white rounded-[4px] border border-rule text-ink text-sm leading-relaxed">
        <StreamingText content={content} />
      </div>
    );
  }

  const hasBothArguments = parsedData.arguments_for && parsedData.arguments_against;

  return (
    <div className="flex flex-col space-y-4 w-full text-ink">
      
      {/* 1. Executive Summary */}
      {parsedData.executive_summary && (
        <AnalysisCard 
          title={SECTION_TITLES.executive_summary}
          icon={SECTION_ICONS.executive_summary}
          content={parsedData.executive_summary}
          defaultOpen={true}
        />
      )}

      {/* 2. Primary Legal Issues */}
      {parsedData.primary_legal_issues && (
        <AnalysisCard 
          title={SECTION_TITLES.primary_legal_issues}
          icon={SECTION_ICONS.primary_legal_issues}
          content={parsedData.primary_legal_issues}
          defaultOpen={true}
        />
      )}

      {/* 3. SIGNATURE TWO-COLUMN FOR / AGAINST COMPARATIVE SPLIT */}
      {hasBothArguments && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* FOR Column */}
          <div className="bg-emerald-50/40 border-2 border-emerald-300 rounded-[4px] p-4 shadow-2xs space-y-3">
            <div className="flex items-center justify-between border-b border-emerald-200 pb-2">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-700" />
                <h4 className="font-serif font-bold text-sm text-emerald-950">
                  Your Position (In Favor)
                </h4>
              </div>
              <span className="font-mono text-[10px] font-bold bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded border border-emerald-300">
                PRO SE ADVANTAGE
              </span>
            </div>
            <div className="text-xs sm:text-[13px] text-ink leading-relaxed">
              {renderNestedContent(parsedData.arguments_for)}
            </div>
          </div>

          {/* AGAINST Column */}
          <div className="bg-amber-50/40 border-2 border-amber-300 rounded-[4px] p-4 shadow-2xs space-y-3">
            <div className="flex items-center justify-between border-b border-amber-200 pb-2">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-accent" />
                <h4 className="font-serif font-bold text-sm text-amber-950">
                  Opposing Position (Counter-Arguments)
                </h4>
              </div>
              <span className="font-mono text-[10px] font-bold bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded border border-amber-300">
                LITIGATION RISK
              </span>
            </div>
            <div className="text-xs sm:text-[13px] text-ink leading-relaxed">
              {renderNestedContent(parsedData.arguments_against)}
            </div>
          </div>
        </div>
      )}

      {/* 4. Other Analysis Sections */}
      {Object.keys(SECTION_TITLES).map(key => {
        if (key === 'executive_summary' || key === 'primary_legal_issues' || key === 'cross_module_links') return null;
        if (hasBothArguments && (key === 'arguments_for' || key === 'arguments_against')) return null;
        if (!parsedData[key]) return null;

        return (
          <AnalysisCard 
            key={key}
            title={SECTION_TITLES[key]}
            icon={SECTION_ICONS[key] || <FileText className="w-4 h-4 text-ink-muted" />}
            content={parsedData[key]}
            defaultOpen={key === 'applicable_statutes' || key === 'risk_assessment'}
          />
        );
      })}

      {/* 5. Extra Unmapped Keys */}
      {Object.keys(parsedData).map(key => {
        if (SECTION_TITLES[key]) return null;
        return (
          <AnalysisCard 
            key={key}
            title={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            content={parsedData[key]}
            defaultOpen={false}
          />
        );
      })}

      {/* 6. Cross-Module Next Steps */}
      {parsedData.cross_module_links && (
        <AnalysisCard 
          title={SECTION_TITLES.cross_module_links}
          icon={SECTION_ICONS.cross_module_links}
          content={parsedData.cross_module_links}
          isCrossModule={true}
          defaultOpen={true}
        />
      )}
    </div>
  );
};

export default LegalAnalysisRenderer;
