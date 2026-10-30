import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import PageContainer from '../components/common/PageContainer';

import Card from '../components/common/Card';

import Button from '../components/common/Button';

import LoadingSpinner from '../components/common/LoadingSpinner';

import { Link, useLocation } from 'react-router-dom';

import DocumentToolbar from '../components/drafting/DocumentToolbar';
import DocumentPage from '../components/drafting/DocumentPage';
import LetterheadSettingsModal from '../components/drafting/LetterheadSettingsModal';

import { generateDraft, editDraft, downloadPdf, downloadDocx } from '../services/draftingService';

import Toast from '../components/common/Toast';

import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';



export default function DocHub() {
  const { t } = useTranslation();

  const { currentUser } = useAuth();
  const { language } = useLanguage();
  const location = useLocation();

  const [step, setStep] = useState(1);

  const [userFacts, setUserFacts] = useState("");

  const [isGenerating, setIsGenerating] = useState(false);

  const [error, setError] = useState("");

  const [toastMessage, setToastMessage] = useState("");

  const [isToastOpen, setIsToastOpen] = useState(false);



  // Edit States

  const [isEditing, setIsEditing] = useState(false);

  const [editInstructions, setEditInstructions] = useState("");



  // Draft Result States

  const [draftResult, setDraftResult] = useState(null);

  const [missingInfo, setMissingInfo] = useState({ documentType: "", fields: [], provided: {} });



  const handleGenerate = async (providedFields = null) => {

    if (!userFacts.trim()) {

      setError(t('docHub.errors.describeSituation'));

      return;

    }

    setError("");

    setIsGenerating(true);

    setStep(2); // Generating/Analyzing step

    

    try {

      const token = await currentUser?.getIdToken(true);
      if (!token) throw new Error(t('docHub.errors.loginRequired'));
      const result = await generateDraft(token, userFacts, providedFields, language);

      // Set isGenerating false BEFORE updating step/draftResult
      // so the Step 4 preview condition (step===4 && !isGenerating && draftResult)
      // is never in a bad intermediate state that causes a blank screen.
      setIsGenerating(false);

      if (result.status === "MISSING_INFO") {

        setMissingInfo({

          documentType: result.document_type,

          fields: result.missing_fields,

          provided: providedFields || {}

        });

        setStep(3); // Missing Info Wizard

      } else if (result.status === "SUCCESS") {

        setDraftResult(result.document_object);

        setStep(4); // Professional Preview

      } else if (result.status === "ERROR") {

        setError(result.message || t('docHub.errors.generateDraft'));

        setStep(1);

      } else {

        setError(t('docHub.errors.unexpected'));

        setStep(1);

      }

    } catch (err) {

      console.error(err);

      setError(t('docHub.errors.failedGenerate'));

      setIsGenerating(false);

      setStep(1);

    }

  };



  const handleEditSubmit = async () => {

    if (!editInstructions.trim()) return;

    setError("");

    setIsGenerating(true);

    try {

      const token = await currentUser?.getIdToken(true);
      const result = await editDraft(token, draftResult, editInstructions, language);

      setDraftResult(result);

      setEditInstructions("");

      setIsEditing(false);

      setToastMessage(t('docHub.toasts.updatedToV', { version: result.metadata.version }));

      setIsToastOpen(true);

    } catch (err) {

      console.error(err);

      setError(t('docHub.errors.failedEdit'));

    } finally {

      setIsGenerating(false);

    }

  };



  const handleMissingInfoSubmit = () => {

    handleGenerate(missingInfo.provided);

  };



  const handleDownloadPdf = async () => {

    try {

      setToastMessage(t('docHub.toasts.generatingPdf'));

      setIsToastOpen(true);

      const token = await currentUser?.getIdToken(true);
      const blob = await downloadPdf(token, draftResult);

      const url = window.URL.createObjectURL(blob);

      const a = document.createElement('a');

      a.href = url;

      a.download = `${draftResult.document_type.toLowerCase()}_v${draftResult.metadata.version}.pdf`;

      document.body.appendChild(a);

      a.click();

      a.remove();

      window.URL.revokeObjectURL(url);

    } catch (err) {

      setError(t('docHub.errors.failedPdf'));

    }

  };



  const handleDownloadDocx = async () => {

    try {

      setToastMessage(t('docHub.toasts.generatingDocx'));

      setIsToastOpen(true);

      const token = await currentUser?.getIdToken(true);
      const blob = await downloadDocx(token, draftResult);

      const url = window.URL.createObjectURL(blob);

      const a = document.createElement('a');

      a.href = url;

      a.download = `${draftResult.document_type.toLowerCase()}_v${draftResult.metadata.version}.docx`;

      document.body.appendChild(a);

      a.click();

      a.remove();

      window.URL.revokeObjectURL(url);

    } catch (err) {

      setError(t('docHub.errors.failedDocx'));

    }

  };



  const handleCopyText = () => {

    if (!draftResult) return;

    const text = draftResult.body.join("\n\n");

    navigator.clipboard.writeText(text);

    setToastMessage(t('docHub.toasts.draftCopied'));

    setIsToastOpen(true);

  };



  const renderA4Document = () => {

    if (!draftResult) return null;

    // Safely normalise parties: handle both Dict<str,str> and Array formats
    const partiesEntries = Array.isArray(draftResult.parties)
      ? draftResult.parties.map((p) => [p.role || p.name || t('docHub.document.party'), p.name || p.details || ''])
      : Object.entries(draftResult.parties || {});

    // Safely normalise body: handle both plain strings and section objects
    const bodyParagraphs = (draftResult.body || []).map((item) =>
      typeof item === 'string' ? item : item.content || item.section_title || JSON.stringify(item)
    );

    return (

      <div className="w-[210mm] min-h-[297mm] bg-white text-black p-[25.4mm] shadow-[0_20px_60px_-15px_rgba(0,0,0,0.1),0_0_0_1px_rgba(0,0,0,0.05)] mx-auto font-serif text-[12pt] leading-normal mb-10 relative">

        {draftResult.title && (

          <h1 className="text-center font-bold text-[14pt] mb-8 uppercase underline underline-offset-4">{draftResult.title}</h1>

        )}

        <div className="mb-6 space-y-2">

          {partiesEntries.map(([key, value], idx) => (

            <div key={idx} className="flex">

              <span className="font-bold mr-2 capitalize">{String(key).replace(/_/g, ' ')}:</span>

              <span>{String(value)}</span>

            </div>

          ))}

        </div>

        <div className="space-y-4 text-justify">

          {bodyParagraphs.length > 0 ? (
            bodyParagraphs.map((para, idx) => (
              <p key={idx} className="indent-8">{para}</p>
            ))
          ) : (
            <p className="text-gray-400 italic text-center py-8">{t('docHub.document.noContent')}</p>
          )}

        </div>

        {draftResult.verification && draftResult.verification.text && (

          <div className="mt-10">

            <h2 className="text-center font-bold text-[14pt] mb-4">{t('docHub.document.verification')}</h2>

            <p className="text-justify mb-4">{draftResult.verification.text}</p>

            <div className="flex flex-col gap-2">

              <p>{t('docHub.document.date')} {draftResult.verification.date}</p>

              <p>{t('docHub.document.place')} {draftResult.verification.place}</p>

            </div>

          </div>

        )}

        {draftResult.signature_blocks && draftResult.signature_blocks.length > 0 && (

          <div className="mt-16 flex flex-col items-end gap-12">

            {draftResult.signature_blocks.map((sig, idx) => (

              <div key={idx} className="text-center min-w-[200px]">

                <div className="border-b border-black mb-2 w-full"></div>

                <p className="font-bold">{sig}</p>

              </div>

            ))}

          </div>

        )}

        {draftResult.annexures && draftResult.annexures.length > 0 && (

          <div className="mt-16 break-before-page">

            <h2 className="text-center font-bold text-[14pt] mb-4">{t('docHub.document.annexures')}</h2>

            <ol className="list-decimal list-inside space-y-2">

              {draftResult.annexures.map((ann, idx) => (

                <li key={idx}>{ann}</li>

              ))}

            </ol>

          </div>

        )}

      </div>

    );

  };



  return (

    <PageContainer>

      <div className="flex flex-col gap-6 text-left max-w-5xl mx-auto mt-4 pb-20">

        {/* Breadcrumb */}

        <Link to="/dashboard" className="flex items-center gap-1 label-stamp text-ink-fog hover:text-ink transition-colors">{t('docHub.ui.dashboard')}</Link>



        {/* Header */}

        <div>
          <span className="label-stamp text-ink-fog">{t('docHub.ui.legalDrafting')}</span>
          <h1 className="text-[32px] font-bold text-ink mt-2 leading-tight" style={{ fontFamily: 'Newsreader, Georgia, serif' }}>
            {t('docHub.ui.documentDrafting')}<br /><span className="italic font-normal">{t('docHub.ui.filingReady')}</span>
          </h1>
          <p className="text-[13px] text-ink-muted mt-2">{t('docHub.ui.generateDescription')}</p>
        </div>



        {error && (
          <div className="bg-error-bg border border-error/30 text-error px-4 py-3 rounded-card text-[13px] shadow-stamp">
            {error}
          </div>
        )}



        {/* Visual 3-Step Mini Stepper */}
        <div className="bg-white border border-rule rounded-[4px] p-3 shadow-2xs">
          <div className="grid grid-cols-3 gap-2 text-center text-xs">
            <div className={`p-2 rounded-[2px] border transition-all ${
              step >= 1 ? 'bg-dark text-white border-dark font-bold' : 'bg-paper text-ink-muted border-rule'
            }`}>
              <span className="font-mono text-[10px] block opacity-80">{t('docHub.ui.step1Label')}</span>
              <span>{t('docHub.ui.step1Desc')}</span>
            </div>
            <div className={`p-2 rounded-[2px] border transition-all ${
              step === 3 ? 'bg-accent text-white border-accent font-bold' :
              step >= 2 ? 'bg-dark text-white border-dark font-bold' : 'bg-paper text-ink-muted border-rule'
            }`}>
              <span className="font-mono text-[10px] block opacity-80">{t('docHub.ui.step2Label')}</span>
              <span>{t('docHub.ui.step2Desc')}</span>
            </div>
            <div className={`p-2 rounded-[2px] border transition-all ${
              step === 4 ? 'bg-emerald-700 text-white border-emerald-700 font-bold' : 'bg-paper text-ink-muted border-rule'
            }`}>
              <span className="font-mono text-[10px] block opacity-80">{t('docHub.ui.step3Label')}</span>
              <span>{t('docHub.ui.step3Desc')}</span>
            </div>
          </div>
        </div>

        {/* Step 1: Input Facts */}

        {step === 1 && (

          <Card className="p-8">
            <span className="label-stamp text-ink-fog block mb-2">{t('docHub.ui.step1Title')}</span>
            <h2 className="text-[22px] font-bold text-ink mb-1" style={{ fontFamily: 'Newsreader, Georgia, serif' }}>{t('docHub.ui.describeSituationTitle')}</h2>
            <p className="text-[13px] text-ink-muted mb-5">{t('docHub.ui.explainIssue')}</p>

            <textarea
              className="w-full h-48 p-4 border border-rule bg-paper rounded-[4px] focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent resize-none text-[14px] text-ink placeholder:text-ink-muted transition-all duration-150 shadow-2xs"
              placeholder={t('docHub.ui.placeholder')}
              value={userFacts}
              onChange={(e) => setUserFacts(e.target.value)}
            />

            <div className="mt-4 flex justify-end">
              <button
                onClick={() => handleGenerate(null)}
                disabled={!userFacts.trim() || isGenerating}
                className={`px-6 py-2.5 rounded-[3px] text-xs font-bold transition-all duration-200 cursor-pointer shadow-xs ${
                  userFacts.trim() 
                    ? 'bg-accent hover:bg-accent-hover text-white' 
                    : 'bg-paper-sunken border border-rule text-ink-muted opacity-60 cursor-not-allowed'
                }`}
              >
                {t('docHub.ui.analyzeDraft')}
              </button>
            </div>
          </Card>

        )}



        {/* Step 2: Generating / Analyzing */}

        {(step === 2 || (step === 4 && isGenerating)) && (

          <Card className="p-16 flex flex-col items-center justify-center gap-4">
            <div className="w-10 h-10 border-2 border-paper-rule border-t-amber rounded-full animate-spin" />
            <span className="label-stamp text-ink-fog">{step === 4 ? t('docHub.ui.applyingEdits') : t('docHub.ui.analysingFacts')}</span>
            <p className="text-[13px] text-ink-muted text-center max-w-md">
              {step === 4 ? t('docHub.ui.redrafting') : t('docHub.ui.identifyingType')}
            </p>
          </Card>

        )}



        {/* Step 3: Missing Info Wizard */}

        {step === 3 && (

          <Card className="p-8">
            <span className="label-stamp text-ink-fog block mb-2">{t('docHub.ui.step2Title')}</span>
            <h2 className="text-[22px] font-bold text-ink mb-2" style={{ fontFamily: 'Newsreader, Georgia, serif' }}>{t('docHub.ui.missingInfo')}</h2>
            <p className="text-[13px] text-ink-muted mb-6 p-4 bg-paper-warm rounded-card border border-paper-rule">
              {t('docHub.ui.weIdentified')}<strong className="text-ink">{missingInfo.documentType.replace(/_/g, ' ')}</strong>{t('docHub.ui.toDraft')}
            </p>

            <div className="space-y-4">
              {missingInfo.fields.map(field => (
                <div key={field} className="flex flex-col gap-1">
                  <label className="label-stamp text-ink-muted capitalize">{field.replace(/_/g, ' ')}</label>
                  <input
                    type="text"
                    className="p-3 bg-paper border border-paper-rule rounded-button focus:ring-1 focus:ring-amber focus:border-amber focus:outline-none text-[14px] text-ink w-full max-w-md transition-all duration-150"
                    placeholder={`${t('docHub.ui.enter')} ${field.replace(/_/g, ' ')}`}
                    value={missingInfo.provided[field] || ""}
                    onChange={(e) => setMissingInfo(prev => ({
                      ...prev,
                      provided: { ...prev.provided, [field]: e.target.value }
                    }))}
                  />
                </div>
              ))}
            </div>

            <div className="mt-8 flex justify-end gap-3">
              <Button variant="outline" onClick={() => setStep(1)}>{t('docHub.ui.back')}</Button>
              <Button onClick={handleMissingInfoSubmit}>{t('docHub.ui.generateFinalDraft')}</Button>
            </div>
          </Card>

        )}



        {/* Step 4: Final Preview */}

        {step === 4 && !isGenerating && draftResult && (

          <div className="flex flex-col gap-6">

            {/* Professional Toolbar */}

            <div className="sticky top-4 z-20 bg-paper/90 backdrop-blur-md p-4 border border-paper-rule rounded-card shadow-card flex flex-col gap-3">
              <div className="flex flex-wrap items-center justify-between">
                <div>
                  <span className="label-stamp text-ink-fog block">{t('docHub.ui.draftV', { version: draftResult.metadata.version })}</span>
                  <span className="text-[14px] font-semibold text-ink">{draftResult.document_type.replace(/_/g, ' ')}</span>
                </div>

                <div className="flex gap-2 flex-wrap">
                  <Button variant="outline" onClick={() => window.print()} className="!py-2 !px-3 text-xs flex items-center gap-1">{t('docHub.ui.print')}</Button>
                  <Button variant="outline" onClick={handleDownloadPdf} className="!py-2 !px-3 text-xs flex items-center gap-1 hover:text-error hover:border-error/30">{t('docHub.ui.pdf')}</Button>
                  <Button variant="outline" onClick={handleDownloadDocx} className="!py-2 !px-3 text-xs flex items-center gap-1 hover:text-amber hover:border-amber/30">{t('docHub.ui.docx')}</Button>
                  <div className="w-px h-6 bg-paper-rule mx-1 self-center" />
                  <Button variant={isEditing ? 'secondary' : 'outline'} onClick={() => setIsEditing(!isEditing)} className="!py-2 !px-3 text-xs">{t('docHub.ui.editDraft')}</Button>
                  <Button variant="outline" onClick={handleCopyText} className="!py-2 !px-3 text-xs">{t('docHub.ui.copyText')}</Button>
                  <Button variant="outline" onClick={() => setStep(1)} className="!py-2 !px-3 text-xs">{t('docHub.ui.startOver')}</Button>
                </div>
              </div>



              {/* Edit Panel */}

              {isEditing && (
                <div className="pt-3 border-t border-paper-rule flex gap-2">
                  <input
                    type="text"
                    className="flex-1 p-3 bg-paper border border-paper-rule rounded-button text-[14px] focus:outline-none focus:ring-1 focus:ring-amber focus:border-amber transition-all"
                    placeholder={t('docHub.ui.editPlaceholder')}
                    value={editInstructions}
                    onChange={(e) => setEditInstructions(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleEditSubmit()}
                  />
                  <Button onClick={handleEditSubmit} disabled={!editInstructions.trim()} className="!py-2 !px-4 text-xs">{t('docHub.ui.applyEdit')}</Button>
                </div>
              )}

            </div>



            {/* A4 Document Preview */}

            <div className="overflow-x-auto bg-paper-warm p-8 rounded-card border border-paper-rule shadow-inner flex justify-center">
              {renderA4Document()}
            </div>

          </div>

        )}

      </div>

      

      <Toast

        message={toastMessage}

        isOpen={isToastOpen}

        onClose={() => setIsToastOpen(false)}

      />

    </PageContainer>

  );

}

