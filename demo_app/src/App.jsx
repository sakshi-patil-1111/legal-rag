import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { LanguageProvider } from './contexts/LanguageContext';
import LoadingSpinner from './components/common/LoadingSpinner';

const LegalReasoning = lazy(() => import('./pages/LegalReasoning'));

const PageLoader = () => (
  <div className="flex items-center justify-center h-screen bg-n-white dark:bg-n-slate">
    <LoadingSpinner
      size="lg"
      color="dark"
      message="Loading"
      fullScreen={false}
      variant="branded"
      brandText="Ny"
      tagline="loading"
    />
  </div>
);

function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-n-white dark:bg-n-slate">
            <Suspense fallback={<PageLoader />}>
              <Routes>
                <Route path="/" element={<Navigate to="/legal-reasoning" replace />} />
                <Route path="/legal-reasoning" element={<LegalReasoning />} />
                <Route path="*" element={<Navigate to="/legal-reasoning" replace />} />
              </Routes>
            </Suspense>
          </div>
        </Router>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
