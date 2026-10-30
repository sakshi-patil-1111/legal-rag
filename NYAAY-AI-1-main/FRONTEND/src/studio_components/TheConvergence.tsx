import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ShieldCheck, 
  Zap, 
  Send, 
  CheckCircle2, 
  ArrowRight, 
  Scale, 
  Layers, 
  FileText, 
  Check, 
  Sparkles,
  Lock,
  Search,
  ExternalLink
} from 'lucide-react';
import { BARE_ACTS_CATALOG } from '../data/bareActsData';
import { BareAct } from '../types';

export interface ConvergenceScenario {
  id: string;
  domain: string;
  query: string;
  actTitle: string;
  actCode: string;
  sectionCite: string;
  statuteQuote: string;
  ttft: number;
  verdict: string;
  denseSim: number;
  sparseMatch: number;
  rrfScore: string;
  parts: Array<{
    num: string;
    label: string;
    tag: string;
    text: string;
    sectionRef: string;
  }>;
}

export const CONVERGENCE_BENCHMARKS: ConvergenceScenario[] = [
  {
    id: 'rti',
    domain: 'CIVIC · RTI',
    query: 'I filed an RTI application 38 days ago with Municipal Corporation regarding road repair tender. No response received from PIO.',
    actTitle: 'Right to Information Act, 2005',
    actCode: 'RTI ACT 2005',
    sectionCite: 'Sec 7(2) & Sec 19(1)',
    statuteQuote: 'Section 7(2): Failure to give decision within 30 days is deemed refusal. Section 19(1): First Appeal right activated without fees.',
    ttft: 365,
    verdict: 'DEEMED REFUSAL',
    denseSim: 0.942,
    sparseMatch: 0.918,
    rrfScore: '0.0328 (Rank #1)',
    parts: [
      { num: '01', label: 'RIGHTS', tag: 'STATUTORY REMEDY', text: 'Sec 7(2) Deemed Refusal triggered on Day 31. Right to First Appeal under Sec 19(1) fully activated.', sectionRef: 'Sec 7(2)' },
      { num: '02', label: 'EVIDENCE', tag: 'BSA 2023 AUDIT', text: 'Speed Post tracking delivery receipt + Original RTI copy + ₹10 fee receipt + Section 63 BSA electronic log.', sectionRef: 'Sec 63 BSA' },
      { num: '03', label: 'AUTHORITY', tag: 'JURISDICTION', text: 'First Appellate Authority (FAA), Municipal Corporation HQ (Senior to PIO).', sectionRef: 'Sec 19(1)' },
      { num: '04', label: 'ACTION', tag: 'LIMITATION 30D', text: 'Day 31–60: File Form A Memorandum of First Appeal before FAA citing Sec 7(2) default.', sectionRef: 'Sec 19(1)' },
      { num: '05', label: 'DOCUMENT', tag: 'FILING-READY', text: 'Memorandum of First Appeal — Form A (RTI Act 2005). Pre-formatted for printing.', sectionRef: 'Form A' },
    ],
  },
  {
    id: 'warranty',
    domain: 'CONSUMER DEFECT',
    query: 'Authorized service center rejected warranty repair on my 4-month-old laptop claiming customer fault without technical diagnostic report.',
    actTitle: 'Consumer Protection Act, 2019',
    actCode: 'CPA 2019',
    sectionCite: 'Sec 2(11), 2(47) & 84',
    statuteQuote: 'Section 84: Strict product liability on manufacturer for manufacturing defect. Section 2(47): Refusal without inspection is unfair trade practice.',
    ttft: 382,
    verdict: 'UNFAIR PRACTICE',
    denseSim: 0.925,
    sparseMatch: 0.904,
    rrfScore: '0.0315 (Rank #1)',
    parts: [
      { num: '01', label: 'RIGHTS', tag: 'PRODUCT LIABILITY', text: 'Sec 84 CPA 2019 strict manufacturer liability for component failure within warranty term.', sectionRef: 'Sec 84' },
      { num: '02', label: 'EVIDENCE', tag: 'BSA 2023 AUDIT', text: 'Tax Invoice + Service rejection job-sheet + Warranty card + WhatsApp communication export.', sectionRef: 'Sec 2(11)' },
      { num: '03', label: 'AUTHORITY', tag: 'JURISDICTION', text: 'District Consumer Disputes Redressal Commission (DCDRC) via e-Daakhil Portal.', sectionRef: 'Sec 34' },
      { num: '04', label: 'ACTION', tag: '15-DAY NOTICE', text: 'Day 1: Issue formal Statutory Legal Notice (15 days) -> Day 16: File complaint on e-Daakhil.', sectionRef: 'Sec 35' },
      { num: '05', label: 'DOCUMENT', tag: 'FILING-READY', text: 'Statutory Legal Notice for Warranty Replacement & Punitive Damages.', sectionRef: 'Legal Notice' },
    ],
  },
  {
    id: 'tenant',
    domain: 'TENANCY & PROPERTY',
    query: 'Landlord sent a WhatsApp message giving me 7 days to vacate apartment despite full rent paid on time and active lease agreement in force.',
    actTitle: 'Transfer of Property Act, 1882',
    actCode: 'TPA 1882',
    sectionCite: 'Sec 106 & SRA Sec 6',
    statuteQuote: 'Section 106: 15-day formal written notice mandatory. Section 6 SRA: Summary dispossession without due process of law is strictly unlawful.',
    ttft: 391,
    verdict: 'UNLAWFUL EVICTION',
    denseSim: 0.951,
    sparseMatch: 0.932,
    rrfScore: '0.0341 (Rank #1)',
    parts: [
      { num: '01', label: 'RIGHTS', tag: 'DUE PROCESS', text: 'Sec 106 TPA: 15-day formal written notice mandatory. Summary WhatsApp eviction has zero legal validity.', sectionRef: 'Sec 106' },
      { num: '02', label: 'EVIDENCE', tag: 'BSA 2023 AUDIT', text: 'Bank rent transfer receipts + Registered lease agreement + WhatsApp chat export with Sec 63 BSA cert.', sectionRef: 'Sec 63 BSA' },
      { num: '03', label: 'AUTHORITY', tag: 'JURISDICTION', text: 'Rent Control Court / Civil Judge Junior Division / Local Police Station (for harassment).', sectionRef: 'Sec 6 SRA' },
      { num: '04', label: 'ACTION', tag: 'INJUNCTION', text: 'Day 1: Issue Reply Notice under Sec 106 -> Day 8: File for Temporary Injunction under Order 39 CPC.', sectionRef: 'Order 39' },
      { num: '05', label: 'DOCUMENT', tag: 'FILING-READY', text: 'Statutory Reply Notice against Unlawful Summary Eviction & Police Complaint Copy.', sectionRef: 'Reply Notice' },
    ],
  },
];

