import React, { useState, useEffect, useCallback } from 'react';
import ChatSidebar from './ChatSidebar';
import { getConversations, getMessages } from '../../services/chatService';
import { useAuth } from '../../contexts/AuthContext';
import { Menu, X } from 'lucide-react';

const ConversationLayout = ({
  featureType,
  onSelectConversation,
  activeConversationId,
  onNewChat,
  children,
  onMessagesLoaded
}) => {
  const { currentUser } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const fetchConversations = useCallback(async () => {
    if (!currentUser) return;
    try {
      setLoading(true);
      const token = await currentUser.getIdToken();
      const data = await getConversations(token, featureType);
      setConversations(data.conversations || []);
    } catch (error) {
      console.error("Failed to load conversations", error);
    } finally {
      setLoading(false);
    }
  }, [currentUser, featureType]);

  useEffect(() => {
    fetchConversations();
  }, [fetchConversations, activeConversationId]);

  const handleSelectConversation = async (conv) => {
    onSelectConversation(conv);
    if (onMessagesLoaded) {
      try {
        const token = await currentUser.getIdToken();
        const data = await getMessages(token, conv.id);
        onMessagesLoaded(data.messages || [], conv);
      } catch (err) {
        console.error("Failed to load messages", err);
      }
    }
  };

  return (
    <div className="flex h-full w-full bg-paper overflow-hidden relative">
      {/* Mobile open sidebar button */}
      {!sidebarOpen && (
        <button
          onClick={() => setSidebarOpen(true)}
          className="md:hidden absolute top-4 left-4 z-20 p-2 bg-paper border border-paper-rule rounded-button shadow-stamp text-ink-muted hover:text-ink transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-amber"
        >
          <Menu size={18} />
        </button>
      )}

      {/* Sidebar Container */}
      <div
        className={`absolute md:relative z-30 h-full transition-transform duration-200 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0 md:w-0 md:overflow-hidden'
        }`}
      >
        <ChatSidebar
          conversations={conversations}
          activeConversationId={activeConversationId}
          onSelectConversation={handleSelectConversation}
          onNewChat={onNewChat}
          onConversationsChanged={fetchConversations}
        />
        <button
          className="md:hidden absolute top-4 right-4 text-ink-muted hover:text-ink transition-colors"
          onClick={() => setSidebarOpen(false)}
        >
          <X size={18} />
        </button>
      </div>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="md:hidden fixed inset-0 bg-ink/20 z-20"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0 bg-paper relative h-full">
        {children}
      </div>
    </div>
  );
};

export default ConversationLayout;
