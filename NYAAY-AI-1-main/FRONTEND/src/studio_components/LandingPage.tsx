import React, { useState, useEffect, useRef } from 'react';
import { 
  ArrowRight, 
  ShieldAlert, 
  FileCheck2, 
  Building2, 
  Milestone, 
  FileText, 
  Layers, 
  Cpu, 
  Hash, 
  CheckCircle2,
  BookOpen,
  Sparkles,
  Search,
  Zap,
  Eye,
  ShieldCheck,
  Bot,
  FileCheck,
  ChevronLeft,
  ChevronRight,
  Scale,
  Gavel,
  Landmark
} from 'lucide-react';
import HeroPipelineAnimation from '../components/landing/HeroPipelineAnimation';
import { StatuteInspectionModal } from './StatuteInspectionModal';
import { BARE_ACTS_CATALOG } from '../data/bareActsData';
import { useTranslation } from 'react-i18next';
import { BareAct } from '../types';

const ThreeDocumentPlanes = React.lazy(() =>
  import('./ThreeDocumentPlanes').then(m => ({ default: m.ThreeDocumentPlanes }))
);

function ThreePlaneFallback() {
  const { t } = useTranslation();
  return (
    <div className="w-full h-[440px] bg-paper-sunken border border-rule flex flex-col items-center justify-center p-6 text-center rounded-[2px]">
      <div className="w-3 h-3 rounded-full bg-accent animate-pulse mb-3" />
      <div className="font-serif font-bold text-ink text-sm">{t('landing.fallback.title', '3D STATUTORY ARRAY')}</div>
      <div className="text-[12px] text-ink-muted mt-1">{t('landing.fallback.subtitle', 'Loading 93 Indian Bare Acts model…')}</div>
    </div>
  );
}

