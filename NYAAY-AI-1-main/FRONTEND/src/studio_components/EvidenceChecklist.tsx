import React, { useState } from 'react';
import { 
  CheckSquare, 
  Square, 
  FileCheck2, 
  UploadCloud, 
  AlertTriangle, 
  ShieldCheck, 
  FileText, 
  Trash2, 
  Printer, 
  Download,
  Plus
} from 'lucide-react';
import { EvidenceItem, FivePartCaseDossier } from '../types';

interface EvidenceChecklistProps {
  dossier: FivePartCaseDossier | null;
  onUpdateEvidence: (items: EvidenceItem[]) => void;
  onGoToNavigator: () => void;
}

export const EvidenceChecklist: React.FC<EvidenceChecklistProps> = ({
  dossier,
  onUpdateEvidence,
  onGoToNavigator
}) => {
  const [newItemTitle, setNewItemTitle] = useState<string>('');
  const [newItemWeight, setNewItemWeight] = useState<'CRITICAL' | 'HIGH' | 'SUPPORTING'>('HIGH');
  const [dragActive, setDragActive] = useState<boolean>(false);

  if (!dossier) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center space-y-4">
        <FileCheck2 className="w-12 h-12 text-ink-muted mx-auto" />
        <h2 className="font-serif text-heading font-bold text-ink">No Active Case Docket Loaded</h2>
        <p className="text-sm text-ink-tertiary max-w-md mx-auto font-sans">
          To audit your legal evidence and compute court readiness, first execute a dispute search in the Civic Navigator.
        </p>
        <button
          onClick={onGoToNavigator}
          className="px-5 py-2.5 bg-dark text-paper text-xs font-bold rounded-[2px] hover:bg-dark-rule transition-colors"
        >
          GO TO CIVIC NAVIGATOR
        </button>
      </div>
    );
  }

  const items = dossier.evidenceRequired.items;

  // Calculate audit readiness score
  const totalWeight = items.reduce((acc, it) => {
    const val = it.evidentiaryWeight === 'CRITICAL' ? 3 : it.evidentiaryWeight === 'HIGH' ? 2 : 1;
    return acc + val;
  }, 0);

  const completedWeight = items.reduce((acc, it) => {
    if (!it.checked) return acc;
    const val = it.evidentiaryWeight === 'CRITICAL' ? 3 : it.evidentiaryWeight === 'HIGH' ? 2 : 1;
    return acc + val;
  }, 0);

  const auditScore = Math.round((completedWeight / (totalWeight || 1)) * 100);

  const handleToggleCheck = (id: string) => {
    const updated = items.map(it => it.id === id ? { ...it, checked: !it.checked } : it);
    onUpdateEvidence(updated);
  };

  const handleAttachFile = (id: string, fileName: string) => {
    const updated = items.map(it => it.id === id ? { ...it, fileAttached: fileName, checked: true } : it);
    onUpdateEvidence(updated);
  };

  const handleRemoveFile = (id: string) => {
    const updated = items.map(it => it.id === id ? { ...it, fileAttached: undefined } : it);
    onUpdateEvidence(updated);
  };

  const handleAddItem = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItemTitle.trim()) return;

    const newItem: EvidenceItem = {
      id: `ev-custom-${Date.now()}`,
      title: newItemTitle,
      description: 'Custom citizen supplementary evidentiary document.',
      isMandatory: false,
      evidentiaryWeight: newItemWeight,
      checked: false
    };

    onUpdateEvidence([...items, newItem]);
    setNewItemTitle('');
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      {/* Docket Subheader */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-rule pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="stamp-badge px-2 py-0.5">
              EVIDENTIARY VAULT // PART 02
            </span>
            <span className="text-xs text-ink-muted">
              DOCKET: {dossier.problemAndRights.docketId}
            </span>
          </div>
          <h1 className="font-serif text-heading font-bold text-ink mt-1">
            Evidentiary Audit & Document Checklist
          </h1>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => window.print()}
            className="px-3.5 py-2 border border-rule bg-white hover:bg-paper-sunken text-ink text-xs rounded-[2px] transition-colors flex items-center space-x-1.5"
          >
            <Printer className="w-3.5 h-3.5 text-accent" />
            <span>PRINT CHECKLIST</span>
          </button>
        </div>
      </div>

      {/* Audit Readiness Banner */}
      <div className="p-6 bg-dark text-paper rounded-[2px] border border-rule-dark grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
        <div className="md:col-span-8 space-y-2">
          <div className="flex items-center space-x-2">
            <span className="text-accent-text text-xs font-bold uppercase tracking-wider">
              JUDICIAL ADMISSIBILITY AUDIT
            </span>
            <span className="text-ink-tertiary">|</span>
            <span className="text-slate text-xs">
              BHARATIYA SAKSHYA ADHINIYAM (BSA 2023)
            </span>
          </div>
          <p className="text-sm text-paper font-sans leading-relaxed">
            {dossier.evidenceRequired.minimumEvidentiaryThreshold}
          </p>
          <div className="text-xs text-slate">
            Completed {items.filter(i => i.checked).length} of {items.length} required evidence items.
          </div>
        </div>

        <div className="md:col-span-4 bg-dark-raised p-4 rounded-[2px] border border-rule-dark text-center space-y-1">
          <div className="text-[12px] text-slate uppercase">AUDIT READINESS</div>
          <div className={`font-serif font-bold text-3xl ${auditScore >= 75 ? 'text-emerald-400' : 'text-amber-400'}`}>
            {auditScore}%
          </div>
          <div className="text-[12px] text-ink-tertiary">
            {auditScore >= 75 ? 'ADMISSIBLE FOR FILING' : 'SUPPLEMENTARY PROOF NEEDED'}
          </div>
        </div>
      </div>

      {/* Evidence Items List */}
      <div className="space-y-4">
        <div className="text-xs font-bold text-ink uppercase tracking-wider">
          MANDATORY & SUPPORTING EVIDENTIARY EXHIBITS:
        </div>

        <div className="space-y-3">
          {items.map((item, idx) => (
            <div
              key={item.id}
              className={`p-5 border transition-all rounded-[2px] bg-white ${
                item.checked ? 'border-dark shadow-xs' : 'border-rule'
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start space-x-3.5 flex-1">
                  <button
                    onClick={() => handleToggleCheck(item.id)}
                    className="mt-0.5 text-ink hover:text-accent cursor-pointer"
                  >
                    {item.checked ? (
                      <CheckSquare className="w-5 h-5 text-emerald-700" />
                    ) : (
                      <Square className="w-5 h-5 text-ink-muted" />
                    )}
                  </button>

                  <div className="space-y-1.5 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xs text-ink-muted">EXHIBIT #{idx + 1}</span>
                      <span className="font-serif font-bold text-base text-ink">{item.title}</span>
                      <span className={`text-[12px] px-2 py-0.5 rounded-[2px] font-bold ${
                        item.evidentiaryWeight === 'CRITICAL' 
                          ? 'bg-rose-100 text-rose-800' 
                          : item.evidentiaryWeight === 'HIGH'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-paper-sunken text-ink-tertiary'
                      }`}>
                        {item.evidentiaryWeight}
                      </span>
                      {item.isMandatory && (
                        <span className="text-[12px] px-1.5 py-0.5 bg-dark text-white rounded-[2px]">
                          STATUTORY MANDATORY
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-ink-tertiary font-sans leading-relaxed">
                      {item.description}
                    </p>

                    {item.notes && (
                      <div className="text-[12px] text-accent-text bg-paper p-2 border border-rule rounded-[2px]">
                        JUDICIAL NOTE: {item.notes}
                      </div>
                    )}

                    {/* Attached File Indicator */}
                    {item.fileAttached && (
                      <div className="flex items-center space-x-2 pt-1">
                        <span className="text-xs text-emerald-800 bg-emerald-50 px-2 py-1 border border-emerald-200 rounded-[2px] flex items-center space-x-1.5">
                          <FileText className="w-3.5 h-3.5 text-emerald-700" />
                          <span>ATTACHED: {item.fileAttached}</span>
                        </span>
                        <button
                          onClick={() => handleRemoveFile(item.id)}
                          className="text-xs text-rose-600 hover:underline flex items-center space-x-0.5"
                        >
                          <Trash2 className="w-3 h-3" />
                          <span>REMOVE</span>
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Upload Action */}
                {!item.fileAttached && (
                  <div className="shrink-0">
                    <label className="cursor-pointer px-3 py-1.5 border border-rule bg-paper hover:bg-rule text-ink text-xs rounded-[2px] flex items-center space-x-1.5 transition-colors">
                      <UploadCloud className="w-3.5 h-3.5 text-accent" />
                      <span>ATTACH PROOF</span>
                      <input
                        type="file"
                        className="hidden"
                        onChange={(e) => {
                          const file = e.target.files?.[0];
                          if (file) handleAttachFile(item.id, file.name);
                        }}
                      />
                    </label>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Add Custom Evidence Row Form */}
      <div className="border border-rule bg-white p-5 rounded-[2px]">
        <form onSubmit={handleAddItem} className="flex flex-col sm:flex-row items-end gap-3">
          <div className="flex-1 w-full space-y-1">
            <label className="text-xs font-bold text-ink uppercase">
              ADD SUPPLEMENTARY CITIZEN EXHIBIT:
            </label>
            <input
              type="text"
              value={newItemTitle}
              onChange={(e) => setNewItemTitle(e.target.value)}
              placeholder="e.g. Courier receipt copy, WhatsApp export PDF, Bank transaction slip..."
              className="w-full p-2.5 border border-rule bg-paper focus:bg-white text-xs font-sans rounded-[2px] outline-none"
            />
          </div>

          <div className="w-full sm:w-44 space-y-1">
            <label className="text-xs text-ink-muted uppercase">WEIGHT:</label>
            <select
              value={newItemWeight}
              onChange={(e) => setNewItemWeight(e.target.value as any)}
              className="w-full p-2.5 border border-rule bg-paper text-xs rounded-[2px] outline-none"
            >
              <option value="CRITICAL">CRITICAL</option>
              <option value="HIGH">HIGH</option>
              <option value="SUPPORTING">SUPPORTING</option>
            </select>
          </div>

          <button
            type="submit"
            className="w-full sm:w-auto px-4 py-2.5 bg-dark hover:bg-dark-rule text-paper text-xs font-bold rounded-[2px] transition-colors flex items-center justify-center space-x-1.5"
          >
            <Plus className="w-3.5 h-3.5 text-accent" />
            <span>ADD EXHIBIT</span>
          </button>
        </form>
      </div>
    </div>
  );
};
