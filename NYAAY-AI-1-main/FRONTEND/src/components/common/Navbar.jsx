import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Sparkles,
  Search,
  BookOpen,
  FileUp,
  FileText,
  Scale,
  LayoutDashboard,
  FolderArchive,
  LogOut,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import LanguageSelector from './LanguageSelector';

/**
 * AppNav — unified navigation bar for all routes.
 *
 * Translucent glassmorphic navy header. Scroll > 80px increases opacity for
 * floating presence.
 *
 * Type: labels are Inter, not mono. Mono is reserved for data (the account
 * identifier) — it is not the UI typeface.
 *
 * Props:
 *   fullWidth    — stretch to full viewport width (default: max-w-7xl centred)
 *   tabs         — array of { id, label } objects
 *   activeTab    — currently active tab id
 *   onTabChange  — (id: string) => void
 */
export default function Navbar({ fullWidth = false, tabs, activeTab, onTabChange }) {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);
  const [signingOut, setSigningOut] = useState(false);
  const rafRef = useRef(null);

  /* ── Scroll-driven opacity boost ── */
  useEffect(() => {
    const onScroll = () => {
      if (rafRef.current) return;
      rafRef.current = requestAnimationFrame(() => {
        setScrolled(window.scrollY > 80);
        rafRef.current = null;
      });
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', onScroll);
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, []);

  const handleLogout = async () => {
    if (signingOut) return;
    setSigningOut(true);
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
      setSigningOut(false);
    }
  };

  const { t } = useTranslation();

  /* ── Nav order: Dashboard → Civic Navigator → Kanoon Q&A → Doc Chat → Drafting → Reasoning ── */
  const NAV_ITEMS = [
    { path: '/dashboard',        label: t('nav.dashboard', 'Dashboard'),            icon: LayoutDashboard },
    { path: '/civic',            label: t('nav.civicNavigator', 'Civic Navigator'), icon: Search },
    { path: '/know-your-kanoon', label: t('nav.kanoonQA', 'Kanoon Q&A'),           icon: BookOpen },
    { path: '/upload-chat',      label: t('nav.docChat', 'Doc Chat'),               icon: FileUp },
    { path: '/dochub',           label: t('nav.drafting', 'Drafting'),             icon: FileText },
    { path: '/reasoning',        label: t('nav.reasoning', 'Reasoning'),            icon: Scale },
  ];

  const innerClass = fullWidth ? 'w-full px-4 md:px-6' : 'w-full px-4 sm:px-6 lg:px-8';

  /* Glassmorphic navy background (#121820 = rgb(18, 24, 32)) */
  const barBg = scrolled
    ? 'rgba(18, 24, 32, 0.92)'
    : 'rgba(18, 24, 32, 0.78)';

  return (
    <header
      className="fixed top-0 w-full z-50 transform-gpu will-change-transform transition-all duration-300"
      style={{
        background: barBg,
        backdropFilter: 'blur(16px) saturate(160%)',
        WebkitBackdropFilter: 'blur(16px) saturate(160%)',
        borderBottom: '1px solid rgba(43, 53, 66, 0.6)',
      }}
    >
      {/* ── Main row: 3-part flex layout [logo (flex-none) | nav-links (flex-1) | utility-cluster (flex-none)] ── */}
      <div className={`${innerClass} flex items-center justify-between h-16 gap-3 sm:gap-4 lg:gap-6`}>

        {/* 1. Brand / Logo (flex: 0 0 auto) */}
        <Link to="/" className="flex items-center space-x-2.5 group select-none shrink-0 flex-none" aria-label="NYAAY AI — home">
          {/* Logo icon box */}
          <div className="w-8 h-8 rounded-lg bg-dark-raised text-paper flex items-center justify-center border border-rule-dark group-hover:border-accent transition-colors">
            <span className="font-serif font-bold text-sm tracking-tight text-paper">Ny</span>
          </div>

          {/* Wordmark */}
          <div className="flex items-baseline space-x-2">
            <span className="font-serif font-bold text-xl tracking-tight text-paper">
              NYAAY
            </span>
            <span className="text-[12px] uppercase tracking-widest px-1.5 py-0.5 rounded bg-accent text-paper font-bold border border-accent">
              AI
            </span>
            <span className="hidden 2xl:inline text-[#2B3542]" aria-hidden="true">|</span>
            <span className="hidden 2xl:inline text-[12px] font-sans font-medium uppercase tracking-wider text-slate">
              Civic Legal OS
            </span>
          </div>
        </Link>

        {/* 2. Middle: Desktop nav — flexible middle section (flex: 1 1 auto, centered) sizing naturally to content */}
        <div className="hidden lg:flex items-center flex-1 justify-center min-w-0">
          <nav
            className="flex items-center p-1 rounded-lg bg-dark-raised/80 border border-rule-dark shadow-inner space-x-0.5 xl:space-x-1"
            aria-label="Main navigation"
          >
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  aria-current={isActive ? 'page' : undefined}
                  className={`relative flex items-center space-x-1.5 px-2.5 xl:px-3 py-1.5 rounded-md text-[12.5px] xl:text-[13px] font-sans font-medium transition-colors duration-150 focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none whitespace-nowrap ${
                    isActive
                      ? 'text-paper font-semibold'
                      : 'text-slate hover:text-paper hover:bg-dark-rule/60'
                  }`}
                >
                  {isActive && (
                    <motion.div
                      layoutId="nav-active-indicator"
                      className="absolute inset-0 bg-accent rounded-md shadow-xs"
                      transition={{ type: 'spring', damping: 25, stiffness: 350 }}
                    />
                  )}
                  <Icon
                    aria-hidden="true"
                    className={`w-3.5 h-3.5 shrink-0 relative z-10 ${
                      isActive ? 'text-paper' : 'text-slate-muted'
                    }`}
                  />
                  <span className="relative z-10">{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* 3. Right: Utility Cluster (flex: 0 0 auto) */}
        <div className="flex items-center space-x-1.5 sm:space-x-2 shrink-0 flex-none">
          {/* Dockets */}
          <Link
            to="/civic"
            className="h-8 flex items-center space-x-1.5 px-2.5 py-1.5 bg-dark-raised/80 hover:bg-accent/10 text-slate hover:text-paper border border-rule-dark hover:border-accent text-[13px] font-sans font-medium rounded-lg transition-all shadow-xs focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none"
            aria-label="View saved case dockets"
          >
            <FolderArchive aria-hidden="true" className="w-3.5 h-3.5 text-slate-muted" />
            <span className="hidden sm:inline">{t('nav.dockets', 'Dockets')}</span>
          </Link>

          {/* Restyled Compact Language Selector */}
          <LanguageSelector />

          {/* User Authentication & Action Pill */}
          {currentUser ? (
            <div className="flex items-center space-x-1.5 sm:space-x-2">
              {/* Account identifier — mono data badge */}
              <span className="hidden md:flex items-center h-8 text-xs font-mono text-slate bg-dark-raised/80 border border-rule-dark px-2.5 py-1.5 rounded-lg truncate max-w-[130px]">
                {currentUser.displayName || currentUser.email?.split('@')[0]}
              </span>

              <button
                onClick={handleLogout}
                disabled={signingOut}
                aria-busy={signingOut}
                className="h-8 flex items-center space-x-1 px-2.5 py-1.5 bg-accent hover:bg-accent-hover disabled:opacity-60 disabled:cursor-not-allowed text-paper text-[13px] font-sans font-medium rounded-lg transition-colors shadow-xs focus-visible:ring-2 focus-visible:ring-[#FAF7F2] focus-visible:outline-none cursor-pointer"
                aria-label="Sign out"
              >
                <LogOut aria-hidden="true" className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">{signingOut ? t('nav.signingOut', 'Signing out…') : t('nav.signOut', 'Sign out')}</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center space-x-1.5 sm:space-x-2">
              <Link
                to="/login"
                className="h-8 flex items-center px-2.5 sm:px-3 py-1.5 text-[13px] font-sans font-medium text-slate hover:text-paper hover:bg-dark-raised/60 transition-colors rounded-lg focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none"
              >
                {t('nav.signIn', 'Sign in')}
              </Link>
              <Link
                to="/signup"
                className="h-8 flex items-center px-2.5 sm:px-3 py-1.5 bg-accent hover:bg-accent-hover text-paper text-[13px] font-sans font-medium rounded-lg transition-colors shadow-xs focus-visible:ring-2 focus-visible:ring-[#FAF7F2] focus-visible:outline-none"
              >
                {t('nav.getStarted', 'Get started')}
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* ── Optional tab strip (e.g. CivicNavigator) ── */}
      {tabs && tabs.length > 0 && (
        <div className="border-t border-rule-dark bg-dark/90 backdrop-blur-md">
          <div
            className={`${innerClass} flex items-center gap-1 h-10 overflow-x-auto scrollbar-none`}
            role="tablist"
            aria-label="Section tabs"
          >
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  role="tab"
                  aria-selected={isActive}
                  onClick={() => onTabChange?.(tab.id)}
                  className={`whitespace-nowrap px-3 py-1.5 rounded-[4px] text-[12px] font-sans font-semibold uppercase tracking-wider transition-all duration-150 focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none ${
                    isActive
                      ? 'bg-accent text-paper'
                      : 'text-slate hover:text-paper hover:bg-dark-raised'
                  }`}
                >
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Mobile nav strip ── */}
      <nav
        className="lg:hidden flex items-center space-x-1.5 px-4 py-2 bg-dark/95 backdrop-blur-md border-t border-rule-dark overflow-x-auto scrollbar-none"
        aria-label="Main navigation"
      >
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              aria-current={isActive ? 'page' : undefined}
              className={`flex items-center space-x-1 px-2.5 py-1.5 rounded-[4px] shrink-0 text-[12px] font-sans font-medium transition-all duration-150 focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none ${
                isActive
                  ? 'bg-accent text-paper font-semibold shadow-xs'
                  : 'bg-dark-raised text-slate hover:text-paper border border-rule-dark'
              }`}
            >
              <Icon aria-hidden="true" className={`w-3 h-3 ${isActive ? 'text-paper' : 'text-slate-muted'}`} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </header>
  );
}