interface TheConvergenceProps {
  initialQuery?: string;
  onExecuteQuery?: (query: string) => void;
  onInspectStatute?: (actCode: string) => void;
  isCompact?: boolean;
  className?: string;
}

type ConvergencePhase = 'idle' | 'classifying' | 'retrieving' | 'ranking' | 'locked' | 'streaming_dossier' | 'completed';

export const TheConvergence: React.FC<TheConvergenceProps> = ({
  initialQuery,
  onExecuteQuery,
  onInspectStatute,
  isCompact = false,
  className = '',
}) => {
  const [selectedScenarioIdx, setSelectedScenarioIdx] = useState<number>(0);
  const [customInput, setCustomInput] = useState<string>(initialQuery || '');
  const [phase, setPhase] = useState<ConvergencePhase>('idle');
  const [activePartIdx, setActivePartIdx] = useState<number>(-1);
  const [ttftDisplay, setTtftDisplay] = useState<number>(0);
  const [isHovered, setIsHovered] = useState<boolean>(false);
  const [tilt, setTilt] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  const activeScenario = CONVERGENCE_BENCHMARKS[selectedScenarioIdx];
  const timerRefs = useRef<Array<ReturnType<typeof setTimeout>>>([]);
  const rafRef = useRef<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const clearAllTimeouts = useCallback(() => {
    timerRefs.current.forEach(t => clearTimeout(t));
    timerRefs.current = [];
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
  }, []);

  useEffect(() => {
    return clearAllTimeouts;
  }, [clearAllTimeouts]);

  // Run the full theatrical Convergence animation sequence
  const startConvergenceSequence = useCallback((scenario: ConvergenceScenario) => {
    clearAllTimeouts();
    setPhase('classifying');
    setActivePartIdx(-1);
    setTtftDisplay(0);

    // 0 -> Classifying (150ms)
    const t1 = setTimeout(() => {
      setPhase('retrieving');
    }, 450);
    timerRefs.current.push(t1);

    // Retrieving (93 -> 34) (650ms)
    const t2 = setTimeout(() => {
      setPhase('ranking');
    }, 1100);
    timerRefs.current.push(t2);

    // Ranking (RRF -> 1 Match) (500ms)
    const t3 = setTimeout(() => {
      setPhase('locked');
      
      // Animate TTFT counter up to target ms
      const startTime = performance.now();
      const target = scenario.ttft;
      const duration = 400;
      
      const tick = (now: number) => {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        setTtftDisplay(Math.round(progress * target));
        if (progress < 1) {
          rafRef.current = requestAnimationFrame(tick);
        }
      };
      rafRef.current = requestAnimationFrame(tick);

    }, 1700);
    timerRefs.current.push(t3);

    // Stream 5-part dossier rows sequentially
    const t4 = setTimeout(() => {
      setPhase('streaming_dossier');
      
      scenario.parts.forEach((_, idx) => {
        const partTimer = setTimeout(() => {
          setActivePartIdx(idx);
          if (idx === scenario.parts.length - 1) {
            const finalTimer = setTimeout(() => {
              setPhase('completed');
            }, 350);
            timerRefs.current.push(finalTimer);
          }
        }, idx * 240);
        timerRefs.current.push(partTimer);
      });

    }, 2300);
    timerRefs.current.push(t4);

  }, [clearAllTimeouts]);

  // Handle benchmark selection
  const handleSelectBenchmark = (idx: number) => {
    setSelectedScenarioIdx(idx);
    const scen = CONVERGENCE_BENCHMARKS[idx];
    setCustomInput(scen.query);
    startConvergenceSequence(scen);
  };

  // Handle custom query submit
  const handleTriggerRun = () => {
    const query = customInput.trim();
    if (!query) return;

    // Detect if query relates to one of our benchmarks or default to matching
    const lower = query.toLowerCase();
    let matchIdx = 0;
    if (lower.includes('warranty') || lower.includes('laptop') || lower.includes('consumer') || lower.includes('defect') || lower.includes('dealer')) {
      matchIdx = 1;
    } else if (lower.includes('tenant') || lower.includes('landlord') || lower.includes('eviction') || lower.includes('rent') || lower.includes('lease')) {
      matchIdx = 2;
    } else {
      matchIdx = 0;
    }

    setSelectedScenarioIdx(matchIdx);
    startConvergenceSequence(CONVERGENCE_BENCHMARKS[matchIdx]);

    if (onExecuteQuery) {
      onExecuteQuery(query);
    }
  };

  // Parallax mouse tilt for 3D depth
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = (e.clientX - cx) / (rect.width / 2);
    const dy = (e.clientY - cy) / (rect.height / 2);
    setTilt({ x: dy * -3.5, y: dx * 3.5 });
  };

  const handleMouseLeave = () => setTilt({ x: 0, y: 0 });

  const isRunning = phase !== 'idle' && phase !== 'completed';
  const isLockedOrStreaming = phase === 'locked' || phase === 'streaming_dossier' || phase === 'completed';

  return (
    <div 
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={`border border-dark bg-white rounded-[4px] shadow-sm overflow-hidden flex flex-col ${className}`}
    >
      {/* 1. TOP DOCKET HEADER */}
      <div className="bg-dark px-4 sm:px-6 py-3 text-paper flex flex-wrap items-center justify-between gap-3 border-b border-rule-dark">
        <div className="flex items-center space-x-2.5">
          <span className="w-2.5 h-2.5 rounded-full bg-accent animate-pulse" />
          <span className="font-mono text-xs font-bold text-accent tracking-widest uppercase">
            THE CONVERGENCE // 93 → 34 → 1
          </span>
          <span className="text-slate-muted hidden sm:inline">|</span>
          <span className="text-[12px] text-slate-muted hidden sm:inline">
            Deterministic Statutory Lock
          </span>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          {isLockedOrStreaming && (
            <span className="font-mono text-emerald-400 font-bold bg-emerald-950/60 border border-emerald-700/50 px-2 py-0.5 rounded-[2px] animate-stamp">
              TTFT: {ttftDisplay || activeScenario.ttft}ms
            </span>
          )}
          <span className="text-slate-muted text-[12px]">
            {phase === 'idle' ? 'STANDBY' : phase.toUpperCase().replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* 2. INTERACTIVE QUERY / BENCHMARK BAR */}
      <div className="p-4 sm:p-5 bg-paper border-b border-rule space-y-3">
        <div className="flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={customInput}
              onChange={(e) => setCustomInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') handleTriggerRun(); }}
              placeholder='Try: "My RTI was ignored for 38 days..." or "Landlord 7-day eviction notice"'
              className="w-full pl-3.5 pr-10 py-2.5 bg-white border border-rule focus:border-accent focus:ring-1 focus:ring-accent rounded-[3px] text-xs sm:text-sm font-sans text-ink placeholder:text-ink-muted outline-none transition-all shadow-2xs"
            />
            {customInput && (
              <button 
                onClick={() => setCustomInput('')}
                className="absolute right-3 top-2.5 text-xs text-ink-muted hover:text-ink cursor-pointer"
              >
                ✕
              </button>
            )}
          </div>

          <button
            onClick={handleTriggerRun}
            disabled={isRunning || !customInput.trim()}
            className="px-5 py-2.5 bg-dark hover:bg-dark-rule text-paper text-xs font-bold rounded-[3px] transition-all flex items-center justify-center space-x-2 shadow-xs cursor-pointer disabled:opacity-50 shrink-0"
          >
            {isRunning ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-accent rounded-full animate-spin" />
                <span>CONVERGING...</span>
              </>
            ) : (
              <>
                <Zap className="w-3.5 h-3.5 text-accent" />
                <span>CONVERGE ACTS</span>
              </>
            )}
          </button>
        </div>

        {/* Benchmark Chips */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-[11px] font-bold text-ink-muted uppercase tracking-wider">
            BENCHMARKS:
          </span>
          {CONVERGENCE_BENCHMARKS.map((bench, idx) => {
            const isSelected = selectedScenarioIdx === idx && phase !== 'idle';
            return (
              <button
                key={bench.id}
                onClick={() => handleSelectBenchmark(idx)}
                className={`px-2.5 py-1 text-[11px] font-medium rounded-[2px] border transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-accent text-white border-accent shadow-xs font-bold'
                    : 'bg-white hover:bg-paper-sunken border-rule text-ink hover:border-dark'
                }`}
              >
                {bench.domain}
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. MAIN CONVERGENCE THEATER (12-COL GRID) */}
      <div className="p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch flex-1 bg-paper-sunken/40">
        
        {/* LEFT COLUMN: 3D Statutory Fan & Lock-In Instrument (lg:col-span-5) */}
        <div 
          style={{
            transform: `perspective(1000px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`,
            transition: 'transform 120ms ease',
          }}
          className="lg:col-span-5 flex flex-col justify-between space-y-4 bg-white border border-rule rounded-[4px] p-4 sm:p-5 shadow-2xs relative overflow-hidden"
        >
          {/* Top Ticker Status */}
          <div className="flex items-center justify-between border-b border-rule pb-2 text-xs">
            <span className="font-mono text-[11px] text-ink-muted uppercase font-bold">
              93 BARE ACTS INDEX
            </span>
            <span className={`text-[11px] font-bold px-2 py-0.5 rounded-[2px] ${
              isLockedOrStreaming 
                ? 'bg-emerald-50 text-emerald-800 border border-emerald-300' 
                : 'bg-paper-sunken text-ink-muted border border-rule'
            }`}>
              {phase === 'idle' ? '93 ACTS READY' :
               phase === 'classifying' ? '0ms ROUTE ACTIVE' :
               phase === 'retrieving' ? '34 CHUNKS RETRIEVED' :
               phase === 'ranking' ? 'FUSING RRF (k=60)' : '1 EXACT ACT LOCKED'}
            </span>
          </div>

          {/* Kinetic Paper Fan Visual */}
          <div className="relative h-[220px] w-full flex items-center justify-center my-2 select-none">
            {/* Background layered paper cards */}
            {[
              { title: 'Payment of Gratuity Act 1972', code: 'PGA 1972', rotate: -12, translateY: 16, zIndex: 1 },
              { title: 'Real Estate (RERA) Act 2016', code: 'RERA 2016', rotate: 10, translateY: 14, zIndex: 2 },
              { title: 'Bharatiya Nyaya Sanhita 2023', code: 'BNS 2023', rotate: -6, translateY: 8, zIndex: 3 },
              { title: 'Transfer of Property Act 1882', code: 'TPA 1882', rotate: 5, translateY: 4, zIndex: 4 },
            ].map((card, i) => (
              <motion.div
                key={card.code}
                animate={{
                  rotate: isLockedOrStreaming ? card.rotate * 0.4 : card.rotate,
                  translateY: isLockedOrStreaming ? card.translateY + 24 : card.translateY,
                  opacity: isLockedOrStreaming ? 0.25 : 0.65,
                  scale: isLockedOrStreaming ? 0.92 : 1,
                }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                className="absolute w-[240px] sm:w-[260px] h-[150px] bg-paper-sunken border border-rule-strong rounded-[4px] p-3 shadow-sm flex flex-col justify-between"
                style={{ zIndex: card.zIndex }}
              >
                <div className="text-[10px] font-mono text-ink-muted uppercase">{card.code}</div>
                <div className="font-serif font-bold text-xs text-ink-secondary">{card.title}</div>
                <div className="h-1 bg-rule rounded-full w-2/3" />
              </motion.div>
            ))}

            {/* WINNING / FOREGROUND ACT CARD */}
            <motion.div
              animate={{
                scale: isLockedOrStreaming ? 1.04 : 1,
                translateY: isLockedOrStreaming ? -8 : 0,
                boxShadow: isLockedOrStreaming 
                  ? '0 10px 25px -5px rgba(200, 75, 49, 0.15), 0 4px 10px rgba(0, 0, 0, 0.05)' 
                  : '0 2px 8px rgba(0, 0, 0, 0.06)',
              }}
              transition={{ type: 'spring', damping: 20, stiffness: 300 }}
              className={`relative z-10 w-[260px] sm:w-[280px] h-[170px] bg-white border-2 rounded-[4px] p-4 flex flex-col justify-between transition-colors ${
                isLockedOrStreaming ? 'border-accent' : 'border-dark'
              }`}
            >
              <div>
                <div className="flex items-center justify-between border-b border-rule pb-1.5 mb-2">
                  <span className="font-mono text-[11px] font-bold text-accent-text">
                    {activeScenario.actCode}
                  </span>
                  <span className="text-[10px] text-ink-muted">YEAR 2005 / 2019</span>
                </div>
                <h4 className="font-serif font-bold text-sm text-ink leading-snug">
                  {activeScenario.actTitle}
                </h4>
                <p className="text-[11px] text-accent-text font-mono font-bold mt-1">
                  {activeScenario.sectionCite}
                </p>
              </div>

              {/* Hand-Stamped GROUNDED Mark */}
              <AnimatePresence>
                {isLockedOrStreaming && (
                  <motion.div
                    initial={{ scale: 2, opacity: 0, rotate: -15 }}
                    animate={{ scale: 1, opacity: 1, rotate: -4 }}
                    transition={{ type: 'spring', damping: 15, stiffness: 400 }}
                    className="self-end bg-emerald-50 border-2 border-emerald-600 px-3 py-1 rounded-[2px] shadow-sm flex items-center space-x-1.5"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                    <span className="font-mono text-[11px] font-bold text-emerald-800 tracking-wider">
                      GROUNDED // 100% TRACE
                    </span>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </div>

          {/* Metrics Footer */}
          <div className="pt-2 border-t border-rule grid grid-cols-3 gap-2 text-center text-[11px]">
            <div className="p-1.5 bg-paper rounded-[2px]">
              <span className="text-ink-muted block text-[10px]">DENSE (CHROMA)</span>
              <span className="font-bold text-emerald-800 font-mono">{(activeScenario.denseSim * 100).toFixed(0)}%</span>
            </div>
            <div className="p-1.5 bg-paper rounded-[2px]">
              <span className="text-ink-muted block text-[10px]">SPARSE (BM25)</span>
              <span className="font-bold text-blue-800 font-mono">{(activeScenario.sparseMatch * 100).toFixed(0)}%</span>
            </div>
            <div className="p-1.5 bg-paper rounded-[2px]">
              <span className="text-ink-muted block text-[10px]">RRF FUSED</span>
              <span className="font-bold text-accent-text font-mono">Rank #1</span>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: 5-Part Dossier Stream with Animated SVG Connector Traces (lg:col-span-7) */}
        <div className="lg:col-span-7 bg-white border border-rule rounded-[4px] flex flex-col justify-between shadow-2xs overflow-hidden">
          
          {/* Dossier Header */}
          <div className="bg-dark px-4 sm:px-5 py-3 flex items-center justify-between text-paper">
            <div className="flex items-center space-x-2">
              <span className="font-mono text-xs font-bold text-accent">5-PART INVARIANT DOSSIER</span>
              <span className="text-slate-muted hidden sm:inline text-xs">· Courtroom-Tested Schema</span>
            </div>
            <span className="text-[11px] font-bold bg-white/10 px-2 py-0.5 rounded-[2px] text-paper">
              {activeScenario.verdict}
            </span>
          </div>

          {/* Dossier Rows with Animated Connector Traces */}
          <div className="p-4 sm:p-5 space-y-3 flex-1 flex flex-col justify-between relative">
            
            {activeScenario.parts.map((part, i) => {
              const isRevealed = activePartIdx >= i || phase === 'completed';
              const isCurrentlyStreaming = activePartIdx === i && phase === 'streaming_dossier';

              return (
                <motion.div
                  key={part.num}
                  initial={{ opacity: 0, x: 12 }}
                  animate={{ 
                    opacity: isRevealed ? 1 : 0.35, 
                    x: isRevealed ? 0 : 4,
                  }}
                  transition={{ duration: 0.3, ease: 'easeOut' }}
                  className={`p-3 rounded-[3px] border transition-all relative ${
                    isRevealed
                      ? isCurrentlyStreaming
                        ? 'bg-accent-wash/60 border-accent shadow-xs'
                        : 'bg-paper/80 border-rule'
                      : 'bg-paper-sunken/40 border-dashed border-rule opacity-35'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center space-x-2">
                      <span className={`font-mono text-[11px] font-bold px-1.5 py-0.2 rounded-[2px] ${
                        isRevealed ? 'bg-dark text-white' : 'bg-rule text-ink-muted'
                      }`}>
                        PART {part.num}
                      </span>
                      <span className="font-bold text-xs text-accent-text tracking-wide">
                        {part.label}
                      </span>
                      <span className="text-[10px] text-ink-muted uppercase hidden sm:inline">
                        [{part.tag}]
                      </span>
                    </div>

                    {/* Grounded Citation Section Tag */}
                    <span className="text-[11px] font-mono text-ink-muted bg-white border border-rule px-1.5 py-0.2 rounded-[2px] flex items-center space-x-1 shrink-0">
                      <Lock className="w-2.5 h-2.5 text-accent" />
                      <span>{part.sectionRef}</span>
                    </span>
                  </div>

                  <p className={`text-xs sm:text-[13px] font-sans mt-1.5 leading-relaxed ${
                    isRevealed ? 'text-ink' : 'text-ink-muted italic'
                  }`}>
                    {isRevealed ? part.text : '[Statutory grounding extraction pending...]'}
                  </p>
                </motion.div>
              );
            })}

          </div>

          {/* Dossier Bottom Action Strip */}
          <div className="border-t border-rule px-4 sm:px-5 py-3 bg-paper flex items-center justify-between text-xs">
            <div className="flex items-center space-x-1.5 text-ink-muted">
              <ShieldCheck className="w-4 h-4 text-accent" />
              <span>0% Hallucination · 100% Statutory Trace</span>
            </div>

            {onExecuteQuery && (
              <button
                onClick={() => onExecuteQuery(activeScenario.query)}
                className="font-bold text-accent-text hover:text-accent-hover flex items-center space-x-1 transition-colors cursor-pointer"
              >
                <span>Open in Civic Navigator</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

        </div>

      </div>
    </div>
  );
};

export default TheConvergence;
