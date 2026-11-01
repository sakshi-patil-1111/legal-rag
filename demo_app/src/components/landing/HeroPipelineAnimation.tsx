import React, { useState, useEffect, useRef, useCallback } from 'react';
import { CheckCircle2, Zap, ArrowRight, ShieldCheck } from 'lucide-react';

const SCENARIOS = [
  {
    id: 'rti',
    domain: 'CIVIC · RTI',
    query: 'I filed an RTI application 38 days ago with Municipal Corporation regarding road repair tender. No response received.',
    statute: 'RTI Act 2005 · Sec 7(2) & 19(1)',
    ttft: 365,
    verdict: 'DEEMED REFUSAL',
    parts: [
      { label: 'RIGHTS', text: 'Sec 7(2) — Deemed Refusal after 30 days. First Appeal right activated.' },
      { label: 'EVIDENCE', text: 'Speed Post tracking slip + Original RTI + ₹10 fee receipt.' },
      { label: 'AUTHORITY', text: 'First Appellate Authority (FAA), Municipal Corporation HQ.' },
      { label: 'ACTION', text: 'Day 31: File Memorandum of First Appeal under Sec 19(1).' },
      { label: 'DOCUMENT', text: 'Memorandum of First Appeal — Form A (RTI Act 2005).' },
    ],
  },
  {
    id: 'warranty',
    domain: 'CONSUMER',
    query: 'Authorized service center rejected warranty repair on my 4-month-old laptop claiming customer fault without technical proof.',
    statute: 'Consumer Protection Act 2019 · Sec 2(11) & 84',
    ttft: 382,
    verdict: 'UNFAIR TRADE PRACTICE',
    parts: [
      { label: 'RIGHTS', text: 'Sec 84 — Strict manufacturer liability for manufacturing defects within warranty.' },
      { label: 'EVIDENCE', text: 'Tax invoice + Service rejection job-sheet + Warranty card.' },
      { label: 'AUTHORITY', text: 'District Consumer Disputes Redressal Commission (DCDRC) via e-Daakhil.' },
      { label: 'ACTION', text: 'Day 1: Legal Notice (15 days) → Day 16: File grievance on e-Daakhil portal.' },
      { label: 'DOCUMENT', text: 'Formal Legal Notice for Warranty Replacement & Damages.' },
    ],
  },
  {
    id: 'tenant',
    domain: 'TENANT',
    query: 'Landlord sent a WhatsApp message giving me 7 days to vacate despite full rent paid and active lease agreement.',
    statute: 'TPA 1882 · Sec 106 & SRA Sec 6',
    ttft: 391,
    verdict: 'UNLAWFUL EVICTION',
    parts: [
      { label: 'RIGHTS', text: 'Sec 106 TPA — 15-day formal written notice mandatory for tenancies.' },
      { label: 'EVIDENCE', text: 'Rent payment bank receipts + Registered Lease agreement + WhatsApp chat export.' },
      { label: 'AUTHORITY', text: 'Rent Control Court / Civil Judge Junior Division.' },
      { label: 'ACTION', text: 'Day 1: Reply Notice citing Sec 106 → Day 8: File for injunction if threatened.' },
      { label: 'DOCUMENT', text: 'Statutory Reply Notice against Unlawful Summary Eviction.' },
    ],
  },
];

const TYPING_SPEED = 24;       // ms per char
const PAUSE_AFTER_TYPING = 600; // ms
const FUNNEL_STAGGER = 350;    // ms per funnel step
const TTFT_DURATION = 600;     // ms
const PART_REVEAL_SPEED = 240; // ms per part
const HOLD_AFTER_COMPLETE = 3200; // ms

type Phase = 'typing' | 'funnel' | 'ttft' | 'parts' | 'done';

interface Props {
  onOpenDossierInNavigator?: (query: string) => void;
}

