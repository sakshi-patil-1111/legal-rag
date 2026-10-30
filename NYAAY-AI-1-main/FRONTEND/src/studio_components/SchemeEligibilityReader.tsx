import React, { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Building, 
  Search, 
  CheckCircle2, 
  XCircle, 
  ExternalLink, 
  FileText, 
  Phone, 
  HelpCircle, 
  Sparkles, 
  ShieldCheck, 
  Coins, 
  UserCheck, 
  Users, 
  ArrowRight,
  Filter,
  Layers,
  Info
} from 'lucide-react';
import { WELFARE_SCHEMES_CATALOG, WelfareScheme } from '../data/welfareSchemesData';

interface SchemeEligibilityReaderProps {
  onGoToNavigator: () => void;
  onGoToFormFiller?: (schemeCode: string) => void;
}

type BeneficiaryPersona = 'ALL' | 'GIG_WORKER' | 'FARMER' | 'WOMEN' | 'SENIOR' | 'LOW_INCOME_URBAN';

export const SchemeEligibilityReader: React.FC<SchemeEligibilityReaderProps> = ({
  onGoToNavigator,
  onGoToFormFiller
}) => {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedPersona, setSelectedPersona] = useState<BeneficiaryPersona>('ALL');
  const [expandedSchemeId, setExpandedSchemeId] = useState<string | null>('ab-pmjay');
  
  // Quick eligibility checker state
  const [checkAge, setCheckAge] = useState<string>('');
  const [checkIncome, setCheckIncome] = useState<string>('');
  const [checkOccupation, setCheckOccupation] = useState<string>('');
  const [checkResult, setCheckResult] = useState<{ eligibleCount: number; matchedSchemes: WelfareScheme[] } | null>(null);

  const filteredSchemes = useMemo(() => {
    return WELFARE_SCHEMES_CATALOG.filter(scheme => {
      const matchesSearch = 
        scheme.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        scheme.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
        scheme.plainLanguageSummary.toLowerCase().includes(searchQuery.toLowerCase()) ||
        scheme.targetBeneficiaries.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCategory = selectedCategory === 'ALL' || scheme.category === selectedCategory;

      let matchesPersona = true;
      if (selectedPersona === 'GIG_WORKER') {
        matchesPersona = scheme.category === 'SKILLS_EDUCATION' || scheme.id.includes('mgnrega') || scheme.id.includes('pm-v');
      } else if (selectedPersona === 'FARMER') {
        matchesPersona = scheme.category === 'AGRICULTURE_FOOD' || scheme.id.includes('kisan') || scheme.id.includes('pmfby');
      } else if (selectedPersona === 'WOMEN') {
        matchesPersona = scheme.category === 'HEALTH_MATERNITY' || scheme.id.includes('mksy') || scheme.id.includes('pmmvy') || scheme.id.includes('pmuy');
      } else if (selectedPersona === 'SENIOR') {
        matchesPersona = scheme.category === 'PENSION_SOCIAL' || scheme.id.includes('ab-pmjay') || scheme.id.includes('nsap') || scheme.id.includes('ignoaps');
      } else if (selectedPersona === 'LOW_INCOME_URBAN') {
        matchesPersona = scheme.id.includes('pmay-u') || scheme.id.includes('nfsa-pds') || scheme.id.includes('pmjdy');
      }

      return matchesSearch && matchesCategory && matchesPersona;
    });
  }, [searchQuery, selectedCategory, selectedPersona]);

  const handleRunQuickAudit = (e: React.FormEvent) => {
    e.preventDefault();
    const incomeNum = parseInt(checkIncome) || 0;
    const ageNum = parseInt(checkAge) || 30;

    const matched = WELFARE_SCHEMES_CATALOG.filter(scheme => {
      if (scheme.id.includes('nsap') && ageNum < 60) return false;
      if (scheme.id.includes('ignoaps') && ageNum < 60) return false;
      if (incomeNum > 800000 && (scheme.category === 'HOUSING_RURAL' || scheme.category === 'PENSION_SOCIAL')) return false;
      return true;
    });

    setCheckResult({
      eligibleCount: matched.length,
      matchedSchemes: matched
    });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      {/* Header Banner */}
      <div className="bg-paper border border-rule rounded-xl p-6 sm:p-8 mb-8 shadow-xs relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-amber-500/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
        
        <div className="max-w-3xl relative z-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-md bg-paper-sunken text-xs text-accent-deep font-bold mb-3">
            <ShieldCheck className="w-3.5 h-3.5 text-accent" />
            <span>{t('schemeReader.badge', 'STATUTORY & WELFARE ENTITLEMENT READER')}</span>
          </div>

          <h1 className="font-serif text-display-md font-bold text-ink mb-3">
            {t('schemeReader.title', 'Government Scheme & Welfare Eligibility Reader')}
          </h1>
          <p className="text-base text-ink-tertiary leading-relaxed mb-6 font-sans">
            {t('schemeReader.description', 'Navigating scattered government gazettes and complex criteria made simple. Enter your situation in plain language to instantly verify your legitimate entitlements, calculation formulas, required documents, and direct application portals.')}
          </p>

          {/* Persona Quick Filters */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs text-ink-tertiary mr-1 flex items-center gap-1">
              <Filter className="w-3 h-3" /> {t('schemeReader.filterByProfile', 'Filter by Profile:')}
            </span>
            {[
              { id: 'ALL', label: t('schemeReader.persona.all', 'All Citizens') },
              { id: 'GIG_WORKER', label: t('schemeReader.persona.gigWorker', '🛵 Gig & Informal Worker') },
              { id: 'FARMER', label: t('schemeReader.persona.farmer', '🌾 Farmer / Landholder') },
              { id: 'WOMEN', label: t('schemeReader.persona.women', '👩 Women & Daughters') },
              { id: 'SENIOR', label: t('schemeReader.persona.senior', '👴 Senior Citizens (60+ / 70+)') },
              { id: 'LOW_INCOME_URBAN', label: t('schemeReader.persona.lowIncomeUrban', '🏙️ Urban EWS / Hawkers') },
            ].map(persona => (
              <button
                key={persona.id}
                onClick={() => {
                  setSelectedPersona(persona.id as BeneficiaryPersona);
                  setCheckResult(null);
                }}
                className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                  selectedPersona === persona.id
                    ? 'bg-dark text-white shadow-xs'
                    : 'bg-white text-ink-tertiary border border-rule hover:border-dark'
                }`}
              >
                {persona.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Quick Eligibility Calculator & Search */}
        <div className="lg:col-span-4 space-y-6">
          {/* Quick Profile Audit Box */}
          <div className="bg-white border border-rule rounded-xl p-5 shadow-xs">
            <div className="flex items-center space-x-2 mb-4 pb-3 border-b border-paper-sunken">
              <Sparkles className="w-4 h-4 text-accent" />
              <h2 className="font-serif font-bold text-base text-ink">
                {t('schemeReader.audit.title', 'Instant Plain-Language Audit')}
              </h2>
            </div>

            <form onSubmit={handleRunQuickAudit} className="space-y-3.5 text-sm">
              <div>
                <label className="block text-xs text-ink-tertiary mb-1">
                  {t('schemeReader.audit.ageLabel', 'Applicant Age (Years)')}
                </label>
                <input
                  type="number"
                  placeholder={t('schemeReader.audit.agePlaceholder', 'e.g. 34 (or 70 for senior health)')}
                  value={checkAge}
                  onChange={(e) => setCheckAge(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-lg border border-rule-strong focus:outline-none focus:ring-1 focus:ring-dark bg-paper"
                />
              </div>

              <div>
                <label className="block text-xs text-ink-tertiary mb-1">
                  {t('schemeReader.audit.incomeLabel', 'Annual Household Income (₹)')}
                </label>
                <input
                  type="number"
                  placeholder={t('schemeReader.audit.incomePlaceholder', 'e.g. 240000 (₹2.4 Lakhs/yr)')}
                  value={checkIncome}
                  onChange={(e) => setCheckIncome(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-lg border border-rule-strong focus:outline-none focus:ring-1 focus:ring-dark bg-paper"
                />
              </div>

              <div>
                <label className="block text-xs text-ink-tertiary mb-1">
                  {t('schemeReader.audit.occupationLabel', 'Primary Occupation / Category')}
                </label>
                <select
                  value={checkOccupation}
                  onChange={(e) => setCheckOccupation(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-lg border border-rule-strong focus:outline-none focus:ring-1 focus:ring-dark bg-paper"
                >
                  <option value="">{t('schemeReader.audit.selectOccupation', 'Select Occupation...')}</option>
                  <option value="gig">{t('schemeReader.audit.occGig', 'Gig / Delivery / Freelance Worker')}</option>
                  <option value="salaried">{t('schemeReader.audit.occSalaried', 'Private Sector Salaried (5+ Yrs)')}</option>
                  <option value="farmer">{t('schemeReader.audit.occFarmer', 'Cultivator / Landowning Farmer')}</option>
                  <option value="vendor">{t('schemeReader.audit.occVendor', 'Street Vendor / Hawkers')}</option>
                  <option value="unorganized">{t('schemeReader.audit.occUnorganized', 'Construction / Domestic Worker')}</option>
                  <option value="senior">{t('schemeReader.audit.occSenior', 'Senior Citizen (Retired / BPL)')}</option>
                </select>
              </div>

              <button
                type="submit"
                className="w-full mt-2 py-2.5 px-4 rounded-lg bg-accent text-white font-medium text-xs uppercase tracking-wider hover:bg-accent-deep transition-colors flex items-center justify-center space-x-2 shadow-xs"
              >
                <span>{t('schemeReader.audit.submit', 'Run Entitlement Audit')}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </form>

            {checkResult && (
              <div className="mt-4 p-3.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-900">
                <div className="font-bold flex items-center space-x-1.5 text-emerald-950 mb-1">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>{t('schemeReader.audit.resultTitle', 'Audit Result:')} {checkResult.eligibleCount} {t('schemeReader.audit.programsMatch', 'Welfare Programs Match')}</span>
                </div>
                <p className="text-emerald-800 leading-snug">
                  {t('schemeReader.audit.resultDesc', 'Based on your parameters, you meet threshold criteria for programs highlighted in the reader.')}
                </p>
              </div>
            )}
          </div>

          {/* Category Filter Pills */}
          <div className="bg-paper border border-rule rounded-xl p-4 text-xs">
            <span className="text-ink-tertiary block mb-2 font-bold uppercase tracking-wider">
              {t('schemeReader.categoriesTitle', 'Statutory Categories')}
            </span>
            <div className="space-y-1.5">
              {[
                { id: 'ALL', label: t('schemeReader.category.all', 'All Statutory Schemes') },
                { id: 'HOUSING_RURAL', label: t('schemeReader.category.housing', '🏠 Housing & Rural Development') },
                { id: 'AGRICULTURE_FOOD', label: t('schemeReader.category.agriculture', '🌾 Agriculture & Food') },
                { id: 'HEALTH_MATERNITY', label: t('schemeReader.category.health', '🏥 Healthcare, Maternity & Welfare') },
                { id: 'PENSION_SOCIAL', label: t('schemeReader.category.pension', '👵 Pensions & Social Security') },
                { id: 'FINANCIAL_INSURANCE', label: t('schemeReader.category.financial', '💰 Financial Inclusion & Insurance') },
                { id: 'SKILLS_EDUCATION', label: t('schemeReader.category.skills', '🎓 Entrepreneurship, Skills & Education') },
              ].map(cat => (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg transition-colors flex items-center justify-between ${
                    selectedCategory === cat.id
                      ? 'bg-white border border-dark text-ink font-bold shadow-xs'
                      : 'text-ink-tertiary hover:bg-paper-sunken'
                  }`}
                >
                  <span>{cat.label}</span>
                  {selectedCategory === cat.id && <span className="w-1.5 h-1.5 rounded-full bg-accent" />}
                </button>
              ))}
            </div>
          </div>

          {/* Quick FAQ info */}
          <div className="p-4 rounded-xl border border-rule bg-white text-xs text-ink-tertiary space-y-2">
            <div className="flex items-center space-x-1.5 text-ink font-bold">
              <Info className="w-3.5 h-3.5 text-accent" />
              <span>{t('schemeReader.dbtNote.title', 'Direct Benefit Transfer (DBT) Note')}</span>
            </div>
            <p className="leading-relaxed">
              {t('schemeReader.dbtNote.desc', 'All statutory monetary entitlements in India require your bank account to be Aadhaar-seeded via NPCI mapper. You can verify seeding at your bank branch or via UIDAI portal.')}
            </p>
          </div>
        </div>

        {/* Right Column: Schemes Catalog & Portal Reader */}
        <div className="lg:col-span-8 space-y-6">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-tertiary" />
            <input
              type="text"
              placeholder={t('schemeReader.searchPlaceholder', "Search scheme name, ministry, keyword (e.g. 'hospital', 'gratuity', '₹6000', 'housing', 'daughter')...")}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-white border border-rule-strong rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-dark shadow-xs"
            />
          </div>

          {/* Scheme Cards */}
          <div className="space-y-4">
            {filteredSchemes.length === 0 ? (
              <div className="p-8 text-center bg-white border border-rule rounded-xl">
                <p className="text-sm text-ink-tertiary">{t('schemeReader.noResults', 'No welfare schemes matched your search criteria.')}</p>
                <button
                  onClick={() => {
                    setSearchQuery('');
                    setSelectedCategory('ALL');
                    setSelectedPersona('ALL');
                  }}
                  className="mt-3 text-xs text-accent-text underline font-bold"
                >
                  {t('schemeReader.resetFilters', 'Reset all filters')}
                </button>
              </div>
            ) : (
              filteredSchemes.map(scheme => {
                const isExpanded = expandedSchemeId === scheme.id;

                return (
                  <div
                    key={scheme.id}
                    className={`bg-white border rounded-xl transition-all ${
                      isExpanded 
                        ? 'border-dark shadow-md ring-1 ring-dark/10' 
                        : 'border-rule hover:border-[#A2B1C6]'
                    }`}
                  >
                    {/* Top Clickable Header */}
                    <div 
                      onClick={() => setExpandedSchemeId(isExpanded ? null : scheme.id)}
                      className="p-5 sm:p-6 cursor-pointer flex flex-col sm:flex-row sm:items-start justify-between gap-4 select-none"
                    >
                      <div className="space-y-2 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="px-2.5 py-0.5 rounded bg-paper text-accent-deep text-xs font-bold border border-rule">
                            {scheme.code}
                          </span>
                          <span className="text-xs text-ink-tertiary">
                            {scheme.ministry}
                          </span>
                        </div>

                        <h3 className="font-serif text-lg sm:text-xl font-bold text-ink">
                          {scheme.name}
                        </h3>

                        <p className="text-xs sm:text-sm text-ink-tertiary leading-relaxed">
                          {scheme.plainLanguageSummary}
                        </p>
                      </div>

                      {/* Right Benefit Badge */}
                      <div className="sm:text-right shrink-0 bg-paper sm:bg-transparent p-3 sm:p-0 rounded-lg sm:rounded-none border sm:border-0 border-rule">
                        <span className="text-[12px] uppercase text-ink-tertiary block">
                          {t('schemeReader.statutoryBenefit', 'Statutory Benefit')}
                        </span>
                        <span className="font-serif font-bold text-sm sm:text-base text-accent-text">
                          {scheme.benefitBadge}
                        </span>
                      </div>
                    </div>

                    {/* Expanded Detail Panel */}
                    {isExpanded && (
                      <div className="px-5 sm:px-6 pb-6 pt-2 border-t border-paper-sunken space-y-6 text-sm">
                        {/* Target & Benefit Breakdown */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-paper p-4 rounded-xl border border-rule">
                          <div>
                            <span className="text-xs font-bold text-ink-tertiary uppercase block mb-1">
                              {t('schemeReader.targetBeneficiaries', 'Target Beneficiaries')}
                            </span>
                            <p className="text-xs text-ink leading-relaxed">
                              {scheme.targetBeneficiaries}
                            </p>
                          </div>
                          <div>
                            <span className="text-xs font-bold text-ink-tertiary uppercase block mb-1">
                              {t('schemeReader.maxEntitlementCap', 'Max Entitlement Cap')}
                            </span>
                            <p className="text-xs text-ink font-medium leading-relaxed">
                              {scheme.maxBenefit}
                            </p>
                          </div>
                        </div>

                        {/* Who Qualifies vs Who is Excluded */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <div className="p-4 rounded-xl bg-emerald-50/70 border border-emerald-200">
                            <h4 className="text-xs font-bold text-emerald-950 uppercase mb-2 flex items-center gap-1.5">
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                              {t('schemeReader.mandatoryEligibilityRules', 'Mandatory Eligibility Rules')}
                            </h4>
                            <ul className="space-y-1.5 text-xs text-emerald-900 list-disc list-inside">
                              {scheme.eligibilityCriteria.map((crit, idx) => (
                                <li key={idx} className="leading-snug">{crit}</li>
                              ))}
                            </ul>
                          </div>

                          <div className="p-4 rounded-xl bg-rose-50/70 border border-rose-200">
                            <h4 className="text-xs font-bold text-rose-950 uppercase mb-2 flex items-center gap-1.5">
                              <XCircle className="w-3.5 h-3.5 text-rose-600" />
                              {t('schemeReader.statutoryIneligibility', 'Statutory Ineligibility / Exclusions')}
                            </h4>
                            <ul className="space-y-1.5 text-xs text-rose-900 list-disc list-inside">
                              {scheme.ineligibilityExclusions.map((excl, idx) => (
                                <li key={idx} className="leading-snug">{excl}</li>
                              ))}
                            </ul>
                          </div>
                        </div>

                        {/* Required Documents Checklist */}
                        <div>
                          <h4 className="text-xs font-bold text-ink uppercase mb-2 flex items-center gap-1.5">
                            <FileText className="w-3.5 h-3.5 text-accent" />
                            {t('schemeReader.mandatoryDocumentation', 'Mandatory Documentation Packet')}
                          </h4>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {scheme.requiredDocuments.map((doc, idx) => (
                              <div 
                                key={idx}
                                className="flex items-center space-x-2 p-2.5 rounded-lg border border-rule bg-white text-xs text-ink-secondary"
                              >
                                <span className="w-1.5 h-1.5 rounded-full bg-accent shrink-0" />
                                <span>{doc}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Step-by-Step Application Roadmap */}
                        <div>
                          <h4 className="text-xs font-bold text-ink uppercase mb-2">
                            {t('schemeReader.applicationProcedure', 'Application Procedure & Portal Path')}
                          </h4>
                          <div className="space-y-2">
                            {scheme.applicationProcess.map((step, idx) => (
                              <div key={idx} className="flex items-start space-x-3 text-xs">
                                <span className="w-6 h-6 rounded-full bg-dark text-white flex items-center justify-center font-bold text-[12px] shrink-0 mt-0.5">
                                  {idx + 1}
                                </span>
                                <p className="text-ink-tertiary leading-relaxed pt-0.5">
                                  {step}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Action Footer Bar */}
                        <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-paper-sunken">
                          <div className="flex items-center space-x-2 text-xs text-ink-tertiary">
                            <Phone className="w-3.5 h-3.5 text-accent" />
                            <span>{t('schemeReader.officialHelpline', 'Official Helpline:')} <strong>{scheme.helplineNumber}</strong></span>
                          </div>

                          <div className="flex items-center space-x-3">
                            <a
                              href={scheme.officialPortalUrl}
                              target="_blank"
                              rel="noreferrer"
                              className="px-3.5 py-2 rounded-lg bg-white border border-rule-strong text-xs text-ink hover:bg-paper font-semibold transition-colors inline-flex items-center space-x-1.5"
                            >
                              <span>{t('schemeReader.officialPortal', 'Official Portal')}</span>
                              <ExternalLink className="w-3 h-3" />
                            </a>

                            {onGoToFormFiller && (
                              <button
                                onClick={() => onGoToFormFiller(scheme.code)}
                                className="px-4 py-2 rounded-lg bg-dark text-white text-xs font-medium hover:bg-dark-rule transition-colors inline-flex items-center space-x-1.5 shadow-xs"
                              >
                                <span>{t('schemeReader.fillFormLive', 'Fill Form Live')}</span>
                                <ArrowRight className="w-3 h-3" />
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
};