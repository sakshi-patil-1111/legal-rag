import React, { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { BookOpen, AlertCircle } from 'lucide-react';
import WorkspaceContainer from '../components/common/WorkspaceContainer';
import ConversationLayout from '../components/chat/ConversationLayout';
import ChatInput from '../components/chat/ChatInput';
import MessageBubble from '../components/chat/MessageBubble';
import KanoonRenderer from '../components/kanoon/KanoonRenderer';
import EmptyState from '../components/common/EmptyState';
import { askKanoon } from '../services/kanoonService';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { useTranslation } from 'react-i18next';

const KanoonChatArea = ({ refreshConversations }) => {
  const { currentUser } = useAuth();
  const { language } = useLanguage();
  const { t } = useTranslation();
  const location = useLocation();
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState(location.state?.presetQuery || '');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);
  
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isGenerating]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isGenerating) return;
    
    const userMessage = { role: 'user', content: inputValue.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsGenerating(true);
    setError(null);
    
    try {
      const token = await currentUser.getIdToken();
      const response = await askKanoon(token, userMessage.content, activeConversationId, language);
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: JSON.stringify(response) // Store as JSON string for renderer
      }]);
      
      // If it's a new conversation, update the active ID and refresh sidebar
      if (!activeConversationId && response.conversation_id) {
        setActiveConversationId(response.conversation_id);
        if (refreshConversations) refreshConversations();
      }
      
    } catch (err) {
      setError(err.message || t('kanoon.error.failedToGetAnswer', 'Failed to get an answer. Please try again.'));
    } finally {
      setIsGenerating(false);
    }
  };

  const handleNewChat = () => {
    setActiveConversationId(null);
    setMessages([]);
    setInputValue('');
    setError(null);
  };

  const handleSelectConversation = (conv) => {
    setActiveConversationId(conv.id);
  };

  const handleMessagesLoaded = (loadedMessages) => {
    // Backend returns { role, content }, content is JSON string for assistant
    setMessages(loadedMessages);
  };

  const EXAMPLE_QUESTIONS = [
    t('kanoon.exampleQuestion1', "Can my landlord evict me without notice?"),
    t('kanoon.exampleQuestion2', "What are my rights during police questioning?"),
    t('kanoon.exampleQuestion3', "What is anticipatory bail?"),
  ];

  return (
    <ConversationLayout
      featureType="know_kanoon"
      activeConversationId={activeConversationId}
      onNewChat={handleNewChat}
      onSelectConversation={handleSelectConversation}
      onMessagesLoaded={handleMessagesLoaded}
    >
      <div className="flex flex-col h-full bg-paper relative">
        {/* Header */}
        <header className="h-14 flex items-center px-6 border-b border-paper-rule bg-paper z-10 shrink-0">
          <div className="flex items-center gap-3 md:ml-12">
            <div className="p-1.5 bg-amber-light border border-amber/30 rounded-stamp flex items-center justify-center">
              <BookOpen className="w-4 h-4 text-amber" />
            </div>
            <div>
              <span className="label-stamp text-ink-fog block">{t('kanoon.header.legalResearch', 'LEGAL RESEARCH')}</span>
              <h1 className="text-[15px] font-semibold text-ink leading-tight" style={{ fontFamily: 'Newsreader, Georgia, serif' }}>{t('kanoon.header.title', 'Know Your Kanoon')}</h1>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto bg-paper-warm/30 relative scroll-smooth">
          {messages.length === 0 ? (
            <EmptyState
              icon={<span className="font-serif italic text-[22px] font-bold text-accent" style={{ fontFamily: 'Newsreader, Georgia, serif' }}>§</span>}
              eyebrow={t('kanoon.emptyState.eyebrow', 'KANOON Q&A')}
              title={<>{t('kanoon.emptyState.titleLine1', 'Ask any legal question.')}<br /><span className="italic font-normal">{t('kanoon.emptyState.titleLine2', 'Get a statute-grounded answer.')}</span></>}
              subtitle={t('kanoon.emptyState.subtitle', 'Indian law, grounded in statute.')}
              actions={EXAMPLE_QUESTIONS.map(q => ({ label: q, onClick: () => setInputValue(q) }))}
            />
          ) : (
            <div className="pb-32">
              {messages.map((msg, idx) => (
                <MessageBubble 
                  key={idx} 
                  message={msg} 
                  renderContent={msg.role === 'assistant' ? (content) => <KanoonRenderer content={content} /> : null}
                />
              ))}
              
              {isGenerating && (
                <MessageBubble
                  message={{ role: 'assistant', content: '' }}
                  renderContent={() => (
                    <div className="flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-1.5 h-1.5 rounded-full bg-amber animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-1.5 h-1.5 rounded-full bg-amber animate-bounce" style={{ animationDelay: '300ms' }} />
                      <span className="text-[12px] text-ink-fog uppercase tracking-wider ml-1">
                        {language === 'en' 
                          ? t('kanoon.status.retrieving', 'Retrieving...') 
                          : t('civic.status.translating', { defaultValue: `Translating to ${language.toUpperCase()}...`, lang: language.toUpperCase() })}
                      </span>
                    </div>
                  )}
                />
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-paper via-paper/90 to-transparent pt-10 pb-6 px-4 md:px-8 z-10 pointer-events-none">
          <div className="max-w-4xl mx-auto w-full pointer-events-auto">
            {error && (
              <div className="mb-4 p-3 bg-error-bg border border-error/30 rounded-card flex items-center gap-2 text-error text-[13px] shadow-stamp">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {error}
              </div>
            )}
            <ChatInput 
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onSubmit={handleSendMessage}
              isLoading={isGenerating}
              placeholder={t('kanoon.input.placeholder', 'E.g., Can my landlord evict me without notice?')}
            />
          </div>
        </div>
      </div>
    </ConversationLayout>
  );
};

const KnowYourKanoon = () => {
  return (
    <WorkspaceContainer>
      <KanoonChatArea />
    </WorkspaceContainer>
  );
};

export default KnowYourKanoon;