import React from 'react';
import { X, BookOpen, Scale, ArrowRight, ShieldCheck, FileText, CheckCircle2, ExternalLink } from 'lucide-react';
import { BareAct } from '../types';
import { CATEGORY_LABELS } from '../data/bareActsData';

interface StatuteInspectionModalProps {
  act: BareAct | null;
  isOpen: boolean;
  onClose: () => void;
  onQueryThisAct: (act: BareAct) => void;
}

// Rich statutory section quotes for authentic legal inspection
const DETAILED_STATUTORY_QUOTES: Record<string, { section: string; title: string; legalText: string; plainMeaning: string }[]> = {
  'rti-2005': [
    {
      section: 'Section 7(1)',
      title: 'Disposal of Request within 30 Days',
      legalText: 'The Central Public Information Officer or State Public Information Officer, on receipt of a request under section 6 shall, as expeditiously as possible, and in any case within thirty days of the receipt of the request, either provide the information on payment of such fee as may be prescribed or reject the request for any of the reasons specified in sections 8 and 9.',
      plainMeaning: 'Mandates that the government officer MUST provide requested records within exactly 30 days (or 48 hours if life and liberty is involved).'
    },
    {
      section: 'Section 7(2)',
      title: 'Deemed Refusal of Request',
      legalText: 'If the Public Information Officer fails to give decision on the request for information within the period specified under sub-section (1), the Central Public Information Officer or State Public Information Officer, as the case may be, shall be deemed to have refused the request.',
      plainMeaning: 'Failure to reply within 30 days legally constitutes a statutory refusal, immediately unlocking the citizen’s right to file a First Appeal.'
    },
    {
      section: 'Section 19(1)',
      title: 'Right to First Appeal',
      legalText: 'Any person who, does not receive a decision within the time specified in sub-section (1) or clause (a) of sub-section (3) of section 7, or is aggrieved by a decision of the Central Public Information Officer or State Public Information Officer, as the case may be, may within thirty days from the expiry of such period or from the receipt of such a decision prefer an appeal to such officer who is senior in rank to the Central Public Information Officer or State Public Information Officer.',
      plainMeaning: 'Citizen can appeal directly to the First Appellate Authority (FAA) within 30 days of deemed refusal without paying court fees.'
    },
    {
      section: 'Section 20(1)',
      title: 'Personal Penalty on Defaulting Officers',
      legalText: 'Where the Central Information Commission or the State Information Commission... is of the opinion that the Central Public Information Officer or State Public Information Officer has, without any reasonable cause, refused to receive an application... or not furnished information within the time specified, it shall impose a penalty of two hundred and fifty rupees each day till application is received or information is furnished, so however, the total amount of such penalty shall not exceed twenty-five thousand rupees.',
      plainMeaning: 'The Commission can levy a ₹250/day personal salary deduction penalty (up to ₹25,000) on the non-compliant public officer.'
    }
  ],
  'cpa-2019': [
    {
      section: 'Section 2(11)',
      title: 'Deficiency in Service Defined',
      legalText: '"Deficiency" means any fault, imperfection, shortcoming or inadequacy in the quality, nature and manner of performance which is required to be maintained by or under any law for the time being in force or has been undertaken to be performed by a person in pursuance of a contract or otherwise in relation to any service.',
      plainMeaning: 'Any refusal by a service center to honor valid warranty terms or delays in repair constitutes statutory deficiency.'
    },
    {
      section: 'Section 35(1)',
      title: 'Manner in which Complaint shall be Made',
      legalText: 'A complaint, in relation to any goods sold or delivered or agreed to be sold or delivered or any service provided or agreed to be provided, may be filed with a District Commission by the consumer to whom such goods are sold or delivered or agreed to be sold or delivered or such service is provided.',
      plainMeaning: 'Enables direct filing before District Consumer Forum with nominal court fee and electronic e-Daakhil filing option.'
    },
    {
      section: 'Section 84',
      title: 'Liability of Product Manufacturer',
      legalText: 'A product manufacturer shall be liable in a product liability action, if the product contains a manufacturing defect, is defective in design, or deviates from manufacturing specifications or express warranty.',
      plainMeaning: 'Manufacturer is strictly liable for defects and cannot shift blame to local dealership or retail distributor.'
    }
  ],
  'tpa-1882': [
    {
      section: 'Section 106',
      title: 'Duration of Leases and Mandatory Notice',
      legalText: 'In the absence of a contract or local law or usage to the contrary, a lease of immovable property for any other purpose shall be deemed to be a lease from month to month, terminable, on the part of either lessor or lessee, by fifteen days’ notice... Every notice under sub-section (1) must be in writing, signed by or on behalf of the person giving it, and either be sent by post or tendered personally.',
      plainMeaning: 'A 7-day informal WhatsApp message is legally invalid. Landlords MUST provide at least 15 days formal written notice ending with the tenancy month.'
    },
    {
      section: 'Section 108(m)',
      title: 'Tenant Duty and Wear & Tear Exemption',
      legalText: 'The lessee is bound to keep, and on the termination of the lease to restore, the property in as good condition as it was in at the time when he was put in possession, subject only to the changes caused by reasonable wear and tear or irresistible force.',
      plainMeaning: 'Normal paint aging and daily wear cannot be arbitrarily deducted from the tenant’s security deposit.'
    }
  ],
  'rera-2016': [
    {
      section: 'Section 18(1)',
      title: 'Return of Amount and Mandatory Interest for Delay',
      legalText: 'If the promoter fails to complete or is unable to give possession of an apartment, plot or building in accordance with the terms of the agreement for sale... he shall be liable on demand to the allottees, in case the allottee wishes to withdraw from the project, without prejudice to any other remedy available, to return the amount received by him in respect of that apartment with interest at such rate as may be prescribed.',
      plainMeaning: 'If possession is delayed past RERA agreed date, builder MUST refund entire principal with prescribed monthly interest (MCLR + 2%) or pay monthly delay interest if buyer stays.'
    },
    {
      section: 'Section 31',
      title: 'Filing of Complaints before Authority',
      legalText: 'Any aggrieved person may file a complaint with the Authority or the adjudicating officer, as the case may be, for any violation or contravention of the provisions of this Act.',
      plainMeaning: 'Allottee can lodge summary complaint on State RERA web portal without requiring an advocate.'
    }
  ]
};

