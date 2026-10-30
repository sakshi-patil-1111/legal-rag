import React, { useState, useMemo } from 'react';
import { Search, Plus, MessageSquare, MoreHorizontal, Pencil, Trash2, Pin } from 'lucide-react';
import { renameConversation, deleteConversation, pinConversation } from "../../services/chatService";
import { useAuth } from "../../contexts/AuthContext";
import ConfirmationModal from "../common/ConfirmationModal";
import Toast from "../common/Toast";
import { useTranslation } from 'react-i18next';

const ChatSidebar = ({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onConversationsChanged
}) => {
  const { t } = useTranslation();
  const { currentUser } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [menuOpenId, setMenuOpenId] = useState(null);
  /* Deleting a conversation is destructive and used to go through
     window.confirm(). Rename/pin/delete failures were also swallowed into
     console.error, so the row simply didn't change and the user was told
     nothing. */
  const [pendingDeleteId, setPendingDeleteId] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [toast, setToast] = useState(null);

  const reportFailure = (action) =>
    setToast({ variant: 'error', message: t('chatSidebar.failureMessage', { action }) });

  const filteredConversations = useMemo(() => {
    if (!searchQuery) return conversations;
    return conversations.filter(c => c.title.toLowerCase().includes(searchQuery.toLowerCase()));
  }, [conversations, searchQuery]);

  // Grouping logic
  const grouped = useMemo(() => {
    const groups = {
      pinned: [],
      today: [],
      yesterday: [],
      previous7Days: [],
      older: []
    };

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
    const yesterday = today - 86400000;
    const sevenDaysAgo = today - 86400000 * 7;

    filteredConversations.forEach(c => {
      if (c.is_pinned) { groups.pinned.push(c); return; }
      const updatedTime = new Date(c.updated_at).getTime();
      if (updatedTime >= today) groups.today.push(c);
      else if (updatedTime >= yesterday) groups.yesterday.push(c);
      else if (updatedTime >= sevenDaysAgo) groups.previous7Days.push(c);
      else groups.older.push(c);
    });
    return groups;
  }, [filteredConversations]);

  const handleRenameSubmit = async (id, e) => {
    e.preventDefault();
    if (!editTitle.trim()) return;
    try {
      const token = await currentUser.getIdToken();
      await renameConversation(token, id, editTitle);
      setEditingId(null);
      if (onConversationsChanged) onConversationsChanged();
    } catch (err) {
      console.error(err);
      setEditingId(null);
      reportFailure(t('chatSidebar.renameSession'));
    }
  };

  const confirmDelete = async () => {
    const id = pendingDeleteId;
    if (!id) return;
    setDeleting(true);
    try {
      const token = await currentUser.getIdToken();
      await deleteConversation(token, id);
      setMenuOpenId(null);
      setPendingDeleteId(null);
      if (onConversationsChanged) onConversationsChanged();
      if (activeConversationId === id) onNewChat();
    } catch (err) {
      console.error(err);
      setPendingDeleteId(null);
      reportFailure(t('chatSidebar.deleteSession'));
    } finally {
      setDeleting(false);
    }
  };

  const handleTogglePin = async (c) => {
    try {
      const token = await currentUser.getIdToken();
      await pinConversation(token, c.id, !c.is_pinned);
      setMenuOpenId(null);
      if (onConversationsChanged) onConversationsChanged();
    } catch (err) {
      console.error(err);
      reportFailure(c.is_pinned ? t('chatSidebar.unpinSession') : t('chatSidebar.pinSession'));
    }
  };

  const pendingDeleteTitle =
    conversations.find((c) => c.id === pendingDeleteId)?.title || t('chatSidebar.thisConversation');

  const renderGroup = (title, items) => {
    if (items.length === 0) return null;
    return (
      <div className="mb-5">
        <h3 className="label-stamp mb-2 px-3">{title}</h3>
        <div className="space-y-0.5">
          {items.map(c => (
            <div
              key={c.id}
              className={`group relative flex items-center gap-2.5 px-3 py-2.5 cursor-pointer transition-colors rounded-card ${
                activeConversationId === c.id
                  ? 'bg-amber-light border border-amber/30 text-ink'
                  : 'hover:bg-paper-warm text-ink-muted hover:text-ink border border-transparent'
              }`}
              onClick={() => { if (editingId !== c.id) onSelectConversation(c); }}
            >
              <MessageSquare size={14} className={activeConversationId === c.id ? 'text-amber' : 'text-ink-fog'} />

              {editingId === c.id ? (
                <form onSubmit={(e) => handleRenameSubmit(c.id, e)} className="flex-1 min-w-0" onClick={e => e.stopPropagation()}>
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onBlur={(e) => handleRenameSubmit(c.id, e)}
                    className="w-full bg-paper border border-amber rounded-stamp px-2 py-0.5 text-[13px] outline-none focus:ring-1 ring-amber/30 text-ink"
                    autoFocus
                  />
                </form>
              ) : (
                <span className="flex-1 min-w-0 truncate text-[13px] font-medium">
                  {c.title || t('chatSidebar.newConversation')}
                </span>
              )}

              {editingId !== c.id && (
                <div className={`relative ${menuOpenId === c.id ? 'block' : 'hidden group-hover:block'}`}>
                  <button
                    onClick={(e) => { e.stopPropagation(); setMenuOpenId(menuOpenId === c.id ? null : c.id); }}
                    className="p-1 text-ink-fog hover:text-ink hover:bg-paper-rule rounded-stamp transition-colors"
                  >
                    <MoreHorizontal size={14} />
                  </button>

                  {menuOpenId === c.id && (
                    <div className="absolute right-0 top-full mt-1 w-36 bg-paper border border-paper-rule rounded-card shadow-card z-50 py-1">
                      <button
                        onClick={(e) => { e.stopPropagation(); handleTogglePin(c); }}
                        className="w-full text-left px-3 py-1.5 text-[12px] text-ink hover:bg-paper-warm flex items-center gap-2 transition-colors"
                      >
                        <Pin size={12} /> {c.is_pinned ? t('chatSidebar.unpin') : t('chatSidebar.pin')}
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); setEditTitle(c.title); setEditingId(c.id); setMenuOpenId(null); }}
                        className="w-full text-left px-3 py-1.5 text-[12px] text-ink hover:bg-paper-warm flex items-center gap-2 transition-colors"
                      >
                        <Pencil size={12} /> {t('chatSidebar.rename')}
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); setPendingDeleteId(c.id); setMenuOpenId(null); }}
                        className="w-full text-left px-3 py-1.5 text-[12px] text-error hover:bg-error-bg flex items-center gap-2 transition-colors"
                      >
                        <Trash2 size={12} /> {t('chatSidebar.deleteAction')}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <>
    <div className="w-72 flex-shrink-0 bg-paper-warm border-r border-paper-rule flex flex-col h-full" onClick={() => setMenuOpenId(null)}>
      {/* Sidebar Header */}
      <div className="px-4 py-4 border-b border-paper-rule flex items-center justify-between bg-paper">
        <div>
          <span className="label-stamp block">{t('chatSidebar.caseHistory')}</span>
          <span className="text-[13px] font-semibold text-ink">{t('chatSidebar.pastSessions')}</span>
        </div>
        <button
          onClick={onNewChat}
          className="p-2 text-ink hover:bg-paper-warm border border-paper-rule rounded-button transition-colors shadow-stamp flex items-center justify-center"
          title="New Session"
        >
          <Plus size={16} />
        </button>
      </div>

      {/* Search */}
      <div className="px-3 py-3 border-b border-paper-rule">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-fog" size={13} />
          <input
            type="text"
            placeholder={t('chatSidebar.searchSessions')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-3 py-2 bg-paper border border-paper-rule rounded-button text-[13px] focus:outline-none focus:ring-1 focus:ring-amber focus:border-amber transition-all text-ink placeholder-ink-fog"
          />
        </div>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto p-3">
        {conversations.length === 0 ? (
          <div className="text-center mt-12 px-4">
            <span className="label-stamp block mb-2">{t('chatSidebar.noSessionsYet')}</span>
            <p className="text-[12px] text-ink-muted leading-relaxed">{t('chatSidebar.startNewQuery')}</p>
          </div>
        ) : filteredConversations.length === 0 ? (
          <div className="text-center mt-10">
            <p className="text-[12px] text-ink-muted">{t('chatSidebar.noMatches', { query: searchQuery })}</p>
          </div>
        ) : (
          <>
            {renderGroup(t('chatSidebar.pinned'), grouped.pinned)}
            {renderGroup(t('chatSidebar.today'), grouped.today)}
            {renderGroup(t('chatSidebar.yesterday'), grouped.yesterday)}
            {renderGroup(t('chatSidebar.previous7Days'), grouped.previous7Days)}
            {renderGroup(t('chatSidebar.older'), grouped.older)}
          </>
        )}
      </div>
    </div>

    <ConfirmationModal
      isOpen={!!pendingDeleteId}
      title={t('chatSidebar.deleteSessionTitle')}
      body={t('chatSidebar.deleteSessionBody', { title: pendingDeleteTitle })}
      confirmText={t('chatSidebar.delete')}
      cancelText={t('chatSidebar.keepIt')}
      isDestructive
      loading={deleting}
      onConfirm={confirmDelete}
      onCancel={() => setPendingDeleteId(null)}
    />

    <Toast
      isOpen={!!toast}
      message={toast?.message}
      variant={toast?.variant}
      duration={0}
      dismissible
      onClose={() => setToast(null)}
    />
    </>
  );
};

export default ChatSidebar;
