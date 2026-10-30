import React from 'react';
import { Gavel } from 'lucide-react';
import { getTemplateMeta, RIBBON_COLORS } from './templates/index';
import DocumentRenderer from './renderer/DocumentRenderer';
import { useTranslation } from 'react-i18next';

/**
 * Generates a stable reference number for a draft session.
 * Format: NYAAY-YYYY-XXXXXX (6-digit random, stable per draftResult instance)
 */
function generateRefNumber(seed) {
  const year = new Date().getFullYear();
  const num  = String(Math.abs(hashCode(seed)) % 1000000).padStart(6, '0');
  return `NYAAY-${year}-${num}`;
}
function hashCode(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) { h = Math.imul(31, h) + str.charCodeAt(i) | 0; }
  return h;
}

/**
 * DocumentPage — renders a single A4 page with letterhead, watermark, status ribbon,
 * content body (via document-type template), and footer.
 *
 * Props:
 *   draftResult       — StructuredDocumentObject
 *   letterheadConfig  — from localStorage
 *   watermark         — 'NONE' | 'DRAFT' | 'CONFIDENTIAL' | 'FINAL' | 'CLIENT COPY'
 *   zoom              — number (0.5–1.5)
 *   pageNumber        — current page (1-indexed)
 *   totalPages        — total page count
 *   isFirstPage       — boolean (renders status ribbon only on first page)
 *   pageContent       — the slice of content for this page (passed by DocumentCanvas)
 *   isLastPage        — boolean
 */
export default function DocumentPage({
  draftResult,
  letterheadConfig,
  watermark,
  zoom = 1,
  pageNumber,
  totalPages,
  isFirstPage,
  isLastPage,
  layoutAST,
}) {
  const { t } = useTranslation();
  const ribbonColor = watermark !== 'NONE' ? RIBBON_COLORS[watermark] : null;

  return (
    <div
      id={isFirstPage ? 'legal-document-canvas' : undefined}
      className="legal-page"
      style={{ transform: `scale(${zoom})`, transformOrigin: 'top center' }}
    >

      {/* === WATERMARK === */}
      {watermark !== 'NONE' && (
        <div className="legal-watermark" aria-hidden="true">
          {watermark}
        </div>
      )}

      {/* === STATUS RIBBON (first page only) === */}
      {isFirstPage && watermark !== 'NONE' && ribbonColor && (
        <div className="legal-ribbon-anchor" aria-hidden="true">
          <div
            className="legal-ribbon"
            style={{ backgroundColor: ribbonColor.bg, color: ribbonColor.text }}
          >
            {watermark}
          </div>
        </div>
      )}

      {/* === CLASSIFICATION HEADER (first page only) === */}
      {isFirstPage && draftResult?.metadata?.classification && (
        <div style={{ textAlign: 'right', fontWeight: 'bold', fontSize: '10pt', marginBottom: '10pt' }}>
          {draftResult.metadata.classification.toUpperCase()}
        </div>
      )}

      {/* === LETTERHEAD HEADER === */}
      <LetterheadHeader config={letterheadConfig} docType={draftResult?.document_type} />

      {/* === DOCUMENT BODY === */}
      {/* === DOCUMENT BODY === */}
      {layoutAST ? (
        <DocumentRenderer layoutAST={layoutAST} />
      ) : (
        <p style={{ textAlign: 'center', color: '#666', marginTop: '40pt' }}>{t('drafting.noLayoutAST', 'No layout AST provided.')}</p>
      )}

      {/* === FOOTER === */}
      <div className="legal-page-footer">
        <hr className="legal-footer-rule" />
        <div className="legal-footer-content">
          <span>{t('drafting.pageOf', { page: pageNumber, total: totalPages, defaultValue: `Page ${pageNumber} of ${totalPages}` })}</span>
        </div>
      </div>
    </div>
  );
}

/* ─── Letterhead Header ─────────────────────────────────────────────────────── */
function LetterheadHeader({ config, docType }) {
  const { t } = useTranslation();
  const mode = config?.mode ?? 'plain';

  /* Affidavits never show a letterhead */
  if (docType === 'AFFIDAVIT') return null;
  if (mode === 'plain') return <div className="legal-header-rule" />;

  return (
    <div className="legal-letterhead">
      {/* Logo placeholder — replaced with <img> when config.logoSrc is set */}
      {(mode === 'law_firm' || mode === 'corporate') && (
        <div className="legal-logo-placeholder">
          {config?.logoSrc
            ? <img src={config.logoSrc} alt="Firm Logo" className="legal-logo-img" />
            : <Gavel className="w-8 h-8 text-ink-muted inline-block" />
          }
        </div>
      )}

      <div className="legal-letterhead-text">
        {config?.name && <p className="legal-letterhead-name">{config.name}</p>}
        {config?.line2 && <p className="legal-letterhead-line2">{config.line2}</p>}
        {mode === 'advocate' && config?.enrollmentNo && (
          <p className="legal-letterhead-meta">{t('drafting.enrollmentNo', { no: config.enrollmentNo, defaultValue: `Enrol. No.: ${config.enrollmentNo}` })}</p>
        )}
        {config?.address && <p className="legal-letterhead-meta">{config.address}</p>}
        {config?.contact && <p className="legal-letterhead-meta">{config.contact}</p>}
      </div>

      <div className="legal-header-rule" />
    </div>
  );
}
