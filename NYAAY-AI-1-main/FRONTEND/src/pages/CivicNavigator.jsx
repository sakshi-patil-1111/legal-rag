import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { FolderArchive, X, Plus, Inbox } from 'lucide-react';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';
import Toast from '../components/common/Toast';

// Import all studio components
import { CivicNavigator as StudioCivicNavigator } from '../studio_components/CivicNavigator';
import { EvidenceChecklist } from '../studio_components/EvidenceChecklist';
import { ActionPlanStepper } from '../studio_components/ActionPlanStepper';
import { SchemeEligibilityReader } from '../studio_components/SchemeEligibilityReader';
import { ConversationalFormFiller } from '../studio_components/ConversationalFormFiller';
import { BareActsBrowser } from '../studio_components/BareActsBrowser';

/*
 * Tabs of this page.
 *
 * 'drafter' used to be listed here, but both handleTabChange and the inner
 * onNavigateToTab redirected it to /dochub, so the `activeTab === 'drafter'`
 * branch was unreachable and DocumentDraftingTool never rendered on this page.
 * A tab that navigates away from its own page is also not a tab. Removed.
 */
const CIVIC_TABS = [
  { id: 'navigator',     label: 'Case Dossier' },
  { id: 'evidence',      label: 'Evidence Checklist' },
  { id: 'action_plan',   label: 'Action Plan' },
  { id: 'scheme_reader', label: 'Schemes' },
  { id: 'bare_acts',     label: 'Bare Acts' },
  { id: 'form_filler',   label: 'Form Filler' },
];

const VALID_TAB_IDS = new Set(CIVIC_TABS.map((t) => t.id));