function HeroPipelineAnimationComponent({ onOpenDossierInNavigator }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(true);
  const [scenarioIdx, setScenarioIdx] = useState(0);
  const [phase, setPhase] = useState<Phase>('typing');
  const [typed, setTyped] = useState('');
  const [funnelStep, setFunnelStep] = useState(-1); // 0=acts 1=chunks 2=match
  const [ttftCount, setTtftCount] = useState(0);
  const [activePart, setActivePart] = useState(-1);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const cardRef = useRef<HTMLDivElement>(null);
  const timeoutsRef = useRef<Array<ReturnType<typeof setTimeout>>>([]);
  const rafRef = useRef<number | null>(null);

  // Clear all pending timeouts and animation frames
  const clearAllTimers = useCallback(() => {
    timeoutsRef.current.forEach(t => clearTimeout(t));
    timeoutsRef.current = [];
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
  }, []);

  const addTimeout = useCallback((fn: () => void, delay: number) => {
    const id = setTimeout(() => {
      // Remove from tracking array once fired
      timeoutsRef.current = timeoutsRef.current.filter(t => t !== id);
      fn();
    }, delay);
    timeoutsRef.current.push(id);
    return id;
  }, []);

  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          setIsVisible(entry.isIntersecting);
        });
      },
      { threshold: 0.05 }
    );
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  const scenario = SCENARIOS[scenarioIdx];

  // Advance to next scenario
  const nextScenario = useCallback(() => {
    clearAllTimers();
    setScenarioIdx(i => (i + 1) % SCENARIOS.length);
    setPhase('typing');
    setTyped('');
    setFunnelStep(-1);
    setTtftCount(0);
    setActivePart(-1);
  }, [clearAllTimers]);

  useEffect(() => {
    clearAllTimers();
    if (!isVisible) return;

    if (phase === 'typing') {
      let charIndex = 0;
      const fullText = scenario.query;
      
      const typeChar = () => {
        if (charIndex <= fullText.length) {
          setTyped(fullText.slice(0, charIndex));
          charIndex++;
          addTimeout(typeChar, TYPING_SPEED);
        } else {
          addTimeout(() => setPhase('funnel'), PAUSE_AFTER_TYPING);
        }
      };
      
      addTimeout(typeChar, 80);

    } else if (phase === 'funnel') {
      addTimeout(() => setFunnelStep(0), 100);
      addTimeout(() => setFunnelStep(1), 100 + FUNNEL_STAGGER);
      addTimeout(() => {
        setFunnelStep(2);
        addTimeout(() => setPhase('ttft'), FUNNEL_STAGGER);
      }, 100 + FUNNEL_STAGGER * 2);

    } else if (phase === 'ttft') {
      const target = scenario.ttft;
      const startTime = performance.now();
      
      const tick = (now: number) => {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / TTFT_DURATION, 1);
        setTtftCount(Math.round(progress * target));
        if (progress < 1) {
          rafRef.current = requestAnimationFrame(tick);
        } else {
          addTimeout(() => setPhase('parts'), 200);
        }
      };
      rafRef.current = requestAnimationFrame(tick);

    } else if (phase === 'parts') {
      scenario.parts.forEach((_, idx) => {
        addTimeout(() => {
          setActivePart(idx);
          if (idx === scenario.parts.length - 1) {
            addTimeout(() => setPhase('done'), 300);
          }
        }, (idx + 1) * PART_REVEAL_SPEED);
      });

    } else if (phase === 'done') {
      addTimeout(nextScenario, HOLD_AFTER_COMPLETE);
    }

    return clearAllTimers;
  }, [phase, scenarioIdx, isVisible, scenario, addTimeout, clearAllTimers, nextScenario]);

  // Parallax tilt
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = (e.clientX - cx) / (rect.width / 2);
    const dy = (e.clientY - cy) / (rect.height / 2);
    setTilt({ x: dy * -4, y: dx * 4 });
  };

  const handleMouseLeave = () => setTilt({ x: 0, y: 0 });

  const isComplete = phase === 'done';

  // Compute active pipeline stage index (0..4) for progress rail
  const currentStageIndex = 
    phase === 'done' || phase === 'parts' ? 4 :
    phase === 'ttft' ? 3 :
    phase === 'funnel' ? (funnelStep >= 2 ? 3 : funnelStep >= 1 ? 2 : 1) :
    typed.length > 20 ? 1 : 0;

  const STAGES = [
    { num: '01', name: 'Query', sub: 'Input Intake' },
    { num: '02', name: 'Classify', sub: '0ms Regex Route' },
    { num: '03', name: 'Retrieve', sub: 'Chroma Dense' },
    { num: '04', name: 'Rank', sub: 'BM25 + RRF' },
    { num: '05', name: 'Stream', sub: '5-Part Dossier' },
  ];

  return (
    <div ref={containerRef} className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch w-full">

      {/* ZONE 1: Vertical Progress Rail */}
      <div className="hidden lg:flex lg:col-span-2 flex-col space-y-3 p-4 bg-white border border-rule rounded-[4px] shadow-2xs">
        <div className="text-[12px] font-bold text-ink-muted uppercase tracking-wider pb-2 border-b border-rule">
          PIPELINE STAGE
        </div>
        <div className="relative space-y-4 pt-1 flex-1 flex flex-col justify-between">
          {STAGES.map((stg, idx) => {
            const isCurrent = currentStageIndex === idx;
            const isPassed = currentStageIndex > idx;
            return (
              <div key={stg.num} className="flex items-start space-x-3 relative group">
                {/* Status Dot */}
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[12px] font-bold border transition-all shrink-0 mt-0.5 ${
                  isCurrent
                    ? 'bg-accent text-white border-accent shadow-xs'
                    : isPassed
                    ? 'bg-dark text-white border-dark'
                    : 'bg-paper-sunken text-ink-muted border-rule-strong'
                }`}>
                  {isPassed ? '✓' : stg.num}
                </div>
                {/* Stage Text */}
                <div className="space-y-0.5">
                  <div className={`text-xs font-bold transition-colors ${
                    isCurrent ? 'text-accent' : isPassed ? 'text-ink' : 'text-ink-muted'
                  }`}>
                    {stg.name}
                  </div>
                  <div className="text-[12px] text-ink-muted leading-tight">
                    {stg.sub}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ZONE 2: Input + Funnel */}
      <div className="lg:col-span-4 space-y-4 flex flex-col justify-between">
        {/* Faux terminal input */}
        <div className="bg-paper border border-rule rounded-[4px] p-4 flex-1 flex flex-col justify-between">
          <div>
            <div className="text-[12px] text-ink-muted uppercase tracking-widest mb-2 flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
              CITIZEN QUERY INPUT
            </div>
            <p className="font-sans text-[14px] text-ink leading-relaxed min-h-[64px]">
              {typed}
              {phase === 'typing' && (
                <span className="inline-block w-0.5 h-[1.1em] bg-accent ml-0.5 align-text-bottom animate-cursor-pulse" />
              )}
            </p>
          </div>
          {phase !== 'typing' && (
            <div className="mt-3 flex items-center gap-2">
              <span className="text-[12px] font-bold text-accent-text uppercase tracking-wider bg-accent-wash border border-accent/20 px-2 py-0.5 rounded-[2px]">
                {scenario.domain}
              </span>
            </div>
          )}
        </div>

        {/* RRF Funnel */}
        <div className="grid grid-cols-3 gap-2">
          {[
            { step: 0, label: 'ACTS', from: 93, to: 93, desc: 'Indexed corpus' },
            { step: 1, label: 'CHUNKS', from: 1400, to: 34, desc: 'RRF retrieved' },
            { step: 2, label: 'MATCH', from: null, to: 1, desc: 'ROUTING' },
          ].map(({ step, label, to, desc }) => {
            const isActive = funnelStep >= step;
            return (
              <div
                key={step}
                className={`border rounded-[4px] p-3 transition-all duration-300 ${
                  isActive
                    ? step === 2
                      ? 'bg-emerald-50 border-emerald-300 shadow-2xs'
                      : 'bg-white border-accent/40 shadow-2xs'
                    : 'bg-paper-sunken/60 border-rule'
                }`}
              >
                <div className="text-[12px] text-ink-muted uppercase tracking-wider">{label}</div>
                <div className={`font-bold text-xl transition-all duration-300 ${
                  isActive
                    ? step === 2 ? 'text-emerald-700' : 'text-ink'
                    : 'text-rule-strong'
                }`}>
                  {isActive ? to : '—'}
                </div>
                <div className={`text-[12px] transition-colors ${isActive ? 'text-accent-text' : 'text-ink-muted'}`}>
                  {desc}
                </div>
              </div>
            );
          })}
        </div>

        {/* TTFT Ticker */}
        <div className="min-h-[44px] flex items-center gap-3">
          {(phase === 'ttft' || phase === 'parts' || phase === 'done') ? (
            <>
              <div className="flex-1 bg-white border border-rule rounded-[4px] px-4 py-2.5 flex items-center gap-3 shadow-2xs">
                <Zap className="w-3.5 h-3.5 text-accent flex-shrink-0" />
                <span className="text-xs text-ink-muted">Time-to-First-Token:</span>
                <span className="font-mono font-bold text-sm text-ink tabular-nums">
                  {ttftCount}ms
                </span>
              </div>
              {isComplete && (
                <div className="flex items-center gap-1.5 bg-emerald-50 border border-emerald-300 px-3 py-2 rounded-[4px] animate-stamp-in shadow-2xs">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                  <span className="text-[12px] font-bold text-emerald-700 uppercase tracking-wide">GROUNDED</span>
                </div>
              )}
            </>
          ) : (
            <div className="flex-1 bg-paper-sunken/40 border border-dashed border-rule rounded-[4px] px-4 py-2 flex items-center gap-2 text-xs text-ink-muted">
              <span className="w-1.5 h-1.5 rounded-full bg-ink-muted/50" />
              <span>Awaiting input stream…</span>
            </div>
          )}
        </div>
      </div>

      {/* ZONE 3: 5-Part Dossier Preview with parallax tilt */}
      <div
        ref={cardRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        style={{
          transform: `perspective(800px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`,
          transition: 'transform 120ms ease',
        }}
        className="lg:col-span-6 border border-rule bg-white rounded-[4px] overflow-hidden shadow-sm flex flex-col justify-between"
      >
        {/* Header */}
        <div className="bg-dark px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-[12px] text-accent font-bold tracking-wide">5-PART DOSSIER</span>
            <span className="text-[12px] text-slate-muted hidden sm:inline">{scenario.statute}</span>
          </div>
          {isComplete ? (
            <span className="text-[12px] text-emerald-400 font-bold border border-emerald-700/40 px-1.5 py-0.5 rounded-[2px] bg-emerald-950/30">
              {scenario.verdict}
            </span>
          ) : (
            <span className="text-[12px] text-slate-muted animate-pulse">
              {phase === 'parts' ? 'STREAMING CITATIONS…' : 'RETRIEVAL PIPELINE'}
            </span>
          )}
        </div>

        {/* 5-Part Sections (Structured Preview) */}
        <div className="divide-y divide-rule-strong/40 flex-1 flex flex-col justify-between">
          {scenario.parts.map((part, i) => {
            const revealed = activePart >= i;
            const isCurrentlyStreaming = activePart === i && phase === 'parts';
            return (
              <div
                key={i}
                className={`px-4 py-3 flex gap-3 transition-all duration-300 ${
                  revealed
                    ? isCurrentlyStreaming
                      ? 'bg-accent-wash/40 border-l-2 border-accent'
                      : 'bg-white'
                    : 'bg-paper/40 opacity-40'
                }`}
              >
                <span className={`text-[12px] font-bold uppercase tracking-wider w-[80px] flex-shrink-0 pt-0.5 ${
                  revealed ? 'text-accent-text' : 'text-ink-muted'
                }`}>
                  {part.label}
                </span>
                <p className={`font-sans text-[13px] leading-relaxed flex-1 ${
                  revealed ? 'text-ink' : 'text-ink-muted italic'
                }`}>
                  {revealed ? (
                    part.text
                  ) : (
                    <span className="text-ink-muted text-xs">
                      [Grounded extraction awaiting verification]
                    </span>
                  )}
                </p>
              </div>
            );
          })}
        </div>

        {/* Footer / CTA strip */}
        <div className="border-t border-rule px-4 py-3 bg-paper flex items-center justify-between">
          <div className="text-[12px] text-ink-muted flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-accent" />
            <span>0% Hallucination · 100% Statutory Trace</span>
          </div>
          {onOpenDossierInNavigator && (
            <button
              onClick={() => onOpenDossierInNavigator(scenario.query)}
              className="text-xs font-bold text-accent-text hover:text-accent-hover flex items-center gap-1 transition-colors cursor-pointer"
            >
              <span>Explore in Navigator</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default React.memo(HeroPipelineAnimationComponent);
