import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { LanguageProvider } from './contexts/LanguageContext';
import ProtectedRoute from './components/common/ProtectedRoute';

// Lazy-load all pages to optimize initial bundle size
const Landing = lazy(() => import('./pages/Landing'));

// Lazy-load all other pages to reduce initial bundle size
const Login = lazy(() => import('./pages/Login'));
const Signup = lazy(() => import('./pages/Signup'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const KnowYourKanoon = lazy(() => import('./pages/KnowYourKanoon'));
const UploadChat = lazy(() => import('./pages/UploadChat'));
const DocHub = lazy(() => import('./pages/DocHub'));
const LegalReasoning = lazy(() => import('./pages/LegalReasoning'));
const CivicNavigator = lazy(() => import('./pages/CivicNavigator'));
const Legal = lazy(() => import('./pages/Legal'));
const NotFound = lazy(() => import('./pages/NotFound'));

/*
 * Route-transition fallback.
 *
 * Was `background: #FFFFFF` with a bare "Loading…" — a white flash against a
 * #FAF7F2 app, then unstyled system text. Paper-toned and branded instead.
 */
function RouteFallback() {
  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center gap-4 bg-paper"
      role="status"
      aria-live="polite"
    >
      <div className="w-8 h-8 rounded-[4px] bg-dark text-paper flex items-center justify-center border border-rule-dark">
        <span className="font-serif font-bold text-sm tracking-tight">Ny</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
        <span className="text-[13px] font-sans text-ink-tertiary">Loading…</span>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <LanguageProvider>
        <AuthProvider>
        <Suspense fallback={<RouteFallback />}>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />

            {/* Public legal pages — Terms / Privacy / Disclaimer.
                These must never sit behind auth: a visitor has to be able to
                read the disclaimer before handing over a legal problem. */}
            <Route path="/legal" element={<Navigate to="/legal/disclaimer" replace />} />
            <Route path="/legal/:doc" element={<Legal />} />

            {/* Protected Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/know-your-kanoon"
              element={
                <ProtectedRoute>
                  <KnowYourKanoon />
                </ProtectedRoute>
              }
            />
            <Route
              path="/upload-chat"
              element={
                <ProtectedRoute>
                  <UploadChat />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dochub"
              element={
                <ProtectedRoute>
                  <DocHub />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reasoning"
              element={
                <ProtectedRoute>
                  <LegalReasoning />
                </ProtectedRoute>
              }
            />
            <Route
              path="/civic"
              element={
                <ProtectedRoute>
                  <CivicNavigator />
                </ProtectedRoute>
              }
            />

            {/* Unknown URLs rendered a blank page. */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
        </AuthProvider>
      </LanguageProvider>
    </Router>
  );
}

export default App;