export default function CivicNavigatorPage() {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();

  /* The landing page and the navbar can request a specific tab via router
     state. Validated, so a stale or hand-typed value can't blank the page. */
  const requestedTab = location.state?.tab;
  const [activeTab, setActiveTab] = useState(
    VALID_TAB_IDS.has(requestedTab) ? requestedTab : 'navigator'
  );

  const [activeDossier, setActiveDossier] = useState(null);
  const [dossierDrawerOpen, setDossierDrawerOpen] = useState(false);
  const [toast, setToast] = useState(null);

  const presetQueryText = location.state?.presetQuery || '';

  const [savedCases, setSavedCases] = useState(() => {
    try {
      const stored = localStorage.getItem('nyaay_saved_dockets');
      if (stored) return JSON.parse(stored);
    } catch {
      // ignore
    }
    return [];
  });

  useEffect(() => {
    try {
      localStorage.setItem('nyaay_saved_dockets', JSON.stringify(savedCases));
    } catch {
      // ignore
    }
  }, [savedCases]);

  // Sync activeDossier updates (like evidence checks) back to savedCases
  useEffect(() => {
    if (activeDossier) {
      setSavedCases(prev => prev.map(c =>
        c.docketNumber === activeDossier?.problemAndRights?.docketId
          ? { ...c, dossier: activeDossier }
          : c
      ));
    }
  }, [activeDossier]);

  /* Close the mobile drawer on Escape */
  useEffect(() => {
    if (!dossierDrawerOpen) return;
    const onKeyDown = (e) => { if (e.key === 'Escape') setDossierDrawerOpen(false); };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [dossierDrawerOpen]);

  const handleSaveDossier = (dossierToSave, title) => {
    const existingIndex = savedCases.findIndex(c => c.docketNumber === dossierToSave.problemAndRights.docketId);
    if (existingIndex >= 0) return;

    const newRecord = {
      id: `case-${Date.now()}`,
      docketNumber: dossierToSave.problemAndRights.docketId,
      title: title.slice(0, 60),
      domain: dossierToSave.problemAndRights.domain,
      createdAt: new Date().toISOString(),
      status: 'ACTIVE',
      dossier: dossierToSave
    };

    setSavedCases(prev => [newRecord, ...prev]);
    setToast({ variant: 'success', message: `Saved to dockets as ${newRecord.docketNumber}.` });
  };

  const handleUpdateEvidence = (itemId, isChecked) => {
    if (!activeDossier) return;
    setActiveDossier(prev => {
      const copy = { ...prev };
      const item = copy.evidenceRequired.items.find(i => i.id === itemId);
      if (item) item.checked = isChecked;
      return copy;
    });
  };

  const handleUpdateSteps = (stepNum, newStatus) => {
    if (!activeDossier) return;
    setActiveDossier(prev => {
      const copy = { ...prev };
      const step = copy.actionPlan.steps.find(s => s.stepNumber === stepNum);
      if (step) step.status = newStatus;
      return copy;
    });
  };

  const goToTab = useCallback((tabId) => {
    if (tabId === 'drafter') {
      navigate('/dochub');
      return;
    }
    setActiveTab(tabId);
    setDossierDrawerOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [navigate]);

  const startNewCase = () => {
    setActiveDossier(null);
    setActiveTab('navigator');
    setDossierDrawerOpen(false);
  };

  const openSavedCase = (c) => {
    if (!c.dossier || !c.dossier.problemAndRights || !c.dossier.evidenceRequired || !c.dossier.actionPlan) {
      /* Was a blocking `alert()`. */
      setToast({
        variant: 'error',
        message: 'That docket was saved by an older version of the app and can no longer be opened. Run the query again to rebuild it.',
      });
      return;
    }
    setActiveDossier(c.dossier);
    setActiveTab('navigator');
    setDossierDrawerOpen(false);
  };

  /* Saved-dossier list, shared by the desktop rail and the mobile drawer.
     Previously this markup was `hidden md:flex` only, so on a phone saved
     dockets were completely unreachable. */
  const dossierPanel = (
    <>
      <div className="p-4 border-b border-rule flex items-center justify-between bg-white shrink-0">
        <h2 className="font-serif font-bold text-ink">{t('civicNavigator.savedDossiers')}</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={startNewCase}
            className="flex items-center gap-1 text-[12px] bg-dark text-paper px-2.5 py-1.5 rounded-[3px] font-semibold hover:bg-accent transition-colors focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-1 focus-visible:outline-none"
          >
            <Plus aria-hidden="true" className="w-3 h-3" />
            {t('civicNavigator.newCase')}
          </button>
          <button
            onClick={() => setDossierDrawerOpen(false)}
            aria-label={t('civicNavigator.closeSavedDossiers')}
            className="md:hidden p-1.5 rounded text-ink-tertiary hover:text-ink hover:bg-paper-sunken transition-colors focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none"
          >
            <X aria-hidden="true" className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {savedCases.length === 0 ? (
          <div className="text-center mt-10 px-2">
            <Inbox aria-hidden="true" className="w-6 h-6 mx-auto text-rule-strong" />
            <p className="mt-3 text-[13px] font-semibold text-ink">{t('civicNavigator.noDocketsYet')}</p>
            <p className="mt-1 text-[12px] text-ink-tertiary leading-relaxed">{t('civicNavigator.runAQuery')}</p>
          </div>
        ) : (
          savedCases.map(c => {
            const isActive = activeDossier?.problemAndRights?.docketId === c.docketNumber;
            return (
              <button
                key={c.id}
                type="button"
                onClick={() => openSavedCase(c)}
                aria-current={isActive ? 'true' : undefined}
                className={`w-full text-left p-3 rounded-[3px] border transition-all focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none ${
                  isActive
                    ? 'bg-white border-accent shadow-sm ring-1 ring-accent/10'
                    : 'bg-white/50 border-rule hover:bg-white hover:border-accent/50'
                }`}
              >
                <div className="text-[12px] font-mono font-bold text-accent-text mb-1.5 tracking-wide">{c.docketNumber}</div>
                <div className="text-sm font-bold text-ink line-clamp-2 leading-snug">{c.title}</div>
                <div className="text-[12px] text-ink-tertiary mt-3 flex justify-between items-center gap-2 border-t border-dashed border-rule pt-2">
                  <span className="truncate">{c.domain}</span>
                  <span className="shrink-0 font-mono">{new Date(c.createdAt).toLocaleDateString()}</span>
                </div>
              </button>
            );
          })
        )}
      </div>
    </>
  );

  return (
    <div className="min-h-screen flex flex-col bg-paper ledger-grid text-ink font-sans">
      <Navbar
        tabs={CIVIC_TABS.map(tab => ({ ...tab, label: t('civicNavigator.tabs.' + tab.id) }))}
        activeTab={activeTab}
        onTabChange={goToTab}
      />

      {/*
        Top padding: 64px navbar + 40px tab strip, plus the ~46px mobile nav
        strip below lg. The old flat pt-[104px] left the mobile tab strip
        underneath the nav.

        The inner scroll region is md+ only. On a phone a nested scroll trap
        inside a page that also scrolls is just two competing scrollbars.
      */}
      <main className="flex-1 bg-paper pt-[150px] lg:pt-[104px] min-h-[calc(100vh-150px)] lg:min-h-[calc(100vh-104px)] flex md:overflow-hidden">

        {/* Saved dossiers — desktop rail */}
        <aside
          className="w-80 bg-paper border-r border-rule flex-col h-full hidden md:flex shrink-0"
          aria-label={t('civicNavigator.savedDossiers')}
        >
          {dossierPanel}
        </aside>

        {/* Saved dossiers — mobile drawer */}
        {dossierDrawerOpen && (
          <div className="md:hidden fixed inset-0 z-40 flex">
            <div
              className="absolute inset-0 bg-dark/50"
              onClick={() => setDossierDrawerOpen(false)}
            />
            <aside
              className="relative w-[85vw] max-w-xs bg-paper border-r border-rule flex flex-col h-full shadow-modal animate-slide-in"
              aria-label={t('civicNavigator.savedDossiers')}
            >
              {dossierPanel}
            </aside>
          </div>
        )}

        {/* MAIN AREA */}
        <div className="flex-1 md:overflow-y-auto bg-paper">
          {/* Mobile entry point to the dossier list */}
          <div className="md:hidden sticky top-0 z-20 px-4 py-2 bg-paper/95 backdrop-blur-sm border-b border-rule">
            <button
              onClick={() => setDossierDrawerOpen(true)}
              className="flex items-center gap-1.5 text-[13px] font-medium text-ink px-2.5 py-1.5 rounded-[3px] border border-rule-strong bg-white hover:border-accent transition-colors focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none"
            >
              <FolderArchive aria-hidden="true" className="w-3.5 h-3.5 text-accent" />
              {t('civicNavigator.savedDossiers')}
              {savedCases.length > 0 && (
                <span className="ml-0.5 font-mono text-[12px] text-ink-tertiary">({savedCases.length})</span>
              )}
            </button>
          </div>

          {activeTab === 'navigator' && (
            <StudioCivicNavigator
              initialQuery={presetQueryText}
              onNavigateToTab={goToTab}
              onSaveDossier={handleSaveDossier}
              savedDocketIds={savedCases.map(c => c.docketNumber)}
              activeDossier={activeDossier}
              setActiveDossier={setActiveDossier}
            />
          )}

          {activeTab === 'scheme_reader' && (
            <SchemeEligibilityReader
              onGoToNavigator={() => goToTab('navigator')}
              onGoToFormFiller={() => goToTab('form_filler')}
            />
          )}

          {activeTab === 'form_filler' && (
            <ConversationalFormFiller />
          )}

          {activeTab === 'evidence' && (
            <EvidenceChecklist
              dossier={activeDossier}
              onUpdateEvidence={handleUpdateEvidence}
              onGoToNavigator={() => goToTab('navigator')}
            />
          )}

          {activeTab === 'action_plan' && (
            <ActionPlanStepper
              dossier={activeDossier}
              onUpdateSteps={handleUpdateSteps}
              onGoToNavigator={() => goToTab('navigator')}
              onGoToDrafter={() => navigate('/dochub')}
            />
          )}

          {activeTab === 'bare_acts' && (
            <BareActsBrowser
              onSelectActForQuery={(act) => {
                navigate('/know-your-kanoon', {
                  state: { presetQuery: `I have a question about the ${act.title}. ` }
                });
              }}
            />
          )}
        </div>
      </main>

      <Toast
        isOpen={!!toast}
        message={toast?.message}
        variant={toast?.variant}
        duration={toast?.variant === 'error' ? 0 : 3000}
        dismissible={toast?.variant === 'error'}
        onClose={() => setToast(null)}
      />

      <Footer />
    </div>
  );
}