interface LandingPageProps {
  onStartQuery: (presetText?: string) => void;
  onExploreActs: () => void;
  onNavigateToTab?: (tab: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ 
  onStartQuery, 
  onExploreActs,
  onNavigateToTab
}) => {
  const [activeStepPinned, setActiveStepPinned] = useState<number>(0);
  const [activePillarIdx, setActivePillarIdx] = useState<number>(0);
  const [actSearchQuery, setActSearchQuery] = useState('');
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const { t } = useTranslation();
  const [selectedDemoAct, setSelectedDemoAct] = useState<string>('rti-2005');
  const [inspectingAct, setInspectingAct] = useState<BareAct | null>(null);
  const scenarioScrollRef = useRef<HTMLDivElement>(null);

  const sampleCivicDisputes = [
    {
      domain: t('landing.scenarios.rti.domain', 'RTI'),
      title: t('landing.scenarios.rti.title', 'Municipal Road Tender RTI Delayed 38 Days'),
      query: t('landing.scenarios.rti.query', 'I filed an RTI application 38 days ago with the Municipal Corporation requesting road repair tender details and contractor payment logs. No response received.'),
      statute: t('landing.scenarios.rti.statute', 'RTI Act 2005 (Sec 7 & 19)'),
      badge: t('landing.scenarios.rti.badge', 'DEEMED REFUSAL')
    },
    {
      domain: t('landing.scenarios.consumer.domain', 'CONSUMER'),
      title: t('landing.scenarios.consumer.title', 'Authorized Dealer Refused Laptop Warranty'),
      query: t('landing.scenarios.consumer.query', 'Authorized service center rejected warranty repair on my 4-month-old laptop claiming customer fault without technical diagnostic inspection.'),
      statute: t('landing.scenarios.consumer.statute', 'Consumer Protection Act 2019 (Sec 2(11) & 84)'),
      badge: t('landing.scenarios.consumer.badge', 'UNFAIR PRACTICE')
    },
    {
      domain: t('landing.scenarios.workplace.domain', 'WORKPLACE'),
      title: t('landing.scenarios.workplace.title', 'Company Withholding Statutory Gratuity & Relieving Letter'),
      query: t('landing.scenarios.workplace.query', 'I resigned after 6 years of continuous service. Company HR is refusing to disburse my statutory gratuity and withholding my relieving letter.'),
      statute: t('landing.scenarios.workplace.statute', 'Payment of Gratuity Act 1972 (Sec 4 & 7)'),
      badge: t('landing.scenarios.workplace.badge', 'STATUTORY GRATUITY')
    },
    {
      domain: t('landing.scenarios.tenant.domain', 'TENANT'),
      title: t('landing.scenarios.tenant.title', 'Landlord Issued 7-Day WhatsApp Eviction Notice'),
      query: t('landing.scenarios.tenant.query', 'Landlord sent a WhatsApp message giving me 7 days to vacate apartment despite full rent paid on time and active lease agreement in force.'),
      statute: t('landing.scenarios.tenant.statute', 'TPA 1882 (Sec 106) & SRA (Sec 6)'),
      badge: t('landing.scenarios.tenant.badge', 'UNLAWFUL EVICTION')
    },
    {
      domain: t('landing.scenarios.rera.domain', 'RERA'),
      title: t('landing.scenarios.rera.title', 'Builder Delayed Apartment Possession 18 Months'),
      query: t('landing.scenarios.rera.query', 'Promoter delayed handover of apartment by 18 months beyond RERA registered completion date and refuses to pay statutory monthly interest.'),
      statute: t('landing.scenarios.rera.statute', 'RERA 2016 (Sec 18)'),
      badge: t('landing.scenarios.rera.badge', 'STATUTORY COMPENSATION')
    }
  ];

  const fivePartArchitecture = [
    {
      index: 1,
      name: t('landing.arch.part1.name', 'Problem & Rights'),
      badge: t('landing.arch.part1.badge', 'GROUNDED STATUTE'),
      icon: ShieldAlert,
      title: t('landing.arch.part1.title', 'Statutory Shield & Rights Identification'),
      description: t('landing.arch.part1.description', 'Zero-hallucination extraction of enforceable citizen rights directly mapped to exact legislative Sections from the 93 Indian Bare Acts.'),
      dossierHighlight: t('landing.arch.part1.dossierHighlight', 'Section 7(2) RTI Act: Deemed Refusal invokes immediate First Appellate Authority jurisdiction without fresh fees.')
    },
    {
      index: 2,
      name: t('landing.arch.part2.name', 'Evidence Required'),
      badge: t('landing.arch.part2.badge', 'AUDIT CHECKLIST'),
      icon: FileCheck2,
      title: t('landing.arch.part2.title', 'Evidentiary Threshold & Verification (BSA 2023)'),
      description: t('landing.arch.part2.description', 'Defines mandatory vs supporting documentation required before any tribunal or magistrate, calculating audit readiness before filing.'),
      dossierHighlight: t('landing.arch.part2.dossierHighlight', 'Mandatory: Speed Post Tracking Acknowledgment Slip proving delivery + Section 63 BSA Electronic Certificate.')
    },
    {
      index: 3,
      name: t('landing.arch.part3.name', 'Relevant Authority'),
      badge: t('landing.arch.part3.badge', 'JURISDICTION MAP'),
      icon: Building2,
      title: t('landing.arch.part3.title', 'Specific Officer & Multi-Tier Escalation'),
      description: t('landing.arch.part3.description', 'Pinpoints the precise designated officer, appellate forum, official e-filing portal (e-Daakhil / RTI Online / Rent Court), and fee schedule.'),
      dossierHighlight: t('landing.arch.part3.dossierHighlight', 'Tier 2: First Appellate Authority (FAA) — Mandatory 30-day speaking order timeline.')
    },
    {
      index: 4,
      name: t('landing.arch.part4.name', 'Action Plan'),
      badge: t('landing.arch.part4.badge', 'LIMITATION TIMELINE'),
      icon: Milestone,
      title: t('landing.arch.part4.title', 'Day 1 → Day 30 Phased Milestone Stepper'),
      description: t('landing.arch.part4.description', 'Chronological execution steps tied strictly to statutory limitation deadlines under the Limitation Act 1963 and respective procedural codes.'),
      dossierHighlight: t('landing.arch.part4.dossierHighlight', 'Day 31 Expiry: File Memorandum of First Appeal within 30 days of statutory default.')
    },
    {
      index: 5,
      name: t('landing.arch.part5.name', 'Document Generation'),
      badge: t('landing.arch.part5.badge', 'SINGLE-PASS ENGINE'),
      icon: FileText,
      title: t('landing.arch.part5.title', 'Dynamic Legal Draft with Placeholder Tokens'),
      description: t('landing.arch.part5.description', 'Instant production of actionable legal notices, affidavits, RTI appeals, and tenant replies formatted to judicial standards with highlighted editable tags.'),
      dossierHighlight: t('landing.arch.part5.dossierHighlight', 'Memorandum of Appeal under Sec 19(1) with bracketed placeholders ready to print, copy, and post.')
    }
  ];

  return (
    <div className="min-h-screen bg-paper ledger-grid text-ink">
      {/* 1. EDITORIAL CASE FILE HERO */}
      <section className="relative min-h-[calc(100vh-64px)] py-12 flex flex-col justify-center border-b border-rule">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          {/* Documentary Docket Sub-Header */}
          <div className="flex flex-wrap items-center justify-between gap-2 pb-4 mb-8 border-b border-rule">
            <div className="flex items-center space-x-2.5">
              <span className="stamp-badge px-2 py-0.5">
                {t('landing.hero.civic_empowerment', 'Civic empowerment')}
              </span>
              {/* A build identifier is genuinely machine output, so mono earns
                  its place here. Most of the mono on this page did not. */}
              <span className="text-[12px] text-ink-muted">
                {t('landing.hero.build_id', 'NYAAY-RAG-2026')}
              </span>
            </div>
            <div className="text-[12px] text-ink-tertiary flex items-center space-x-3">
              <span>{t('landing.hero.acts_indexed', '93 Indian Bare Acts indexed')}</span>
              <span aria-hidden="true" className="text-rule-strong">•</span>
              <span className="font-semibold text-success">{t('landing.hero.fast_answers', '100% Statute-Grounded Answers')}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
            {/* Left: Asymmetric Editorial Typography */}
            <div className="lg:col-span-7 space-y-6">
              <div className="space-y-3">
                {/*
                  This badge used to read "HYBRID DENSE + SPARSE RETRIEVAL
                  (CHROMA + BM25)". The first thing a citizen read on a legal-aid
                  site was a vector-database spec. The retrieval architecture is
                  still stated on the page — in the strip below and in the Live
                  Proof section — just not as the opening line.
                */}
                <div className="inline-flex items-center space-x-2 bg-paper-sunken px-2.5 py-1 rounded-[2px] border border-rule-strong">
                  <Cpu aria-hidden="true" className="w-3.5 h-3.5 text-accent" />
                  <span className="text-[12px] text-ink font-semibold">
                    {t('landing.hero.badge', 'Grounded in statute — every answer cites the Act it came from')}
                  </span>
                </div>

                <h1 className="font-serif text-display-lg text-ink font-bold leading-tight">
                  {t('landing.hero.title1', 'Not Just a Legal Engine.')} <br className="hidden sm:inline" />
                  <span className="text-accent italic font-normal">{t('landing.hero.title2', 'A Companion to Justice. ⚖️')}</span>
                </h1>
              </div>

              <div className="space-y-4 max-w-2xl">
                <p className="text-lg sm:text-xl text-ink-secondary leading-relaxed font-sans">
                  {t('landing.hero.subtitle', 'From laws to landmark judgments — making India’s legal knowledge easier to find, understand, and access.')}
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 sm:gap-8 w-full pt-4 pb-2">
                  <div className="group flex flex-col items-start cursor-default">
                    <Scale className="w-[20px] h-[20px] text-accent mb-2" />
                    <div className="font-serif text-[28px] sm:text-[32px] font-bold text-ink leading-none mb-1">93</div>
                    <div className="text-ink-muted text-[11px] uppercase tracking-widest font-semibold">{t('landing.stats.acts', 'Acts & Statutes')}</div>
                  </div>

                  <div className="group flex flex-col items-start cursor-default">
                    <Gavel className="w-[20px] h-[20px] text-accent mb-2" />
                    <div className="font-serif text-[28px] sm:text-[32px] font-bold text-ink leading-none mb-1">4,371</div>
                    <div className="text-ink-muted text-[11px] uppercase tracking-widest font-semibold">{t('landing.stats.sc', 'SC Judgments')}</div>
                  </div>

                  <div className="group flex flex-col items-start cursor-default">
                    <Landmark className="w-[20px] h-[20px] text-accent mb-2" />
                    <div className="font-serif text-[28px] sm:text-[32px] font-bold text-ink leading-none mb-1">21</div>
                    <div className="text-ink-muted text-[11px] uppercase tracking-widest font-semibold">{t('landing.stats.schemes', 'Govt Schemes')}</div>
                  </div>
                </div>
              </div>

              {/* Action buttons with quick-try micro-instruction */}
              <div className="space-y-3 pt-2">
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={() => onStartQuery()}
                    className="px-6 py-3.5 bg-dark hover:bg-dark-rule text-paper text-[15px] font-semibold rounded-[2px] transition-all flex items-center space-x-2.5 shadow-sm group active:translate-y-0.5 focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:outline-none cursor-pointer"
                  >
                    <Search aria-hidden="true" className="w-4 h-4 text-accent" />
                    <span>{t('landing.hero.cta_start', 'Describe your problem')}</span>
                    <ArrowRight aria-hidden="true" className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </button>

                  <button
                    onClick={onExploreActs}
                    className="px-5 py-3.5 border border-dark bg-white hover:bg-paper-sunken text-ink text-[15px] font-semibold rounded-[2px] transition-colors focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:outline-none cursor-pointer"
                  >
                    {t('landing.hero.cta_explore', 'Browse the 93 Bare Acts')}
                  </button>
                </div>

                {/* Quick-try helper chip */}
                <div className="flex flex-wrap items-center gap-1.5 text-xs text-ink-muted">
                  <span className="font-mono text-[11px] uppercase">{t('landing.hero.try_label', 'TRY:')}</span>
                  <button
                    onClick={() => onStartQuery(t('landing.hero.try_rti_query', 'I filed an RTI application 38 days ago with the Municipal Corporation regarding road repair tender. No response received.'))}
                    className="font-mono text-[11px] text-accent-text hover:underline cursor-pointer bg-paper-sunken px-2 py-0.5 rounded border border-rule"
                  >
                    {t('landing.hero.try_rti', '"My RTI has been ignored for 38 days"')}
                  </button>
                  <button
                    onClick={() => onStartQuery(t('landing.hero.try_eviction_query', 'Landlord sent a WhatsApp message giving me 7 days to vacate despite full rent paid and active lease agreement.'))}
                    className="font-mono text-[11px] text-accent-text hover:underline cursor-pointer bg-paper-sunken px-2 py-0.5 rounded border border-rule hidden sm:inline-block"
                  >
                    {t('landing.hero.try_eviction', '"Landlord 7-day eviction notice"')}
                  </button>
                </div>
              </div>
            </div>

            {/* Right: Interactive 3D Document Planes Visual */}
            <div className="lg:col-span-5 space-y-3">
              <div className="border border-rule bg-white p-2 rounded-[2px] shadow-sm overflow-hidden h-[460px] flex flex-col">
                <React.Suspense fallback={<ThreePlaneFallback />}>
                  <ThreeDocumentPlanes
                    activeActId={selectedDemoAct}
                    isConverging={true}
                    onSelectAct={(actId) => setSelectedDemoAct(actId)}
                    onInspectAct={(act) => setInspectingAct(act)}
                    className="w-full h-full flex-1"
                  />
                </React.Suspense>
              </div>
              <div className="flex items-center justify-between text-[12px] text-ink-tertiary px-1">
                <span>{t('landing.hero.planes.caption1', 'Statutes ranked against your problem')}</span>
                <span className="text-accent-text font-semibold">{t('landing.hero.planes.caption2', 'Click any plane to inspect')}</span>
              </div>
            </div>
          </div>

          {/* Unified 5-Card Feature Row — All 5 cards equidistant in one continuous row */}
          <div className="pt-8 mt-8 border-t border-rule grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
            <div className="p-3.5 bg-[#FFFFFF] border border-rule rounded-[2px] flex flex-col justify-between">
              <div>
                <div className="font-serif font-bold text-[16px] text-ink leading-snug">
                  {t('landing.hero.tile1.title', 'Free, and no lawyer needed to start')}
                </div>
                <div className="text-[12.5px] text-ink-tertiary mt-1.5 leading-relaxed">
                  {t('landing.hero.tile1.desc', 'Describe the problem in plain Hindi or English.')}
                </div>
              </div>
            </div>

            <div className="p-3.5 bg-[#FFFFFF] border border-rule rounded-[2px] flex flex-col justify-between">
              <div>
                <div className="font-serif font-bold text-[16px] text-ink leading-snug">
                  {t('landing.hero.tile2.title', 'Every claim traced to a statute')}
                </div>
                <div className="text-[12.5px] text-ink-tertiary mt-1.5 leading-relaxed">
                  {t('landing.hero.tile2.desc', 'Hybrid retrieval across 93 Acts — meaning and keyword search, fused.')}
                </div>
              </div>
            </div>

            <div className="p-3.5 bg-[#FFFFFF] border border-rule rounded-[2px] flex flex-col justify-between">
              <div>
                <div className="font-serif font-bold text-[16px] text-ink leading-snug">
                  {t('landing.hero.tile3.title', 'You leave with a filled-in draft')}
                </div>
                <div className="text-[12.5px] text-ink-tertiary mt-1.5 leading-relaxed">
                  {t('landing.hero.tile3.desc', 'Notice, RTI or appeal — ready to print and post.')}
                </div>
              </div>
            </div>

            <div className="p-3.5 bg-[#FFFFFF] border border-rule rounded-[2px] flex flex-col justify-between">
              <div>
                <div className="font-serif font-bold text-[16px] text-ink leading-snug">
                  {t('landing.hero.tile4.title', 'Dense + sparse hybrid search')}
                </div>
                <div className="text-[12.5px] text-ink-tertiary mt-1.5 leading-relaxed">
                  {t('landing.hero.tile4.desc', 'Chroma vectors fused with BM25 keyword matching across 93 Bare Acts.')}
                </div>
              </div>
            </div>

            <div className="p-3.5 bg-[#FFFFFF] border border-rule rounded-[2px] flex flex-col justify-between">
              <div>
                <div className="font-serif font-bold text-[16px] text-ink leading-snug">
                  {t('landing.hero.tile5.title', 'Zero hallucinated citations')}
                </div>
                <div className="text-[12.5px] text-ink-tertiary mt-1.5 leading-relaxed">
                  {t('landing.hero.tile5.desc', 'Every legal claim is traced to an exact Section of an Act — verifiable before filing.')}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. LIVE AUTO-PLAYING STREAMING PROOF TERMINAL */}
      <section className="py-10 sm:py-14 border-b border-rule bg-paper-sunken">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 space-y-6">
          <div className="space-y-1.5 text-left">
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-accent animate-pulse"></span>
              <span className="text-xs text-accent-text font-bold tracking-widest uppercase">
                {t('landing.proof.live_proof', 'LIVE PROOF')}
              </span>
            </div>
            <h2 className="font-serif text-display-md text-ink font-bold">
              {t('landing.proof.title', 'Multi-Layer Retrieval & Synthesis in Action')}
            </h2>
            <p className="text-base text-ink-tertiary font-sans max-w-4xl">
              {t('landing.proof.description', 'Watch real citizen grievances type in, route through deterministic legal classifiers, fuse Chroma dense + BM25 sparse vectors, and stream into the 5-part invariant dossier.')}
            </p>
          </div>

          {/* Live Streaming Proof Engine — 12-column full width grid with vertical progress rail */}
          <HeroPipelineAnimation 
            onOpenDossierInNavigator={(query) => onStartQuery(query)}
          />
        </div>
      </section>

      {/* 3. FOUR CORE PILLARS OF CIVIC EMPOWERMENT — 2-ZONE COMPOSITION */}
      <section className="py-16 sm:py-20 border-b border-rule bg-paper">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 space-y-8">
          <div className="space-y-1.5 text-left">
            <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded bg-paper-sunken text-xs text-accent-deep font-bold">
              <Sparkles className="w-3.5 h-3.5 text-accent" />
              <span>{t("landing.problemArchitecture", "PROBLEM ARCHITECTURE")}</span>
            </div>
            <h2 className="font-serif text-display-md font-bold text-ink">
              {t('landing.pillars.title', 'Empowering Citizens Across 4 Civic Dimensions')}
            </h2>
            <p className="text-sm text-ink-tertiary font-sans max-w-3xl">
              {t('landing.pillars.subtitle', 'Turning opaque bureaucracy, scattered legislation, and legal intimidation into accessible, grounded, and automated citizen action.')}
            </p>
          </div>

          {/* 2-Column Full Width Editorial Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch pt-2">
            
            {/* Left Column: Numbered Pillar List */}
            <div className="lg:col-span-6 space-y-3 pr-0 lg:pr-4 border-r-0 lg:border-r border-rule">
              {[
                {
                  n: '01',
                  name: t('landing.pillars.rti.name', 'RTI Drafting Agent'),
                  desc: t('landing.pillars.rti.desc', 'Converts plain-language citizen questions into legally formatted RTI Form A applications and Sec 19 First Appeals directed to the exact Public Information Officer.'),
                  query: 'I filed an RTI application 38 days ago with the Municipal Corporation requesting road repair tender details. No response received.',
                  cta: t('landing.pillars.rti.cta', 'Draft RTI Application'),
                  badge: t('landing.pillars.rti.badge', 'FORM A & FIRST APPEAL'),
                },
                {
                  n: '02',
                  name: t('landing.pillars.rights.name', 'Rights Navigator'),
                  desc: t('landing.pillars.rights.desc', 'Translates messy disputes (tenant evictions, consumer defects, unpaid wages) into simple terms backed by citations from 93 Bare Acts and evidence checklists.'),
                  query: 'Authorized service center rejected warranty repair on my 4-month-old laptop claiming customer fault without technical diagnostic inspection.',
                  cta: t('landing.pillars.rights.cta', 'Explore Rights Dossier'),
                  badge: t('landing.pillars.rights.badge', 'EVIDENCE & 93 ACTS'),
                },
                {
                  n: '03',
                  name: t('landing.pillars.schemes.name', 'Scheme Eligibility Reader'),
                  desc: t('landing.pillars.schemes.desc', 'Answers eligibility questions in plain language across healthcare, housing, pensions, and gig worker funds with benefit calculators and document lists.'),
                  query: null,
                  cta: t('landing.pillars.schemes.cta', 'Check Welfare Schemes'),
                  navTab: 'scheme_reader',
                  badge: t('landing.pillars.schemes.badge', 'WELFARE BENEFIT CALCULATOR'),
                },
                {
                  n: '04',
                  name: t('landing.pillars.form.name', 'Conversational Form-Filler'),
                  desc: t('landing.pillars.form.desc', 'Interviews the user in plain English or Hinglish and auto-populates the official legal/civic form in real-time side-by-side ready for filing.'),
                  query: null,
                  cta: t('landing.pillars.form.cta', 'Live Interactive Intake'),
                  navTab: 'form_filler',
                  badge: t('landing.pillars.form.badge', 'HINGLISH INTAKE ENGINE'),
                },
              ].map((item, idx) => {
                const isActive = activePillarIdx === idx;
                return (
                  <div
                    key={item.n}
                    onMouseEnter={() => setActivePillarIdx(idx)}
                    onClick={() => setActivePillarIdx(idx)}
                    className={`group cursor-pointer p-4 transition-all rounded-[4px] border border-transparent ${
                      isActive
                        ? 'bg-white border-l-4 border-l-accent border-rule shadow-xs'
                        : 'hover:bg-paper-sunken hover:border-rule'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-3">
                        <span className={`text-xl font-bold transition-colors ${
                          isActive ? 'text-accent' : 'text-ink-muted'
                        }`}>
                          {item.n}
                        </span>
                        <h3 className={`font-serif font-bold text-lg transition-colors ${
                          isActive ? 'text-ink' : 'text-ink-tertiary'
                        }`}>
                          {item.name}
                        </h3>
                      </div>
                      <span className="text-xs text-ink-muted group-hover:text-accent-hover">
                        {isActive ? t('landing.pillars.active', '● ACTIVE') : '→'}
                      </span>
                    </div>

                    <p className={`text-xs mt-2 leading-relaxed transition-all ${
                      isActive ? 'text-ink font-medium' : 'text-ink-secondary'
                    }`}>
                      {item.desc}
                    </p>
                  </div>
                );
              })}
            </div>

            {/* Right Column: Live Snippet Preview Panel */}
            <div className="lg:col-span-6 bg-white border border-rule rounded-[4px] p-6 shadow-sm flex flex-col justify-between space-y-6">
              
              {/* Dynamic Snippet Mockup Content based on activePillarIdx */}
              {activePillarIdx === 0 && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-rule">
                    <span className="text-xs font-bold text-accent-text">
                      {t('landing.pillars.preview.rti.label', 'PREVIEW // RTI FORM A MEMORANDUM')}
                    </span>
                    <span className="text-[12px] bg-accent/10 text-accent-text px-2 py-0.5 rounded border border-accent/20 font-bold">
                      {t('landing.pillars.preview.rti.sec', 'SEC 6(1) & SEC 19(1)')}
                    </span>
                  </div>

                  <div className="p-4 bg-paper border border-rule rounded-[2px] text-xs space-y-2 text-ink">
                    <div className="text-accent font-bold">{t('landing.pillars.preview.rti.title', 'MEMORANDUM OF FIRST APPEAL')}</div>
                    <div>{t('landing.pillars.preview.rti.to', 'To:')} <span className="underline decoration-dotted">{t('landing.pillars.preview.rti.to_authority', '[First Appellate Authority, Municipal Corporation]')}</span></div>
                    <div className="text-ink-tertiary text-[12px] leading-relaxed">
                      {t('landing.pillars.preview.rti.quote', '"Application dated 15-Jan-2026 regarding Ward 14 Road Repair Tender funds ignored for 38 days. Invoking Section 7(2) Deemed Refusal."')}
                    </div>
                    <div className="pt-2 text-[12px] text-emerald-700 font-bold flex items-center space-x-1">
                      <span>{t('landing.pillars.preview.rti.ready', '✓ PRE-FORMATTED LEGAL DRAFT READY TO PRINT & FILE')}</span>
                    </div>
                  </div>
                </div>
              )}

              {activePillarIdx === 1 && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-rule">
                    <span className="text-xs font-bold text-accent-text">
                      {t('landing.pillars.preview.rights.label', 'PREVIEW // RIGHTS & EVIDENCE DOSSIER')}
                    </span>
                    <span className="text-[12px] bg-blue-50 text-blue-800 px-2 py-0.5 rounded border border-blue-200 font-bold">
                      {t('landing.pillars.preview.rights.badge', '93 BARE ACT CITATION')}
                    </span>
                  </div>

                  <div className="p-4 bg-paper border border-rule rounded-[2px] text-xs space-y-2.5 text-ink">
                    <div className="text-ink font-serif font-bold text-sm">{t('landing.pillars.preview.rights.act', 'Consumer Protection Act 2019 · Sec 84')}</div>
                    <div className="text-[12px] text-ink-secondary">
                      {t('landing.pillars.preview.rights.quote', '"Manufacturer strict product liability for warranty rejection without diagnostic log."')}
                    </div>
                    <div className="pt-1 flex flex-wrap gap-2 text-[12px]">
                      <span className="bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded">{t('landing.pillars.preview.rights.item1', 'Mandatory: Tax Invoice')}</span>
                      <span className="bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded">{t('landing.pillars.preview.rights.item2', 'Mandatory: Job-Sheet')}</span>
                      <span className="bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded">{t('landing.pillars.preview.rights.item3', 'Supporting: Sec 63 BSA Cert')}</span>
                    </div>
                  </div>
                </div>
              )}

              {activePillarIdx === 2 && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-rule">
                    <span className="text-xs font-bold text-accent-text">
                      {t('landing.pillars.preview.schemes.label', 'PREVIEW // WELFARE SCHEME EVALUATOR')}
                    </span>
                    <span className="text-[12px] bg-emerald-50 text-emerald-800 px-2 py-0.5 rounded border border-emerald-200 font-bold">
                      {t('landing.pillars.preview.schemes.badge', 'BENEFIT CALCULATOR')}
                    </span>
                  </div>

                  <div className="p-4 bg-paper border border-rule rounded-[2px] text-xs space-y-2 text-ink">
                    <div className="font-serif font-bold text-sm text-ink">{t('landing.pillars.preview.schemes.scheme_name', 'Ayushman Bharat PM-JAY Scheme')}</div>
                    <div className="text-emerald-700 font-bold">{t('landing.pillars.preview.schemes.coverage', 'STATUTORY COVERAGE: ₹5,00,000 / FAMILY / YEAR')}</div>
                    <div className="text-[12px] text-ink-tertiary">
                      {t('landing.pillars.preview.schemes.eligibility', 'Eligible: Deprivation D1-D7 criteria under SECC 2011 + Ration Card holder status.')}
                    </div>
                    <div className="text-[12px] text-ink-muted">
                      {t('landing.pillars.preview.schemes.required', 'Required: Aadhaar + SECC Household ID + Empanelled Hospital list.')}
                    </div>
                  </div>
                </div>
              )}

              {activePillarIdx === 3 && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-rule">
                    <span className="text-xs font-bold text-accent-text">
                      {t('landing.pillars.preview.form.label', 'PREVIEW // CONVERSATIONAL INTAKE ENGINE')}
                    </span>
                    <span className="text-[12px] bg-purple-50 text-purple-800 px-2 py-0.5 rounded border border-purple-200 font-bold">
                      {t('landing.pillars.preview.form.badge', 'HINGLISH & ENGLISH')}
                    </span>
                  </div>

                  <div className="p-4 bg-paper border border-rule rounded-[2px] text-xs space-y-2 text-ink">
                    <div className="text-ink-muted text-[12px]">{t('landing.pillars.preview.form.user_text', 'User: "Landlord 7 days me nikalne ko bol raha hai whatsapp par."')}</div>
                    <div className="text-accent font-bold">{t('landing.pillars.preview.form.ai_text', 'AI Assistant: "Sec 106 TPA applies. 15-day written notice is statutory requirement. Auto-filling Reply Notice."')}</div>
                    <div className="pt-1 text-[12px] text-emerald-700 font-bold">
                      {t('landing.pillars.preview.form.ready', '✓ SIDE-BY-SIDE AUTO-POPULATED OFFICIAL LEGAL FORM')}
                    </div>
                  </div>
                </div>
              )}

              {/* Action Button */}
              <div className="pt-4 border-t border-rule flex items-center justify-between">
                <span className="text-xs text-ink-muted">
                  {t('landing.pillars.module_prefix', 'CIVIC MODULE 0')}{activePillarIdx + 1}
                </span>
                <button
                  onClick={() => {
                    const pillarQueries = [
                      t('landing.pillars.rti.preset_query', 'I filed an RTI application 38 days ago with the Municipal Corporation requesting road repair tender details. No response received.'),
                      t('landing.pillars.rights.preset_query', 'Authorized service center rejected warranty repair on my 4-month-old laptop claiming customer fault without technical diagnostic inspection.'),
                      t('landing.pillars.schemes.preset_query', 'Ayushman Bharat PMJAY scheme eligibility criteria'),
                      t('landing.pillars.form.preset_query', 'File RTI Form A')
                    ];
                    const navTabs = [null, null, 'scheme_reader', 'form_filler'];
                    const targetTab = navTabs[activePillarIdx];
                    if (targetTab && onNavigateToTab) {
                      onNavigateToTab(targetTab);
                    } else {
                      onStartQuery(pillarQueries[activePillarIdx]);
                    }
                  }}
                  className="px-5 py-2.5 bg-dark hover:bg-dark-rule text-white text-xs font-bold rounded-[2px] transition-colors flex items-center space-x-2 group focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none"
                >
                  <span>{t('landing.pillars.launch', 'LAUNCH THIS MODULE')}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-accent group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* 4. SEQUENTIAL LINE-BY-LINE TEXT REVEAL ON SCROLL */}
      <ScrollRevealSection />


      {/* 5. PINNED 5-PART CASE FILE ARCHITECTURE SHOWCASE */}
      <section className="py-16 flex flex-col justify-center border-b border-rule bg-paper">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="max-w-3xl mb-12 space-y-2">
            <span className="text-xs text-accent-text font-bold tracking-widest uppercase">
              {t('landing.dossier.badge', 'STRUCTURED OUTPUT STANDARD')}
            </span>
            <h2 className="font-serif text-display-md text-ink font-bold">
              {t('landing.dossier.title', 'The Five-Part Case Dossier')}
            </h2>
            <p className="text-base text-ink-tertiary font-sans">
              {t('landing.dossier.subtitle', 'Unlike generic chatbots that hallucinate citations, NYAAY AI structures every legal solution into an invariant, courtroom-tested shape.')}
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Left Tabs */}
            <div className="lg:col-span-5 space-y-2.5">
              {fivePartArchitecture.map((item, idx) => {
                const IconComponent = item.icon;
                const isActive = activeStepPinned === idx;
                return (
                  <button
                    key={item.index}
                    onClick={() => setActiveStepPinned(idx)}
                    className={`w-full text-left p-4 border transition-all rounded-[2px] flex items-start space-x-3.5 focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none ${
                      isActive
                        ? 'border-dark bg-white shadow-xs ring-1 ring-dark/10'
                        : 'border-rule bg-paper-sunken/60 hover:bg-paper-sunken text-ink-tertiary'
                    }`}
                  >
                    <div className={`p-2 rounded-[2px] ${isActive ? 'bg-dark text-white' : 'bg-rule text-ink-tertiary'}`}>
                      <IconComponent className="w-4 h-4" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="text-[12px] font-bold text-accent-text uppercase">
                          {t('landing.dossier.part_prefix', 'PART 0')}{item.index} · {item.badge}
                        </span>
                        <span className="text-[12px] text-ink-muted">{t('landing.dossier.step_prefix', 'STEP ')}{item.index}{t('landing.dossier.step_of', ' OF 5')}</span>
                      </div>
                      <div className="font-serif font-bold text-base text-ink mt-0.5">
                        {item.name}
                      </div>
                      <p className="text-xs text-ink-tertiary mt-1 line-clamp-1 font-sans">
                        {item.title}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Right: Pinned Dossier Preview Card */}
            <div className="lg:col-span-7">
              <div className="sticky top-24 border border-dark bg-white rounded-[2px] shadow-sm overflow-hidden">
                {/* Dossier Header */}
                <div className="bg-dark text-paper px-6 py-3.5 flex items-center justify-between border-b border-rule-dark">
                  <div className="flex items-center space-x-3">
                    <span className="text-xs text-accent-text font-bold">
                      {t('landing.dossier.section_prefix', 'SECTION 0')}{fivePartArchitecture[activeStepPinned].index}
                    </span>
                    <span className="text-xs text-slate">
                      {fivePartArchitecture[activeStepPinned].badge}
                    </span>
                  </div>
                  {/* On #121820, #667085 is 3.70:1 — fails AA. #7A8699 is 4.84:1
                      and still reads below the #A2B1C6 badge beside it. */}
                  <div className="text-[12px] text-slate-muted">
                    {t('landing.dossier.grounded_view', 'GROUNDED DOSSIER VIEW')}
                  </div>
                </div>

                {/* Dossier Body */}
                <div className="p-6 sm:p-8 space-y-6">
                  <div>
                    <h3 className="font-serif text-heading text-ink font-bold">
                      {fivePartArchitecture[activeStepPinned].title}
                    </h3>
                    <p className="text-sm text-ink-secondary mt-2 font-sans leading-relaxed">
                      {fivePartArchitecture[activeStepPinned].description}
                    </p>
                  </div>

                  {/* Highlighted Statutory Box */}
                  <div className="p-4 bg-paper border-l-3 border-accent border-y border-r border-rule space-y-2">
                    <div className="text-[12px] text-accent-text font-bold uppercase tracking-wider">
                      {t('landing.dossier.retrieval_annotation', '// REAL-TIME RETRIEVAL ANNOTATION')}
                    </div>
                    <p className="font-serif text-base text-ink italic">
                      "{fivePartArchitecture[activeStepPinned].dossierHighlight}"
                    </p>
                  </div>

                  {/* Actions inside dossier preview */}
                  <div className="pt-4 border-t border-rule flex items-center justify-between">
                    <span className="text-xs text-ink-muted">
                      {t('landing.dossier.sectors', 'SECTORS: RTI • CONSUMER • TENANT • RERA')}
                    </span>
                    <button
                      onClick={() => {
                        const tabMapping: Array<'evidence' | 'action_plan' | 'drafter' | null> = [
                          null,
                          'evidence',
                          null,
                          'action_plan',
                          'drafter'
                        ];
                        const targetTab = tabMapping[activeStepPinned];
                        if (targetTab && onNavigateToTab) {
                          onNavigateToTab(targetTab);
                        } else {
                          onStartQuery(fivePartArchitecture[activeStepPinned].dossierHighlight);
                        }
                      }}
                      className="px-4 py-2 bg-dark hover:bg-dark-rule text-paper text-xs font-bold rounded-[2px] transition-colors flex items-center space-x-1.5 focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none cursor-pointer"
                    >
                      <span>{t('landing.dossier.test_module', 'TEST THIS MODULE')}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-accent" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 6. COMMON CIVIC SCENARIOS — POLISHED CAROUSEL */}
      <section className="py-12 sm:py-16 border-b border-rule bg-paper">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 space-y-6">
          
          {/* Header + Controls */}
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="text-xs text-accent-text font-bold tracking-widest uppercase">
                  {t('landing.scenarios.badge', 'TEST GROUNDED DISPUTES')}
                </span>
                <span className="text-[12px] bg-paper-sunken border border-rule px-2 py-0.5 rounded font-mono font-bold text-ink-muted">
                  {t('landing.scenarios.benchmark', '5 BENCHMARK SCENARIOS')}
                </span>
              </div>
              <h2 className="font-serif text-display-md text-ink font-bold">
                {t('landing.scenarios.title', 'Common Civic Scenarios')}
              </h2>
            </div>
            
            <div className="flex items-center space-x-4">
              <p className="hidden md:block text-xs text-ink-muted max-w-sm text-right">
                {t('landing.scenarios.subtitle', 'Select any benchmark scenario to test real-world statutory grounding.')}
              </p>

              {/* Carousel Arrow Controls */}
              <div className="flex items-center space-x-1.5">
                <button
                  onClick={() => {
                    scenarioScrollRef.current?.scrollBy({ left: -360, behavior: 'smooth' });
                  }}
                  className="p-2.5 bg-white border border-rule hover:border-dark text-ink rounded-[2px] shadow-2xs transition-colors focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none cursor-pointer"
                  title={t('landing.scenarios.scroll_left', 'Scroll left')}
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>

                <button
                  onClick={() => {
                    scenarioScrollRef.current?.scrollBy({ left: 360, behavior: 'smooth' });
                  }}
                  className="p-2.5 bg-white border border-rule hover:border-dark text-ink rounded-[2px] shadow-2xs transition-colors focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none cursor-pointer"
                  title={t('landing.scenarios.scroll_right', 'Scroll right')}
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Horizontal scroll strip with visible peek-bleed */}
          <div className="relative">
            <div 
              ref={scenarioScrollRef}
              className="flex gap-4 overflow-x-auto pb-4 scrollbar-none scroll-smooth snap-x snap-mandatory"
            >
              {sampleCivicDisputes.map((scenario, idx) => (
                <div
                  key={idx}
                  onClick={() => onStartQuery(scenario.query)}
                  className="group cursor-pointer flex-shrink-0 w-[290px] sm:w-[340px] p-5 border border-rule bg-white hover:border-accent hover:shadow-md hover:-translate-y-1 transition-all duration-200 rounded-[4px] flex flex-col justify-between space-y-4 snap-start"
                  tabIndex={0}
                  role="button"
                  onKeyDown={(e) => { if (e.key === 'Enter') onStartQuery(scenario.query); }}
                >
                  <div className="space-y-2.5">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-accent-text uppercase tracking-wider bg-accent/10 px-2 py-0.5 rounded-[2px] border border-accent/20">
                        {scenario.domain} · {scenario.badge}
                      </span>
                      <span className="text-[12px] text-ink-muted group-hover:text-accent font-bold flex items-center space-x-1 transition-colors">
                        <span>{t('landing.scenarios.launch', 'LAUNCH')}</span>
                        <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
                      </span>
                    </div>

                    <h4 className="font-serif font-bold text-base text-ink group-hover:text-accent-hover transition-colors leading-snug">
                      {scenario.title}
                    </h4>

                    <p className="text-xs text-ink-secondary font-sans leading-relaxed line-clamp-3">
                      "{scenario.query}"
                    </p>
                  </div>

                  <div className="pt-3 border-t border-paper-sunken flex items-center justify-between text-[12px] text-ink-muted">
                    <span className="truncate max-w-[200px] font-mono">{t('landing.scenarios.grounded', 'GROUNDED:')} {scenario.statute}</span>
                    <span className="text-emerald-700 font-bold flex-shrink-0 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200 text-[11px]">{t('landing.scenarios.ready', 'READY')}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination Indicators */}
            <div className="flex items-center justify-center gap-2 pt-2">
              {sampleCivicDisputes.map((_, i) => (
                <button
                  key={i}
                  onClick={() => {
                    if (scenarioScrollRef.current) {
                      scenarioScrollRef.current.scrollTo({ left: i * 350, behavior: 'smooth' });
                    }
                  }}
                  className="w-2 h-2 rounded-full bg-rule-strong hover:bg-accent transition-colors"
                  aria-label={t('landing.scenarios.go_to', 'Go to scenario {{number}}', { number: i + 1 })}
                />
              ))}
            </div>
          </div>

        </div>
      </section>

      {/* 7. STATUTORY REPOSITORY BANNER */}
      <section className="py-16 flex flex-col justify-center bg-paper border-b border-rule text-ink">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-2">
            <span className="text-xs text-accent-text font-bold tracking-widest uppercase">
              {t('landing.repository.badge', 'KNOWLEDGE BASE')}
            </span>
            <h2 className="font-serif text-display-md font-bold text-ink">
              {t('landing.repository.title', 'Explore the 93 Indian Bare Acts Catalog')}
            </h2>
            <p className="text-sm text-ink-secondary max-w-xl font-sans">
              {t('landing.repository.subtitle', 'From the Constitution of India to the Consumer Protection Act 2019, Transfer of Property Act 1882, and modern procedural enactments.')}
            </p>
          </div>

          <button
            onClick={onExploreActs}
            className="px-6 py-3.5 bg-dark hover:bg-dark-rule text-paper text-xs font-bold rounded-[2px] transition-colors shrink-0 flex items-center space-x-2 focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none cursor-pointer active:translate-y-0.5 shadow-sm"
          >
            <BookOpen className="w-4 h-4 text-accent" />
            <span>{t('landing.repository.cta', 'OPEN 93 ACTS REPOSITORY')}</span>
          </button>
        </div>
      </section>

      {/* Statute Inspection Modal */}
      <StatuteInspectionModal
        act={inspectingAct}
        isOpen={!!inspectingAct}
        onClose={() => setInspectingAct(null)}
        onQueryThisAct={(act) => {
          onStartQuery(t('landing.modal.query_act', 'Citizen dispute involving rights and remedies under {{title}} ({{actCode}})', { title: act.title, actCode: act.actCode }));
        }}
      />
    </div>
  );
};

/* Isolated ScrollRevealSection — manages its own scroll listener to prevent parent re-renders */
const ScrollRevealSection: React.FC = React.memo(() => {
  const scrollSectionRef = useRef<HTMLDivElement>(null);
  const [scrollProgress, setScrollProgress] = useState<number>(0);
  const { t } = useTranslation();

  useEffect(() => {
    let ticking = false;
    const handleScroll = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          if (scrollSectionRef.current) {
            const rect = scrollSectionRef.current.getBoundingClientRect();
            const windowH = window.innerHeight;
            const progress = Math.min(1, Math.max(0, (windowH - rect.top) / (rect.height + windowH)));
            setScrollProgress(progress);
          }
          ticking = false;
        });
        ticking = true;
      }
    };

    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    window.addEventListener('resize', handleScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('resize', handleScroll);
    };
  }, []);

  return (
    <section 
      ref={scrollSectionRef} 
      className="min-h-[70vh] py-16 bg-dark text-paper border-t-2 border-accent border-b-2 border-accent relative overflow-hidden transform-gpu flex flex-col justify-center"
    >
      <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#FAF7F2_1px,transparent_1px)] [background-size:24px_24px]" />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 relative z-10 space-y-10">
        <div className="text-xs text-accent-text tracking-widest uppercase font-bold flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-accent inline-block"></span>
          <span>{t('landing.scroll_reveal.badge', 'CIVIC REALITY & PROBLEM STATEMENT')}</span>
        </div>

        <div className="space-y-6 font-serif text-2xl sm:text-4xl lg:text-5xl leading-[1.3] font-medium tracking-tight">
          <p 
            className={`transition-colors duration-200 ease-out ${
              scrollProgress > 0.08 ? 'text-paper font-semibold' : 'text-slate-muted'
            }`}
          >
            {t('landing.scroll_reveal.line1', 'A citizen enters with raw real-world distress.')}
          </p>

          <p 
            className={`transition-colors duration-200 ease-out ${
              scrollProgress > 0.20 ? 'text-paper font-semibold' : 'text-slate-muted'
            }`}
          >
            {t('landing.scroll_reveal.line2', 'Bureaucracy buries rights under ninety-three disconnected statutes.')}
          </p>

          <p 
            className={`transition-colors duration-200 ease-out ${
              scrollProgress > 0.32 ? 'text-accent font-bold italic' : 'text-slate-muted'
            }`}
          >
            {t('landing.scroll_reveal.line3', 'The law already protects you — most people just cannot find the path through it.')}
          </p>
        </div>

        <div className="pt-8 border-t border-rule-dark flex flex-wrap items-center justify-between gap-4 text-xs text-slate-muted">
          <div>{t('landing.scroll_reveal.footer1', 'NYAAY ENGINE: RETRIEVAL-AUGMENTED STATUTORY DOSSIER')}</div>
          <div className="text-accent font-semibold">{t('landing.scroll_reveal.footer2', 'DETERMINISTIC JURISDICTION ROUTING')}</div>
        </div>
      </div>
    </section>
  );
});