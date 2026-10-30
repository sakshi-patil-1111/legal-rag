import React from 'react';
import ReactMarkdown from 'react-markdown';
import { useTranslation } from 'react-i18next';

const MessageBubble = ({ message, renderContent }) => {
  const { t } = useTranslation();
  const isUser = message.role === 'user';

  return (
    <div className={`flex w-full py-5 px-4 md:px-8 ${isUser ? 'justify-end' : 'justify-start border-b border-paper-rule bg-paper-warm/40'}`}>
      <div className={`flex gap-4 max-w-4xl ${isUser ? 'flex-row-reverse' : 'flex-row w-full mx-auto'}`}>
        {/* Avatar */}
        <div className="flex-shrink-0 mt-0.5">
          {isUser ? (
            <div className="w-7 h-7 bg-paper-rule rounded-stamp flex items-center justify-center border border-paper-border">
              <span className="text-[12px] font-bold text-ink-muted uppercase">{t('messageBubble.you')}</span>
            </div>
          ) : (
            <div className="w-7 h-7 bg-ink rounded-stamp flex items-center justify-center shadow-stamp">
              <span
                className="font-display italic text-[13px] font-bold text-paper leading-none"
                style={{ fontFamily: 'Newsreader, Georgia, serif' }}
              >
                N
              </span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className={`flex flex-col min-w-0 flex-1 ${isUser ? 'items-end' : 'items-start'}`}>
          <div className="text-[12px] font-bold mb-2 text-ink-fog uppercase tracking-wider">
            {isUser ? t('messageBubble.yourQuery') : t('messageBubble.nyaayAnalysis')}
          </div>
          <div className={`text-[14px] leading-relaxed ${
            isUser
              ? 'bg-ink text-paper px-4 py-3 rounded-card rounded-tr-stamp inline-block max-w-[90%] shadow-stamp'
              : 'text-ink w-full'
          }`}>
            {isUser ? (
              <div className="whitespace-pre-wrap">{message.content}</div>
            ) : (
              renderContent ? renderContent(message.content) : (
                <div className="prose prose-sm max-w-none prose-headings:font-display prose-headings:text-ink prose-strong:text-ink prose-li:text-ink prose-a:text-amber">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
              )
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
