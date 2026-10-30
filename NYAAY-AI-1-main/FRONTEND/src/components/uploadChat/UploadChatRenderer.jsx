import React from 'react';
import ReactMarkdown from 'react-markdown';
import { FileText, ChevronRight } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const UploadChatRenderer = ({ content }) => {
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
      <div className="prose prose-slate max-w-none text-slate-700">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    );
  }

  if (!parsed || !parsed.answer) return null;

  return (
    <div className="space-y-4">
      {/* Answer */}
      <div>
        <div className="prose prose-sm md:prose-base prose-slate max-w-none text-slate-700">
          <ReactMarkdown>{parsed.answer}</ReactMarkdown>
        </div>
      </div>
      
      {/* Summary Reference */}
      {parsed.summary && (
        <div className="mt-4 pt-4 border-t border-slate-200">
          <div className="bg-slate-50 border border-slate-200 p-4 rounded-xl flex gap-3">
            <FileText className="text-primary-600 shrink-0 mt-0.5" size={18} />
            <div>
              <h5 className="text-sm font-semibold text-slate-800 mb-1">{t('uploadChat.contextReference')}</h5>
              <div className="text-xs md:text-sm text-slate-600 leading-relaxed">
                <ReactMarkdown>{parsed.summary}</ReactMarkdown>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadChatRenderer;
