/**
 * NYAAY AI — Drafting Engine Template Registry
 * 
 * Each entry defines per-document-type behaviour:
 *  - hasRefNumber: whether to render Ref No. row
 *  - hasDate:      whether to render Date row on the header
 *  - component:    which template component to use for body layout
 *  - refLabel:     label for the reference field
 *
 * Court-specific templates (High Court, District Court, Consumer Commission,
 * RERA, Tribunal) are stubbed here for future extension.
 */

export const DOCUMENT_TEMPLATE_META = {
  LEGAL_NOTICE:       { hasRefNumber: true,  hasDate: true,  refLabel: 'Ref. No.' },
  AFFIDAVIT:          { hasRefNumber: false, hasDate: true,  refLabel: null },
  PLAINT:             { hasRefNumber: true,  hasDate: true,  refLabel: 'Suit No.' },
  BAIL_APPLICATION:   { hasRefNumber: true,  hasDate: true,  refLabel: 'Application No.' },
  CONSUMER_COMPLAINT: { hasRefNumber: false, hasDate: true,  refLabel: null },
  RTI_APPLICATION:    { hasRefNumber: true,  hasDate: true,  refLabel: 'Ref. No.' },
  POLICE_COMPLAINT:   { hasRefNumber: false, hasDate: true,  refLabel: null },
  SP_COMPLAINT:       { hasRefNumber: true,  hasDate: true,  refLabel: 'Ref. No.' },
  REPRESENTATION:     { hasRefNumber: true,  hasDate: true,  refLabel: 'Ref. No.' },
  DECLARATION:        { hasRefNumber: false, hasDate: true,  refLabel: null },
  INDEMNITY_BOND:     { hasRefNumber: false, hasDate: true,  refLabel: null },
  POWER_OF_ATTORNEY:  { hasRefNumber: false, hasDate: true,  refLabel: null },

  // Future court-specific stubs
  // HIGH_COURT_PETITION:        { hasRefNumber: true, hasDate: true, refLabel: 'W.P. No.' },
  // DISTRICT_COURT_APPLICATION: { hasRefNumber: true, hasDate: true, refLabel: 'Civil Misc. No.' },
  // CONSUMER_COMMISSION_COMPLAINT: { hasRefNumber: true, hasDate: true, refLabel: 'Complaint No.' },
  // RERA_COMPLAINT:             { hasRefNumber: true, hasDate: true, refLabel: 'Complaint No.' },
  // TRIBUNAL_APPLICATION:       { hasRefNumber: true, hasDate: true, refLabel: 'Application No.' },
};

export const getTemplateMeta = (documentType) =>
  DOCUMENT_TEMPLATE_META[documentType] ?? { hasRefNumber: false, hasDate: true, refLabel: null };

/**
 * Letterhead templates — only change presentation (header/footer).
 * Content is always identical regardless of template selected.
 */
export const LETTERHEAD_TEMPLATES = [
  { id: 'plain',     label: 'Plain Court Filing' },
  { id: 'advocate', label: 'Advocate Chamber' },
  { id: 'law_firm', label: 'Law Firm' },
  { id: 'corporate', label: 'Corporate Legal' },
  { id: 'personal', label: 'Personal Notice' },
];

export const WATERMARK_OPTIONS = [
  { id: 'NONE',        label: 'None' },
  { id: 'DRAFT',       label: 'DRAFT',        color: '#6B7280' },
  { id: 'CONFIDENTIAL', label: 'CONFIDENTIAL', color: '#DC2626' },
  { id: 'FINAL',       label: 'FINAL',         color: '#16A34A' },
  { id: 'CLIENT COPY', label: 'CLIENT COPY',   color: '#2563EB' },
];

export const RIBBON_COLORS = {
  DRAFT:        { bg: '#6B7280', text: '#fff' },
  CONFIDENTIAL: { bg: '#DC2626', text: '#fff' },
  FINAL:        { bg: '#16A34A', text: '#fff' },
  'CLIENT COPY': { bg: '#2563EB', text: '#fff' },
};

/** Default letterhead config stored in localStorage */
export const DEFAULT_LETTERHEAD_CONFIG = {
  mode: 'plain',
  name: '',
  line2: '',
  address: '',
  contact: '',
  enrollmentNo: '',
  logoSrc: null,          // reserved for future upload feature
  preferredTemplate: 'plain',
  preferredWatermark: 'NONE',
  refNumberMode: 'auto',  // 'auto' | 'manual' | 'hidden'
  manualRefNumber: '',
  showDraftVersion: false,
};
