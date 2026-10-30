import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { FileText, AlertCircle, UploadCloud, FileUp } from 'lucide-react';
import WorkspaceContainer from '../components/common/WorkspaceContainer';
import ConversationLayout from '../components/chat/ConversationLayout';
import ChatInput from '../components/chat/ChatInput';
import MessageBubble from '../components/chat/MessageBubble';
import UploadChatRenderer from '../components/uploadChat/UploadChatRenderer';
import EmptyState from '../components/common/EmptyState';
import { uploadDocument, queryDocument } from '../services/uploadChatService';
import ConfirmationModal from '../components/common/ConfirmationModal';
import Toast from '../components/common/Toast';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';

const UploadChatArea = ({ refreshConversations }) => {
  const { t } = useTranslation();
  const { currentUser } = useAuth();
  const { language } = useLanguage();
  
  // File Upload State
  const [file, setFile] = useState(null);
  const [documentMetadata, setDocumentMetadata] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  // Chat State
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [chatError, setChatError] = useState(null);
  
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

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setUploadError("");
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    const ext = file.name.split('.').pop().toLowerCase();
    if (ext !== 'pdf' && ext !== 'docx') {
      setUploadError(t('uploadChat.errors.unsupportedFile'));
      return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
      setUploadError(t('uploadChat.errors.sizeLimit'));
      return;
    }

    setUploading(true);
    setUploadError("");

    try {
      const token = await currentUser.getIdToken();
      const response = await uploadDocument(token, file);
      setDocumentMetadata(response);
      
      // Clear current chat when a new document is uploaded
      setActiveConversationId(null);
      setMessages([]);
    } catch (err) {
      setUploadError(err.message || t('uploadChat.errors.uploadFailed'));
    } finally {
      setUploading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isGenerating || !documentMetadata) return;
    
    const userMessage = { role: 'user', content: inputValue.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsGenerating(true);
    setChatError(null);
    
    abortControllerRef.current = new AbortController();
    
    try {
      const token = await currentUser.getIdToken();
      const response = await queryDocument(
        token, 
        documentMetadata.document_id, 
        userMessage.content, 
        activeConversationId, 
        abortControllerRef.current.signal,
        language
      );
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: JSON.stringify(response)
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
        setChatError(err.message || t('uploadChat.errors.queryFailed'));
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handleNewChat = () => {
    setActiveConversationId(null);
    setMessages([]);
    setInputValue('');
    setChatError(null);
    setDocumentMetadata(null); // Return to upload screen
    setFile(null);
  };

  const handleSelectConversation = (conv) => {
    setActiveConversationId(conv.id);
    if (conv.document_id) {
      setDocumentMetadata({
        document_id: conv.document_id,
        filename: conv.document?.filename || "Previously Uploaded Document",
        pages: conv.document?.pages || "?",
        summary: conv.document?.summary || "Loaded from history."
      });
    }
  };

  const handleMessagesLoaded = (loadedMessages) => {
    setMessages(loadedMessages);
  };

  return (
    <ConversationLayout
      featureType="upload_chat"
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
              <FileUp className="w-4 h-4 text-amber" />
            </div>
            <div>
              <span className="label-stamp text-ink-fog block">{t('uploadChat.subtitle')}</span>
              <h1 className="text-[15px] font-semibold text-ink leading-tight" style={{ fontFamily: 'Newsreader, Georgia, serif' }}>
                {documentMetadata ? documentMetadata.filename : t('uploadChat.title')}
              </h1>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto bg-paper-warm/30 relative scroll-smooth">
          {!documentMetadata ? (
            <div className="h-full flex items-center justify-center p-6">
              <div className="max-w-md w-full">
                {/* Icon + heading via shared pattern */}
                <div className="flex flex-col items-center text-center mb-6">
                  <div className="w-14 h-14 bg-paper border border-paper-rule rounded-[4px] flex items-center justify-center mb-6 shadow-[0_1px_3px_rgba(26,24,20,0.06)]">
                    <UploadCloud className="w-6 h-6 text-accent" />
                  </div>
                  <span className="text-[12px] font-bold uppercase tracking-[0.12em] text-ink-muted mb-3 block">{t('uploadChat.emptyState.eyebrow')}</span>
                  <h2 className="text-[22px] font-bold text-ink mb-2 leading-tight" style={{ fontFamily: 'Newsreader, Georgia, serif' }}>
                    {t('uploadChat.emptyState.titleLine1')}<br /><span className="italic font-normal">{t('uploadChat.emptyState.titleLine2')}</span>
                  </h2>
                  <p className="text-[13px] text-ink-muted leading-relaxed">{t('uploadChat.emptyState.subtitle')}</p>
                </div>

                {/* Upload zone with drag-and-drop */}
                <div 
                  onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                  onDragLeave={() => setIsDragging(false)}
                  onDrop={(e) => {
                    e.preventDefault();
                    setIsDragging(false);
                    const droppedFile = e.dataTransfer.files[0];
                    if (droppedFile) {
                      setFile(droppedFile);
                      setUploadError("");
                    }
                  }}
                  className={`border-2 rounded-[4px] p-6 transition-all duration-200 ${
                    isDragging 
                      ? 'border-accent bg-accent/10 shadow-md scale-[1.01]' 
                      : 'border-dashed border-rule-strong hover:border-accent bg-white'
                  }`}
                >
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    accept=".pdf,.docx"
                    className="hidden"
                  />

                  {uploading ? (
                    <div className="text-center py-4 space-y-3 animate-stamp">
                      <div className="w-10 h-10 border-2 border-accent border-t-transparent rounded-full animate-spin mx-auto" />
                      <div className="space-y-1">
                        <p className="font-mono text-xs font-bold text-accent uppercase">
                          {t('uploadChat.processing')}
                        </p>
                        <p className="text-[12px] text-ink-muted">{t('uploadChat.extracting')}</p>
                      </div>
                      <div className="w-full bg-paper-sunken h-1.5 rounded-full overflow-hidden max-w-[200px] mx-auto">
                        <div className="h-full bg-accent animate-pulse w-3/4 rounded-full" />
                      </div>
                    </div>
                  ) : file ? (
                    <div className="text-center space-y-3">
                      <p className="text-[12px] font-medium text-accent-text bg-accent-wash inline-block px-3 py-1 rounded-[3px] border border-accent/30 font-mono">
                        {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </p>
                      <div className="flex gap-2 justify-center">
                        <button
                          onClick={() => fileInputRef.current?.click()}
                          disabled={uploading}
                          className="px-4 py-2 bg-paper-sunken border border-rule-strong text-ink rounded-[3px] hover:border-dark font-medium text-[13px] transition-colors cursor-pointer"
                        >
                          {t('uploadChat.changeBtn')}
                        </button>
                        <button
                          onClick={handleUpload}
                          disabled={uploading}
                          className="px-5 py-2 bg-dark hover:bg-dark-rule text-white rounded-[3px] font-semibold text-[13px] transition-colors disabled:opacity-60 flex items-center gap-2 cursor-pointer shadow-xs"
                        >{t('uploadChat.uploadBtn')}</button>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center space-y-2">
                      <button
                        onClick={() => fileInputRef.current?.click()}
                        disabled={uploading}
                        className="px-6 py-2.5 bg-dark hover:bg-dark-rule text-white rounded-[3px] font-semibold text-[13px] transition-colors cursor-pointer shadow-xs"
                      >{t('uploadChat.selectFileBtn')}</button>
                      <p className="text-[12px] text-ink-muted">{t('uploadChat.dragDrop')}</p>
                    </div>
                  )}

                  {uploadError && (
                    <p className="text-accent-text text-[13px] mt-4 bg-accent-wash py-2 px-3 rounded-[3px] border border-accent-hover/30 text-center font-medium">
                      {uploadError}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="pb-32">
              {messages.map((msg, idx) => (
                <MessageBubble 
                  key={idx} 
                  message={msg} 
                  renderContent={msg.role === 'assistant' ? (content) => <UploadChatRenderer content={content} /> : null}
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
                      <span className="text-[12px] text-ink-fog uppercase tracking-wider ml-1">{t('uploadChat.analysing')}</span>
                    </div>
                  )}
                />
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area (Only visible when document is uploaded) */}
        {documentMetadata && (
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-paper via-paper/90 to-transparent pt-10 pb-6 px-4 md:px-8 z-10 pointer-events-none">
            <div className="max-w-4xl mx-auto w-full pointer-events-auto">
              {chatError && (
                <div className="mb-4 p-3 bg-error-bg border border-error/30 rounded-card flex items-center gap-2 text-error text-[13px] shadow-stamp">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  {chatError}
                </div>
              )}
              <ChatInput 
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onSubmit={handleSendMessage}
                isLoading={isGenerating}
                placeholder={t('uploadChat.placeholder')}
              />
            </div>
          </div>
        )}
      </div>
    </ConversationLayout>
  );
};

const UploadChat = () => {
  return (
    <WorkspaceContainer>
      <UploadChatArea />
    </WorkspaceContainer>
  );
};

export default UploadChat;
