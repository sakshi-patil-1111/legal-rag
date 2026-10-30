import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Scale, AlertCircle } from 'lucide-react';
import WorkspaceContainer from '../components/common/WorkspaceContainer';
import ConversationLayout from '../components/chat/ConversationLayout';
import ChatInput from '../components/chat/ChatInput';
import MessageBubble from '../components/chat/MessageBubble';
import LegalAnalysisRenderer from '../components/reasoning/LegalAnalysisRenderer';
import EmptyState from '../components/common/EmptyState';
import { generateReasoning } from '../services/reasoningService';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';

const LegalReasoningChatArea = ({ refreshConversations }) => {
  const { t } = useTranslation();
  const { currentUser } = useAuth();
  const { language } = useLanguage();
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);
  
  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

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
    
    abortControllerRef.current = new AbortController();
    
    try {
      const token = await currentUser.getIdToken();
      const response = await generateReasoning(
        token,
        userMessage.content, 
        activeConversationId, // pass conversation_id
        abortControllerRef.current.signal,
        language
      );
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.content,
        citations: response.citations || [],
        id: response.analysis_id
      }]);
      
      // If it's a new conversation, update the active ID and refresh sidebar
      if (!activeConversationId && response.conversation_id) {
        setActiveConversationId(response.conversation_id);
        if (refreshConversations) refreshConversations();
      }
      
    } catch (err) {
      if (err.name === 'CanceledError' || err.message === 'canceled') {
        console.log('Request canceled');
      } else {
        setError(err.message || 'Failed to generate legal reasoning.');
      }
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
    // Map backend messages to frontend format if needed
    setMessages(loadedMessages);
  };

  return (
    <ConversationLayout
      featureType="legal_reasoning"
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
              <Scale className="w-4 h-4 text-amber" />
            </div>
            <div>
              <span className="label-stamp text-ink-fog block">{t('legalReasoning.subtitle')}</span>
              <h1 className="text-[15px] font-semibold text-ink leading-tight" style={{ fontFamily: 'Newsreader, Georgia, serif' }}>{t('legalReasoning.title')}</h1>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto bg-paper-warm/30 relative scroll-smooth">
          {messages.length === 0 ? (
            <EmptyState
              icon={<span className="font-serif italic text-[22px] font-bold text-accent" style={{ fontFamily: 'Newsreader, Georgia, serif' }}>⚖</span>}
              eyebrow={t('legalReasoning.emptyState.eyebrow')}
              title={<>{t('legalReasoning.emptyState.titleLine1')}<br /><span className="italic font-normal">{t('legalReasoning.emptyState.titleLine2')}</span></>}
              subtitle={t('legalReasoning.emptyState.subtitle')}
              actions={[
                { label: t('legalReasoning.emptyState.action1'), onClick: () => setInputValue('Analyze a potential contract dispute regarding late delivery...') },
                { label: t('legalReasoning.emptyState.action2'), onClick: () => setInputValue('What are the legal steps for an eviction notice...') },
                { label: t('legalReasoning.emptyState.action3'), onClick: () => setInputValue('Analyze the new BNS provisions regarding...') },
              ]}
            />
          ) : (
            <div className="pb-32">
              {messages.map((msg, idx) => (
                <MessageBubble 
                  key={idx} 
                  message={msg} 
                  renderContent={msg.role === 'assistant' ? (content) => <LegalAnalysisRenderer content={content} /> : null}
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
                      <span className="text-[12px] text-ink-fog uppercase tracking-wider ml-1">{t('legalReasoning.reasoning')}</span>
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
              placeholder={t('legalReasoning.placeholder')}
            />
          </div>
        </div>
      </div>
    </ConversationLayout>
  );
};

const LegalReasoning = () => {
  return (
    <WorkspaceContainer>
      <LegalReasoningChatArea />
    </WorkspaceContainer>
  );
};

export default LegalReasoning;
