import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  BookOpen, 
  Search, 
  Layers, 
  ExternalLink, 
  FileText, 
  Filter, 
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { BARE_ACTS_CATALOG, CATEGORY_LABELS } from '../data/bareActsData';
import { BareAct } from '../types';

interface BareActsBrowserProps {
  onSelectActForQuery: (act: BareAct) => void;
}

export const BareActsBrowser: React.FC<BareActsBrowserProps> = ({
  onSelectActForQuery
}) => {
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedActModal, setSelectedActModal] = useState<BareAct | null>(null);

  const filteredActs = BARE_ACTS_CATALOG.filter(act => {
    const matchesSearch = act.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          act.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          act.keySections.some(s => s.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory = selectedCategory === 'ALL' || act.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      {/* Header */}
      <div className="border-b border-rule pb-6 space-y-2">
        <div className="flex items-center space-x-2">
          <span className="stamp-badge px-2 py-0.5">
            {t('bareActs.statutoryRepository', 'STATUTORY REPOSITORY // 93 BARE ACTS')}
          </span>
          <span className="text-xs text-ink-muted">
            {t('bareActs.indianLegislativeDatabase', 'INDIAN LEGISLATIVE DATABASE')}
          </span>
        </div>
        <h1 className="font-serif text-display-md font-bold text-ink">
          {t('bareActs.groundingIndexTitle', 'Indian Bare Acts Grounding Index')}
        </h1>
        <p className="text-sm text-ink-tertiary max-w-2xl font-sans">
          {t('bareActs.groundingIndexDesc', "Search the grounded statutory repository powering NYAAY AI's hybrid dense and sparse RRF retrieval engine.")}
        </p>
      </div>

      {/* Search & Category Filter */}
      <div className="flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-ink-muted absolute left-3.5 top-3.5" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={t('bareActs.searchPlaceholder', "Search across 93 Bare Acts by title, section, or subject (e.g. 'RTI', 'Eviction', 'Warranty', 'Sec 106')...")}
            className="w-full pl-10 pr-4 py-2.5 bg-white border border-rule focus:border-dark rounded-[2px] text-xs font-sans outline-none"
          />
        </div>

        <div className="w-full sm:w-64">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full py-2.5 px-3 bg-white border border-rule text-xs rounded-[2px] outline-none"
          >
            <option value="ALL">{t('bareActs.allCategories', 'ALL CATEGORIES')} ({BARE_ACTS_CATALOG.length})</option>
            <option value="CIVIC_RIGHTS">{t('bareActs.catCivicRights', 'Civic & Information Rights')}</option>
            <option value="CONSUMER_COMMERCIAL">{t('bareActs.catConsumerCommercial', 'Consumer & Commercial')}</option>
            <option value="PROPERTY_HOUSING">{t('bareActs.catPropertyHousing', 'Property & Tenancy')}</option>
            <option value="CONSTITUTIONAL">{t('bareActs.catConstitutional', 'Constitutional Charter')}</option>
            <option value="PENAL_PROCEDURAL">{t('bareActs.catPenalProcedural', 'Procedural & Penal')}</option>
            <option value="ENVIRONMENTAL_LABOR">{t('bareActs.catEnvironmentalLabor', 'Environmental & Labor')}</option>
          </select>
        </div>
      </div>

      {/* Grid of Bare Acts */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredActs.map((act) => (
          <div
            key={act.id}
            className="border border-rule bg-white hover:border-dark hover:shadow-xs transition-all rounded-[2px] p-5 flex flex-col justify-between space-y-4"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[12px] font-bold text-accent-text uppercase">
                  {act.actCode}
                </span>
                <span className="text-[12px] text-ink-muted">
                  {act.year}
                </span>
              </div>

              <h3 className="font-serif font-bold text-lg text-ink">
                {act.title}
              </h3>

              <div className="text-[12px] text-ink-tertiary">
                {t('bareActs.categoryPrefix', 'Category:')} {CATEGORY_LABELS[act.category]}
              </div>

              <p className="text-xs text-ink-tertiary font-sans line-clamp-3 leading-relaxed">
                {act.summary}
              </p>
            </div>

            {/* Key Sections Tags */}
            <div className="space-y-3 pt-3 border-t border-paper-sunken">
              <div className="flex flex-wrap gap-1">
                {act.keySections.slice(0, 3).map((sec, idx) => (
                  <span key={idx} className="text-[12px] bg-paper text-ink border border-rule px-1.5 py-0.5 rounded-[2px]">
                    {sec}
                  </span>
                ))}
              </div>

              <div className="flex items-center justify-between pt-1">
                <span className="text-[12px] text-ink-muted">
                  {act.sectionCount} {t('bareActs.sections', 'SECTIONS')}
                </span>
                <button
                  onClick={() => onSelectActForQuery(act)}
                  className="px-3 py-1 bg-dark hover:bg-dark-rule text-paper text-[12px] rounded-[2px] transition-colors flex items-center space-x-1"
                >
                  <span>{t('bareActs.queryThisAct', 'QUERY THIS ACT')}</span>
                  <ArrowRight className="w-3 h-3 text-accent" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};