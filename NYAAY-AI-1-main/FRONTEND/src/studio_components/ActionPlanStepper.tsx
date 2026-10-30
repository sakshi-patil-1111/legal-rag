import React from 'react';
import { 
  Milestone, 
  Clock, 
  Calendar, 
  CheckCircle2, 
  AlertOctagon, 
  ArrowRight, 
  Printer, 
  Download,
  ShieldAlert
} from 'lucide-react';
import { ActionPlanStep, FivePartCaseDossier } from '../types';

interface ActionPlanStepperProps {
  dossier: FivePartCaseDossier | null;
  onUpdateSteps: (steps: ActionPlanStep[]) => void;
  onGoToNavigator: () => void;
  onGoToDrafter: () => void;
}

export const ActionPlanStepper: React.FC<ActionPlanStepperProps> = ({
  dossier,
  onUpdateSteps,
  onGoToNavigator,
  onGoToDrafter
}) => {
  if (!dossier) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center space-y-4">
        <Milestone className="w-12 h-12 text-ink-muted mx-auto" />
        <h2 className="font-serif text-heading font-bold text-ink">No Active Case Timeline Loaded</h2>
        <p className="text-sm text-ink-tertiary max-w-md mx-auto font-sans">
          To generate a phased statutory action plan, submit your dispute query in the Civic Navigator.
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

  const steps = dossier.actionPlan.steps;

  const handleStepStatus = (stepNumber: number, newStatus: 'pending' | 'in_progress' | 'completed') => {
    const updated = steps.map(s => s.stepNumber === stepNumber ? { ...s, status: newStatus } : s);
    onUpdateSteps(updated);
  };

  const completedCount = steps.filter(s => s.status === 'completed').length;
  const progressPercent = Math.round((completedCount / (steps.length || 1)) * 100);

  const handleDownloadIcs = () => {
    // Generate simple ICS calendar event payload
    const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//NYAAY AI//Civic Legal Limitation Calendar//EN
BEGIN:VEVENT
SUMMARY:NYAAY AI: ${dossier.problemAndRights.docketId} Limitation Deadline
DESCRIPTION:Action step due for ${dossier.problemAndRights.summary}
DTSTART:${new Date().toISOString().replace(/[-:]/g, '').split('.')[0]}Z
DTEND:${new Date(Date.now() + 86400000 * 30).toISOString().replace(/[-:]/g, '').split('.')[0]}Z
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR`;

    const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `NYAAY-Deadline-${dossier.problemAndRights.docketId}.ics`;
    link.click();
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-rule pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="stamp-badge px-2 py-0.5">
              ACTION PLAN // PART 04
            </span>
            <span className="text-xs text-ink-muted">
              DOCKET: {dossier.problemAndRights.docketId}
            </span>
          </div>
          <h1 className="font-serif text-heading font-bold text-ink mt-1">
            Phased Statutory Action Plan & Deadlines
          </h1>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleDownloadIcs}
            className="px-3.5 py-2 border border-rule bg-white hover:bg-paper-sunken text-ink text-xs rounded-[2px] transition-colors flex items-center space-x-1.5"
          >
            <Calendar className="w-3.5 h-3.5 text-accent" />
            <span>EXPORT ICS DEADLINES</span>
          </button>

          <button
            onClick={() => window.print()}
            className="px-3.5 py-2 border border-rule bg-white hover:bg-paper-sunken text-ink text-xs rounded-[2px] transition-colors flex items-center space-x-1.5"
          >
            <Printer className="w-3.5 h-3.5 text-accent" />
            <span>PRINT PLAN</span>
          </button>
        </div>
      </div>

      {/* Progress & Summary Banner */}
      <div className="p-6 bg-dark text-paper rounded-[2px] border border-rule-dark grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
        <div className="md:col-span-8 space-y-2">
          <div className="flex items-center space-x-2">
            <span className="text-accent-text text-xs font-bold uppercase tracking-wider">
              TOTAL ESTIMATED DURATION: ~{dossier.actionPlan.totalEstimatedDays} CALENDAR DAYS
            </span>
            <span className="text-ink-tertiary">|</span>
            <span className="text-slate text-xs">
              LIMITATION ACT 1963 ENFORCED
            </span>
          </div>
          <p className="text-sm text-paper font-sans leading-relaxed">
            Every step is calibrated against mandatory statutory limitation periods. Missing statutory appeal windows forfeits legal remedies.
          </p>
          <div className="w-full bg-dark-raised h-2 rounded-full overflow-hidden">
            <div 
              className="bg-accent h-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        <div className="md:col-span-4 bg-dark-raised p-4 rounded-[2px] border border-rule-dark text-center space-y-1">
          <div className="text-[12px] text-slate uppercase">EXECUTION PROGRESS</div>
          <div className="font-serif font-bold text-3xl text-emerald-400">
            {completedCount} / {steps.length}
          </div>
          <div className="text-[12px] text-ink-tertiary">
            {progressPercent}% MILESTONES COMPLETED
          </div>
        </div>
      </div>

      {/* Phased Timeline Stepper */}
      <div className="space-y-4">
        <div className="text-xs font-bold text-ink uppercase tracking-wider">
          CHRONOLOGICAL EXECUTION TIMELINE:
        </div>

        <div className="space-y-4 relative before:absolute before:top-4 before:bottom-4 before:left-7 before:w-0.5 before:bg-rule">
          {steps.map((step) => (
            <div
              key={step.stepNumber}
              className={`relative z-10 p-6 border rounded-[2px] bg-white transition-all ${
                step.status === 'completed' 
                  ? 'border-dark shadow-xs' 
                  : step.status === 'in_progress' 
                    ? 'border-accent ring-1 ring-accent/30' 
                    : 'border-rule'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                <div className="flex items-start space-x-4 flex-1">
                  <div className={`w-8 h-8 rounded-[2px] flex items-center justify-center text-sm font-bold shrink-0 ${
                    step.status === 'completed'
                      ? 'bg-emerald-800 text-white'
                      : step.status === 'in_progress'
                        ? 'bg-accent text-white'
                        : 'bg-rule text-ink-tertiary'
                  }`}>
                    {step.stepNumber}
                  </div>

                  <div className="space-y-2 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-serif font-bold text-lg text-ink">{step.title}</span>
                      <span className="text-xs px-2 py-0.5 bg-paper text-accent-text border border-accent/20 font-bold rounded-[2px]">
                        {step.timeframe}
                      </span>
                      <span className="text-[12px] text-ink-muted px-1.5 py-0.5 bg-paper-sunken rounded-[2px]">
                        TYPE: {step.actionType}
                      </span>
                    </div>

                    <p className="text-sm text-ink-secondary font-sans leading-relaxed">
                      {step.description}
                    </p>

                    {step.statutoryDeadlineNotice && (
                      <div className="p-2.5 bg-rose-50 border border-rose-200 rounded-[2px] text-xs text-rose-900 flex items-start space-x-2">
                        <AlertOctagon className="w-4 h-4 text-rose-700 shrink-0 mt-0.5" />
                        <span>STATUTORY LIMITATION: {step.statutoryDeadlineNotice}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Status Toggle Buttons */}
                <div className="flex sm:flex-col items-center gap-1.5 shrink-0 text-xs">
                  <button
                    onClick={() => handleStepStatus(step.stepNumber, 'completed')}
                    className={`w-full px-3 py-1.5 rounded-[2px] transition-colors ${
                      step.status === 'completed' 
                        ? 'bg-emerald-800 text-white font-bold' 
                        : 'bg-paper hover:bg-paper-sunken text-ink-tertiary border border-rule'
                    }`}
                  >
                    COMPLETED
                  </button>
                  <button
                    onClick={() => handleStepStatus(step.stepNumber, 'in_progress')}
                    className={`w-full px-3 py-1.5 rounded-[2px] transition-colors ${
                      step.status === 'in_progress' 
                        ? 'bg-accent text-white font-bold' 
                        : 'bg-paper hover:bg-paper-sunken text-ink-tertiary border border-rule'
                    }`}
                  >
                    IN PROGRESS
                  </button>
                  <button
                    onClick={() => handleStepStatus(step.stepNumber, 'pending')}
                    className={`w-full px-3 py-1.5 rounded-[2px] transition-colors ${
                      step.status === 'pending' 
                        ? 'bg-dark text-white font-bold' 
                        : 'bg-paper hover:bg-paper-sunken text-ink-tertiary border border-rule'
                    }`}
                  >
                    PENDING
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom CTA to Document Drafter */}
      <div className="p-6 bg-paper border border-rule rounded-[2px] flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h4 className="font-serif font-bold text-lg text-ink">Ready to execute formal filings?</h4>
          <p className="text-xs text-ink-tertiary font-sans">
            Launch the single-pass drafting engine to assemble your notices and appeals with instant bracketed token replacement.
          </p>
        </div>
        <button
          onClick={onGoToDrafter}
          className="px-5 py-2.5 bg-dark hover:bg-dark-rule text-paper text-xs font-bold rounded-[2px] transition-colors flex items-center space-x-2 shrink-0"
        >
          <span>OPEN DRAFTING TOOL</span>
          <ArrowRight className="w-3.5 h-3.5 text-accent" />
        </button>
      </div>
    </div>
  );
};
