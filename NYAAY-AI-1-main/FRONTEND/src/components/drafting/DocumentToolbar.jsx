import React from 'react';
import { 
  ArrowLeft, 
  Settings, 
  Minus, 
  Plus, 
  Maximize, 
  Printer, 
  FileText, 
  Copy, 
  Edit3 
} from 'lucide-react';
import { WATERMARK_OPTIONS, LETTERHEAD_TEMPLATES } from './templates/index';
import { useTranslation } from 'react-i18next';

/**
 * DocumentToolbar — sticky PDF-viewer-style toolbar.
 * Modelled on Adobe Reader / Microsoft Word top bar.
 *
 * Layout:
 *   [ ← Back ] | [ Template ▾ ] [ Watermark ▾ ] [ ⚙ ] | [ − ] XX% [ + ] [ ⛶ ] | [ 🖨 ] [ PDF ] [ DOCX ] | [ ✂ Copy ] [ ✎ Edit ] [ ↩ Over ]
 */
export default function DocumentToolbar({
  draftResult,
  zoom,           onZoomChange,
  watermark,      onWatermarkChange,
  template,       onTemplateChange,
  onLetterheadOpen,
  onPrint,
  onDownloadPdf,
  onDownloadDocx,
  onCopyText,
  onEditToggle,   isEditing,
  onStartOver,
  onFullscreen,
}) {
  const { t } = useTranslation();
  const zoomPct = Math.round(zoom * 100);

  return (
    <div className="no-print sticky top-0 z-20 bg-dark-rule text-white px-4 py-2 flex flex-wrap items-center gap-2 shadow-lg select-none">

      {/* ── Back ──────────────────────────── */}
      <button onClick={onStartOver} className="toolbar-btn toolbar-btn--text flex items-center gap-1.5" title={t('drafting.startOver', 'Start Over')}>
        <ArrowLeft className="w-4 h-4" />
        <span className="hidden sm:inline text-xs">{t('drafting.back', 'Back')}</span>
      </button>

      <div className="toolbar-divider" />

      {/* ── Document info ─────────────────── */}
      <span className="text-xs text-slate hidden md:block truncate max-w-[200px]">
        {draftResult?.document_type?.replace(/_/g, ' ')} · v{draftResult?.metadata?.version || 1}
      </span>

      <div className="toolbar-divider" />

      {/* ── Template ──────────────────────── */}
      <label className="text-xs text-slate-muted hidden sm:block">{t('drafting.template', 'Template')}</label>
      <select
        value={template}
        onChange={e => onTemplateChange(e.target.value)}
        className="toolbar-select"
        title={t('drafting.selectTemplate', 'Select letterhead template')}
      >
        {LETTERHEAD_TEMPLATES.map(t => (
          <option key={t.id} value={t.id}>{t.label}</option>
        ))}
      </select>

      {/* ── Watermark ─────────────────────── */}
      <label className="text-xs text-slate-muted hidden sm:block">{t('drafting.watermark', 'Watermark')}</label>
      <select
        value={watermark}
        onChange={e => onWatermarkChange(e.target.value)}
        className="toolbar-select"
        title={t('drafting.selectWatermark', 'Select watermark')}
      >
        {WATERMARK_OPTIONS.map(w => (
          <option key={w.id} value={w.id}>{w.label}</option>
        ))}
      </select>

      {/* ── Letterhead Settings ───────────── */}
      <button onClick={onLetterheadOpen} className="toolbar-btn flex items-center justify-center" title={t('drafting.letterheadSettings', 'Letterhead Settings')}>
        <Settings className="w-4 h-4" />
      </button>

      <div className="toolbar-divider" />

      {/* ── Zoom ──────────────────────────── */}
      <button onClick={() => onZoomChange(Math.max(0.5, zoom - 0.1))} className="toolbar-btn flex items-center justify-center" title={t('drafting.zoomOut', 'Zoom out')}>
        <Minus className="w-4 h-4" />
      </button>
      <span className="text-xs w-10 text-center tabular-nums">{zoomPct}%</span>
      <button onClick={() => onZoomChange(Math.min(1.5, zoom + 0.1))} className="toolbar-btn flex items-center justify-center" title={t('drafting.zoomIn', 'Zoom in')}>
        <Plus className="w-4 h-4" />
      </button>

      {/* ── Fullscreen ────────────────────── */}
      <button onClick={onFullscreen} className="toolbar-btn flex items-center justify-center" title={t('drafting.fullscreen', 'Fullscreen')}>
        <Maximize className="w-4 h-4" />
      </button>

      <div className="toolbar-divider" />

      {/* ── Print ─────────────────────────── */}
      <button onClick={onPrint} className="toolbar-btn flex items-center gap-1.5" title={t('drafting.print', 'Print')}>
        <Printer className="w-4 h-4" />
        <span className="hidden sm:inline text-xs">{t('drafting.print', 'Print')}</span>
      </button>

      {/* ── PDF ───────────────────────────── */}
      <button onClick={onDownloadPdf} className="toolbar-btn toolbar-btn--pdf flex items-center gap-1.5" title={t('drafting.downloadPdf', 'Download PDF')}>
        <FileText className="w-4 h-4 text-accent" />
        <span className="hidden sm:inline text-xs">{t('drafting.pdf', 'PDF')}</span>
      </button>

      {/* ── DOCX ──────────────────────────── */}
      <button onClick={onDownloadDocx} className="toolbar-btn toolbar-btn--docx flex items-center gap-1.5" title={t('drafting.downloadDocx', 'Download DOCX')}>
        <FileText className="w-4 h-4 text-blue-400" />
        <span className="hidden sm:inline text-xs">{t('drafting.docx', 'DOCX')}</span>
      </button>

      <div className="toolbar-divider" />

      {/* ── Copy ──────────────────────────── */}
      <button onClick={onCopyText} className="toolbar-btn flex items-center gap-1.5" title={t('drafting.copyText', 'Copy text')}>
        <Copy className="w-4 h-4" />
        <span className="hidden sm:inline text-xs">{t('drafting.copy', 'Copy')}</span>
      </button>

      {/* ── Edit ──────────────────────────── */}
      <button
        onClick={onEditToggle}
        className={`toolbar-btn flex items-center gap-1.5 ${isEditing ? 'toolbar-btn--active' : ''}`}
        title={t('drafting.editDraft', 'Edit draft')}
      >
        <Edit3 className="w-4 h-4" />
        <span className="hidden sm:inline text-xs">{t('drafting.edit', 'Edit')}</span>
      </button>
    </div>
  );
}
