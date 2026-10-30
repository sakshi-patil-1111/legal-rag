import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { LETTERHEAD_TEMPLATES, WATERMARK_OPTIONS, DEFAULT_LETTERHEAD_CONFIG } from './templates/index';
import { useTranslation } from 'react-i18next';

const LS_KEY = 'nyaay_letterhead_config';

export function useLetterheadConfig() {
  const [config, setConfig] = useState(() => {
    try {
      const stored = localStorage.getItem(LS_KEY);
      return stored ? { ...DEFAULT_LETTERHEAD_CONFIG, ...JSON.parse(stored) } : DEFAULT_LETTERHEAD_CONFIG;
    } catch { return DEFAULT_LETTERHEAD_CONFIG; }
  });

  const save = (updated) => {
    const merged = { ...config, ...updated };
    setConfig(merged);
    localStorage.setItem(LS_KEY, JSON.stringify(merged));
  };

  return [config, save];
}

/**
 * LetterheadSettingsModal — opened from the toolbar gear icon.
 * Saves all settings to localStorage. Never asked per-draft.
 */
export default function LetterheadSettingsModal({ isOpen, onClose, config, onSave }) {
  const { t } = useTranslation();
  const [local, setLocal] = useState(config);
  useEffect(() => { setLocal(config); }, [config, isOpen]);

  if (!isOpen) return null;

  const update = (key, val) => setLocal(prev => ({ ...prev, [key]: val }));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={onClose}>
      <div
        className="bg-surface rounded-lg shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-200">
          <h2 className="font-semibold text-base">{t('drafting.letterheadModalTitle', 'Letterhead & Document Settings')}</h2>
          <button onClick={onClose} className="p-1 rounded text-ink-muted hover:text-ink hover:bg-paper-sunken transition-colors" title={t('drafting.close', 'Close')}>
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="px-6 py-5 space-y-5">

          {/* Mode */}
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-zinc-500 block mb-2">
              {t('drafting.letterheadMode', 'Letterhead Mode')}
            </label>
            <div className="grid grid-cols-2 gap-2">
              {LETTERHEAD_TEMPLATES.map(tOption => (
                <button
                  key={tOption.id}
                  onClick={() => update('mode', tOption.id)}
                  className={`text-sm px-3 py-2 rounded border transition-all ${
                    local.mode === tOption.id
                      ? 'border-primary-hover bg-primary-hover text-white'
                      : 'border-zinc-300 hover:border-zinc-500'
                  }`}
                >
                  {tOption.label}
                </button>
              ))}
            </div>
          </div>

          {/* Name */}
          {local.mode !== 'plain' && (
            <>
              <Field label={t('drafting.nameFirmName', 'Name / Firm Name')} value={local.name} onChange={v => update('name', v)} placeholder={t('drafting.namePlaceholder', 'e.g. Adv. Ramesh Sharma / Sharma & Associates')} />
              <Field label={t('drafting.line2', 'Line 2 (Designation / Specialisation)')} value={local.line2} onChange={v => update('line2', v)} placeholder={t('drafting.line2Placeholder', 'e.g. Advocates & Legal Consultants')} />
              {local.mode === 'advocate' && (
                <Field label={t('drafting.enrollmentNoLabel', 'Enrollment Number')} value={local.enrollmentNo} onChange={v => update('enrollmentNo', v)} placeholder={t('drafting.enrollmentPlaceholder', 'e.g. MH/1234/2015')} />
              )}
              <Field label={t('drafting.address', 'Address')} value={local.address} onChange={v => update('address', v)} placeholder={t('drafting.addressPlaceholder', 'Chamber / Office Address')} />
              <Field label={t('drafting.contact', 'Contact (Phone / Email)')} value={local.contact} onChange={v => update('contact', v)} placeholder={t('drafting.contactPlaceholder', '+91 98765 43210 | advocate@email.com')} />
            </>
          )}

          <hr className="border-zinc-200" />

          {/* Reference Number Mode */}
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-zinc-500 block mb-2">
              {t('drafting.refNumber', 'Reference Number')}
            </label>
            <div className="flex gap-3">
              {[
                { id: 'auto',   label: t('drafting.autoGenerate', 'Auto-generate') },
                { id: 'manual', label: t('drafting.manual', 'Manual') },
                { id: 'hidden', label: t('drafting.hide', 'Hide') },
              ].map(opt => (
                <label key={opt.id} className="flex items-center gap-1.5 text-sm cursor-pointer">
                  <input
                    type="radio"
                    name="refMode"
                    value={opt.id}
                    checked={local.refNumberMode === opt.id}
                    onChange={() => update('refNumberMode', opt.id)}
                    className="accent-primary-hover"
                  />
                  {opt.label}
                </label>
              ))}
            </div>
            {local.refNumberMode === 'manual' && (
              <Field label="" value={local.manualRefNumber} onChange={v => update('manualRefNumber', v)} placeholder={t('drafting.refPlaceholder', 'e.g. FIRM/LN/2026/001')} />
            )}
          </div>

          <hr className="border-zinc-200" />

          {/* Default Template */}
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-zinc-500 block mb-2">
              {t('drafting.defaultTemplate', 'Default Template')}
            </label>
            <select
              value={local.preferredTemplate}
              onChange={e => update('preferredTemplate', e.target.value)}
              className="w-full border border-zinc-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-zinc-600"
            >
              {LETTERHEAD_TEMPLATES.map(tOption => (
                <option key={tOption.id} value={tOption.id}>{tOption.label}</option>
              ))}
            </select>
          </div>

          {/* Default Watermark */}
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-zinc-500 block mb-2">
              {t('drafting.defaultWatermark', 'Default Watermark')}
            </label>
            <select
              value={local.preferredWatermark}
              onChange={e => update('preferredWatermark', e.target.value)}
              className="w-full border border-zinc-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-zinc-600"
            >
              {WATERMARK_OPTIONS.map(w => (
                <option key={w.id} value={w.id}>{w.label}</option>
              ))}
            </select>
          </div>

          {/* Show Draft Version in footer */}
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={!!local.showDraftVersion}
              onChange={e => update('showDraftVersion', e.target.checked)}
              className="accent-primary-hover"
            />
            {t('drafting.showDraftVersion', 'Show "Draft Version" in document footer')}
          </label>

        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 px-6 py-4 border-t border-zinc-200">
          <button onClick={onClose} className="px-4 py-2 text-sm rounded border border-zinc-300 hover:bg-zinc-50">{t('drafting.cancel', 'Cancel')}</button>
          <button
            onClick={() => { onSave(local); onClose(); }}
            className="px-5 py-2 text-sm rounded bg-zinc-900 text-white hover:bg-zinc-700"
          >
            {t('drafting.saveSettings', 'Save Settings')}
          </button>
        </div>
      </div>
    </div>
  );
}

function Field({ label, value, onChange, placeholder }) {
  return (
    <div>
      {label && <label className="text-xs text-zinc-500 block mb-1">{label}</label>}
      <input
        type="text"
        value={value || ''}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full border border-zinc-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-zinc-600"
      />
    </div>
  );
}