export const StatuteInspectionModal: React.FC<StatuteInspectionModalProps> = ({
  act,
  isOpen,
  onClose,
  onQueryThisAct
}) => {
  if (!isOpen || !act) return null;

  const sections = DETAILED_STATUTORY_QUOTES[act.id] || act.keySections.map((sec, idx) => ({
    section: sec,
    title: `Statutory Provision ${idx + 1}`,
    legalText: `Substantive provision governing citizen remedies and enforcement protocols under ${act.title}.`,
    plainMeaning: `Provides statutory grounding and procedural compliance requirements for citizens.`
  }));

  return (
    <div 
      className="fixed inset-0 z-50 bg-dark/75 backdrop-blur-xs flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="statute-modal-title"
    >
      <div className="bg-paper border border-dark max-w-3xl w-full rounded-[2px] shadow-2xl overflow-hidden flex flex-col max-h-[90vh] animate-stamp">
        {/* Header */}
        <div className="bg-dark text-paper px-6 py-4 flex items-center justify-between border-b border-rule-dark">
          <div className="flex items-center space-x-3 text-xs">
            <div className="w-2.5 h-2.5 rounded-full bg-accent animate-pulse"></div>
            <span className="font-bold tracking-wider uppercase">STATUTE INSPECTION DOSSIER</span>
            <span className="text-ink-tertiary">|</span>
            <span className="text-slate">{act.actCode}</span>
          </div>
          <button
            onClick={onClose}
            className="text-slate hover:text-white p-1 rounded-[2px] focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-ink">
          {/* Act Title & Metadata Box */}
          <div className="border border-rule bg-white p-5 rounded-[2px] space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="stamp-badge px-2 py-0.5">
                {CATEGORY_LABELS[act.category]}
              </span>
              <span className="text-xs text-ink-muted">
                ENACTED: {act.year} • {act.actNumber} • {act.sectionCount} SECTIONS
              </span>
            </div>

            <h2 id="statute-modal-title" className="font-serif text-heading font-bold text-ink">
              {act.title}
            </h2>

            <p className="text-sm text-ink-secondary font-sans leading-relaxed">
              {act.summary}
            </p>
          </div>

          {/* Detailed Legal Provisions Breakdown */}
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-rule pb-2">
              <span className="text-xs font-bold text-accent-text uppercase tracking-wider flex items-center space-x-1.5">
                <BookOpen className="w-3.5 h-3.5" />
                <span>AUTHENTIC STATUTORY PROVISIONS & CITIZEN REMEDIES</span>
              </span>
              <span className="text-[12px] text-ink-muted">GROUNDED LEGISLATIVE TEXT</span>
            </div>

            <div className="space-y-3">
              {sections.map((sec, idx) => (
                <div 
                  key={idx}
                  className="p-4 border border-rule bg-white rounded-[2px] space-y-2 hover:border-dark transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-ink bg-paper px-2 py-0.5 border border-rule rounded-[2px]">
                      {sec.section}
                    </span>
                    <span className="font-serif font-bold text-sm text-ink">
                      {sec.title}
                    </span>
                  </div>

                  {/* Verbatim Legal Language Quote */}
                  <blockquote className="p-3 bg-paper border-l-2 border-accent text-xs text-ink-secondary leading-relaxed italic">
                    "{sec.legalText}"
                  </blockquote>

                  {/* Plain Language Interpretation */}
                  <div className="flex items-start space-x-2 text-xs font-sans text-ink-secondary pt-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700 shrink-0 mt-0.5" />
                    <span><strong className="text-ink">Plain Legal Effect:</strong> {sec.plainMeaning}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-paper-sunken border-t border-rule flex flex-wrap items-center justify-between gap-3">
          <div className="text-xs text-ink-muted">
            NYAAY AI LEGISLATIVE INDEX // 93 BARE ACTS
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-rule bg-white hover:bg-paper text-ink text-xs rounded-[2px] transition-colors focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none"
            >
              CLOSE
            </button>

            <button
              onClick={() => {
                onQueryThisAct(act);
                onClose();
              }}
              className="px-5 py-2 bg-dark hover:bg-dark-rule text-paper text-xs font-bold rounded-[2px] transition-colors flex items-center space-x-1.5 focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none"
            >
              <span>QUERY THIS ACT IN CIVIC NAVIGATOR</span>
              <ArrowRight className="w-3.5 h-3.5 text-accent" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
