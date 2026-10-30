import React, { useRef, useState, useEffect, useCallback } from 'react';
import DocumentPage from './DocumentPage';

/**
 * DocumentCanvas — Adobe Acrobat-style document workspace.
 *
 * Renders one or more DocumentPage components in a dark-gray workspace.
 * Page count is estimated by body paragraph count (simple heuristic).
 * Zoom, fullscreen, and page count are managed here.
 *
 * Props:
 *   draftResult       — StructuredDocumentObject
 *   letterheadConfig  — saved letterhead settings
 *   watermark         — watermark string
 *   zoom              — zoom level (managed by parent toolbar)
 */
function calculateEstimatedHeight(node) {
  // Rough estimate of node height in pt.
  switch (node.type) {
    case 'title': return 40;
    case 'heading': return 30;
    case 'subject': return 50;
    case 'metadata_table': 
    case 'parties_table': 
      return Object.keys(node.content || {}).length * 20 + 20;
    case 'paragraph': 
    case 'numbered_paragraph': {
      const text = node.content.text || '';
      // Approx 80 characters per line, 24pt line height
      const lines = Math.ceil(text.length / 80);
      return (lines * 24) + 18; // plus margin-bottom
    }
    case 'signature_block': return 120;
    case 'verification_block': return 150;
    case 'annexure_list': 
      return (node.content.items?.length || 0) * 30 + 30;
    case 'page_break': return 9999; // Force new page
    case 'spacer': return 20;
    default: return 20;
  }
}

export default function DocumentCanvas({ draftResult, letterheadConfig, watermark, zoom }) {
  const workspaceRef = useRef(null);

  const nodes = draftResult?.layout_model?.nodes || [];
  
  // A standard A4 page is ~297mm height. With 1-inch margins, usable height is ~9.69 inches (~700pt).
  const PAGE_HEIGHT_PT = 650;
  
  const pages = [];
  let currentPage = [];
  let currentHeight = 0;

  nodes.forEach((node) => {
    const nodeHeight = calculateEstimatedHeight(node);
    if (node.type === 'page_break') {
      pages.push(currentPage);
      currentPage = [];
      currentHeight = 0;
    } else if (currentHeight + nodeHeight > PAGE_HEIGHT_PT && currentPage.length > 0) {
      pages.push(currentPage);
      currentPage = [node];
      currentHeight = nodeHeight;
    } else {
      currentPage.push(node);
      currentHeight += nodeHeight;
    }
  });
  
  if (currentPage.length > 0 || pages.length === 0) {
    pages.push(currentPage);
  }

  const totalPages = Math.max(1, pages.length);

  return (
    <div
      ref={workspaceRef}
      className="legal-workspace"
      id="legal-workspace"
    >
      {pages.map((pageNodes, idx) => {
        const pageNum = idx + 1;
        const pageAST = { nodes: pageNodes };
        return (
          <div
            key={pageNum}
            className="legal-page-wrapper"
            style={{ marginBottom: pageNum < totalPages ? '24px' : '0' }}
          >
            <DocumentPage
              draftResult={draftResult}
              layoutAST={pageAST}
              letterheadConfig={letterheadConfig}
              watermark={watermark}
              zoom={zoom}
              pageNumber={pageNum}
              totalPages={totalPages}
              isFirstPage={pageNum === 1}
              isLastPage={pageNum === totalPages}
            />
          </div>
        );
      })}
    </div>
  );
}
