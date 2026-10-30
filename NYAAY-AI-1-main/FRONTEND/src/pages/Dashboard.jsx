import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';

const TOOLS = [
  {
    step: '01',
    workflow: 'CASE INTAKE',
    tag: 'CORE',
    name: 'Civic Navigator',
    desc: 'RTI, Consumer, Tenant — 5-part dossiers from 93 Bare Acts.',
    path: '/civic',
    accent: true,
  },
  {
    step: '02',
    workflow: 'STATUTE RESEARCH',
    tag: 'RESEARCH',
    name: 'Kanoon Q&A',
    desc: 'Statute-grounded answers to Indian law questions.',
    path: '/know-your-kanoon',
    accent: false,
  },
  {
    step: '03',
    workflow: 'DOCUMENT DRAFTING',
    tag: 'DRAFTING',
    name: 'Legal Drafting',
    desc: 'Generate Affidavits, Notices, RTI Applications.',
    path: '/dochub',
    accent: false,
  },
  {
    step: '04',
    workflow: 'CONTRACT ANALYSIS',
    tag: 'ANALYSIS',
    name: 'Document Chat',
    desc: 'Upload a contract — extract clauses, identify red flags.',
    path: '/upload-chat',
    accent: false,
  },
  {
    step: '05',
    workflow: 'LITIGATION STRATEGY',
    tag: 'STRATEGY',
    name: 'Legal Reasoning',
    desc: 'Build arguments, evaluate litigation risk.',
    path: '/reasoning',
    accent: false,
  },
];

const ROLE_LABEL = { citizen: 'CITIZEN', student: 'LAW STUDENT', lawyer: 'LEGAL PROFESSIONAL' };

function DashboardField({ label, value }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="label-stamp text-ink-fog">{label}</span>
      <span className="text-[13px] font-medium text-ink truncate">{value || '—'}</span>
    </div>
  );
}

function formatDate(ds) {
  if (!ds) return null;
  try { return new Date(ds).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' }); }
  catch { return ds; }
}

export default function Dashboard() {
  const { currentUser, userProfile } = useAuth();
  const displayName = userProfile?.name || currentUser?.displayName || 'Counselor';

  return (
    <div className="min-h-screen bg-paper ledger-grid text-ink flex flex-col font-sans">
      <Navbar />
      <main className="max-w-7xl w-full mx-auto px-4 sm:px-6 pt-24 pb-20 flex-grow">

        {/* Welcome header */}
        <div className="border-b border-rule pb-8 pt-4">
          <span className="stamp-badge px-2 py-0.5">
            DASHBOARD // {new Date().getFullYear()}
          </span>
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mt-4">
            <h1
              className="font-serif text-display-lg font-bold text-ink"
            >
              Welcome back,<br />
              <span className="text-accent italic font-normal">{displayName}.</span>
            </h1>
            {userProfile?.role && (
              <span className="self-start md:self-end stamp-badge px-3 py-1 text-accent border-accent">
                {ROLE_LABEL[userProfile.role] || userProfile.role.toUpperCase()}
              </span>
            )}
          </div>
        </div>

        {/* Main grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mt-10">

          {/* Tools Workflow Journey */}
          <div className="lg:col-span-8 space-y-4">
            <div className="flex items-center justify-between border-b border-rule pb-2">
              <span className="text-xs font-bold text-ink-muted uppercase tracking-wider">
                CIVIC LEGAL OPERATING SYSTEM // 5-STEP JOURNEY
              </span>
              <span className="font-mono text-[11px] text-accent-text font-bold">
                INTAKE → STRATEGY
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {TOOLS.map((tool, i) => (
                <motion.div
                  key={tool.name}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: i * 0.05, ease: [0.16, 1, 0.3, 1] }}
                >
                  <Link
                    to={tool.path}
                    className="flex flex-col justify-between p-5 bg-white border border-rule rounded-[4px] group transition-all duration-200 shadow-2xs hover:border-accent hover:shadow-md hover:-translate-y-0.5 h-full"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-accent px-1.5 py-0.5 bg-paper rounded border border-rule">
                          STEP {tool.step}
                        </span>
                        <span className="text-[11px] font-bold px-2 py-0.5 rounded-[2px] border border-accent/25 text-accent-text bg-accent/10">
                          {tool.workflow}
                        </span>
                      </div>
                      <span className="text-ink-muted group-hover:text-accent group-hover:translate-x-1 transition-all">→</span>
                    </div>
                    <div className="mt-4">
                      <h3 className="font-serif text-[16px] font-bold text-ink mb-1 group-hover:text-accent-hover transition-colors">{tool.name}</h3>
                      <p className="text-xs leading-relaxed text-ink-secondary">{tool.desc}</p>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Account sidebar */}
          <div className="lg:col-span-4">
            <span className="text-xs font-bold text-ink-muted uppercase tracking-wider block mb-4">CASE FILE ACCOUNT</span>
            <div className="bg-white/90 border border-rule rounded-[4px] p-6 flex flex-col gap-4 shadow-2xs">
              {/* Avatar */}
              <div className="flex items-center gap-3 pb-4 border-b border-rule">
                <div className="w-10 h-10 bg-dark rounded-[4px] border border-rule-dark flex items-center justify-center flex-shrink-0 text-white font-serif font-bold italic text-lg">
                  {(displayName[0] || 'N').toUpperCase()}
                </div>
                <div>
                  <p className="text-[14px] font-bold text-ink">{displayName}</p>
                  <p className="font-mono text-[12px] text-ink-muted truncate max-w-[160px]">{currentUser?.uid || 'mock-uid'}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-x-4 gap-y-3">
                <DashboardField label="EMAIL" value={userProfile?.email || currentUser?.email} />
                <DashboardField label="ROLE" value={ROLE_LABEL[userProfile?.role] || userProfile?.role} />
                <DashboardField label="JOINED" value={formatDate(userProfile?.created_at)} />
                <DashboardField label="LAST SYNC" value={formatDate(userProfile?.last_login)} />
              </div>

              <div className="pt-3 border-t border-rule">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-600 flex-shrink-0" />
                  <span className="text-[12px] text-ink-muted">NYAAY RAG Engine · Connected</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
