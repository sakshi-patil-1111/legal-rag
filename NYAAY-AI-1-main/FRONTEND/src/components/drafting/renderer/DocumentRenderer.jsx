import React from 'react';
import './DocumentRenderer.css';
import { useTranslation } from 'react-i18next';

// === Rendering Rules ===
// These match the backend rules exactly to ensure pagination parity
const RENDERING_RULES = {
  fontFamily: '"Times New Roman", Times, serif',
  fontSize: '12pt',
  lineHeight: '24pt', // 2x line-height equivalent
  headingFontSize: '14pt',
  margin: '1in',
};

// === Universal Blocks ===

const MetadataTable = ({ data }) => (
  <table className="ast-metadata-table">
    <tbody>
      {Object.entries(data).map(([key, value]) => (
        <tr key={key}>
          <td className="ast-metadata-label">{key.replace(/_/g, ' ').toUpperCase()}:</td>
          <td className="ast-metadata-value">{value}</td>
        </tr>
      ))}
    </tbody>
  </table>
);

const PartiesTable = ({ data }) => (
  <table className="ast-parties-table">
    <tbody>
      {Object.entries(data).map(([key, value]) => (
        <tr key={key}>
          <td className="ast-metadata-label">{key}:</td>
          <td className="ast-metadata-value">{value}</td>
        </tr>
      ))}
    </tbody>
  </table>
);

const NumberedParagraph = ({ num, text }) => (
  <div className="ast-numbered-paragraph">
    <span className="ast-number">{num}.</span>
    <span className="ast-text">{text}</span>
  </div>
);

const SignatureBlock = ({ closing, signatures }) => (
  <div className="ast-signature-block">
    {closing && <p className="ast-closing">{closing}</p>}
    {signatures.map((sig, idx) => (
      <div key={idx} className="ast-signature-unit">
        {sig.name && <p className="ast-signature-name">({sig.name})</p>}
        <p className="ast-signature-role">{sig.role}</p>
      </div>
    ))}
  </div>
);

const VerificationBlock = ({ text, place, date }) => {
  const { t } = useTranslation();
  return (
    <div className="ast-verification-block">
      <h2 className="ast-heading" style={{ fontSize: RENDERING_RULES.fontSize }}>{t('docHub.document.verification')}</h2>
      <p className="ast-paragraph">{text}</p>
      <p className="ast-paragraph">{t('docHub.document.date')} {date}</p>
      <p className="ast-paragraph">{t('docHub.document.place')} {place}</p>
    </div>
  );
};

// === Helper to parse inline markdown bold ===
const parseBoldText = (text) => {
  if (!text) return null;
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
};

// === AST Renderer Engine ===

export default function DocumentRenderer({ layoutAST }) {
  const { t } = useTranslation();
  
  if (!layoutAST || !layoutAST.nodes) return null;

  return (
    <div className="ast-document-canvas" style={{
      fontFamily: RENDERING_RULES.fontFamily,
      fontSize: RENDERING_RULES.fontSize,
      lineHeight: RENDERING_RULES.lineHeight,
      padding: RENDERING_RULES.margin,
    }}>
      {layoutAST.nodes.map((node) => {
        switch (node.type) {
          case 'title':
            return (
              <h2 key={node.id} className="ast-title" style={{ fontSize: RENDERING_RULES.headingFontSize }}>
                {node.content.text}
              </h2>
            );

          case 'heading':
            return (
              <h2 key={node.id} className="ast-heading">
                {node.content.text}
              </h2>
            );
          
          case 'subject':
            return (
              <p key={node.id} className="ast-subject">
                <strong>{t('docHub.document.subject')}: {node.content.text}</strong>
              </p>
            );

          case 'metadata_table':
            return <MetadataTable key={node.id} data={node.content} />;

          case 'parties_table':
            return <PartiesTable key={node.id} data={node.content} />;

          case 'paragraph':
            return (
              <p 
                key={node.id} 
                className="ast-paragraph" 
                style={{ fontWeight: node.metadata?.bold ? 'bold' : 'normal' }}
              >
                {/* Parse newlines as React breaks and apply bold parsing */}
                {(node.content.text || '').split('\n').map((line, i, lines) => (
                  <React.Fragment key={i}>
                    {parseBoldText(line)}
                    {i < lines.length - 1 && <br />}
                  </React.Fragment>
                ))}
              </p>
            );

          case 'numbered_paragraph':
            return <NumberedParagraph key={node.id} num={node.content.number} text={parseBoldText(node.content.text)} />;

          case 'signature_block':
            return <SignatureBlock key={node.id} closing={node.content.closing} signatures={node.content.signatures} />;

          case 'verification_block':
            return <VerificationBlock key={node.id} {...node.content} />;

          case 'annexure_list':
            return (
              <table key={node.id} className="ast-annexure-table">
                <tbody>
                  {node.content.items.map((item, idx) => (
                    <tr key={idx}>
                      <td className="ast-annexure-label">{item.label}</td>
                      <td className="ast-annexure-value">{item.desc}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            );

          case 'page_break':
            return <div key={node.id} className="ast-page-break" />;

          case 'spacer':
            return <div key={node.id} style={{ height: node.content.height || '16pt' }} />;

          default:
            console.warn(`Unknown block type: ${node.type}`);
            return null;
        }
      })}
    </div>
  );
}
