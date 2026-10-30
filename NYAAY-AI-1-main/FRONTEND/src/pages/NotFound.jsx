import React from 'react';
import { Link } from 'react-router-dom';
import { Search, BookOpen, FileText, ArrowLeft } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';

/*
 * 404. Previously an unknown URL matched no route and React Router rendered
 * nothing — a blank #FAF7F2 page with a navbar-less body.
 */

export default function NotFound() {
  const { t } = useTranslation();

  const SUGGESTIONS = [
    { to: '/civic', icon: Search, label: t('notFound.civicNavigator'), desc: t('notFound.civicDesc') },
    { to: '/know-your-kanoon', icon: BookOpen, label: t('notFound.kanoon'), desc: t('notFound.kanoonDesc') },
    { to: '/dochub', icon: FileText, label: t('notFound.docDrafting'), desc: t('notFound.docDesc') },
  ];

  return (
    <div className="min-h-screen bg-paper text-ink flex flex-col font-sans">
      <Navbar />

      <main className="flex-grow pt-[124px] lg:pt-[88px] pb-20">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 py-12 sm:py-20">

          <p className="text-xs font-bold uppercase tracking-[0.1em] text-accent-text">
            {t('notFound.error')}
          </p>

          <h1 className="mt-4 font-serif text-display-md font-bold text-ink">
            {t('notFound.title')}
          </h1>

          <p className="mt-4 text-[15px] text-ink-secondary leading-relaxed">
            {t('notFound.description')}
          </p>

          <Link
            to="/"
            className="mt-8 inline-flex items-center gap-1.5 text-[13px] font-medium text-accent-text hover:text-accent-deep transition-colors rounded focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none"
          >
            <ArrowLeft aria-hidden="true" className="w-3.5 h-3.5" />
            {t('notFound.backHome')}
          </Link>

          <nav className="mt-12 pt-8 border-t border-rule" aria-labelledby="nf-suggestions">
            <h2
              id="nf-suggestions"
              className="text-[12px] font-semibold uppercase tracking-[0.08em] text-ink-tertiary"
            >
              {t('notFound.startHere')}
            </h2>

            <ul className="mt-4 space-y-2">
              {SUGGESTIONS.map(({ to, icon: Icon, label, desc }) => (
                <li key={to}>
                  <Link
                    to={to}
                    className="group flex items-start gap-3 p-4 bg-[#FFFFFF] border border-rule rounded-[3px] hover:border-accent transition-colors focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none"
                  >
                    <Icon aria-hidden="true" className="w-4 h-4 mt-0.5 shrink-0 text-accent" />
                    <span>
                      <span className="block text-[14px] font-semibold text-ink">
                        {label}
                      </span>
                      <span className="block mt-0.5 text-[13px] text-ink-tertiary">
                        {desc}
                      </span>
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

        </div>
      </main>

      <Footer />
    </div>
  );
}
