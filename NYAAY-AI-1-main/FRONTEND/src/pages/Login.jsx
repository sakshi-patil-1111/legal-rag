import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AlertTriangle, Eye, EyeOff, ArrowRight } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/common/Navbar';

/*
 * Human-readable names for the destinations a visitor can be bounced from, so
 * the sign-in screen can say what it is protecting instead of showing a bare
 * form and then dumping the user somewhere unrelated.
 */
const DESTINATION_LABELS = {
  '/civic': 'login.destCivic',
  '/know-your-kanoon': 'login.destKanoon',
  '/upload-chat': 'login.destUpload',
  '/dochub': 'login.destDocHub',
  '/reasoning': 'login.destReasoning',
  '/dashboard': 'login.destDashboard',
};

function FieldLabel({ htmlFor, children }) {
  /* htmlFor was missing, so none of these labels were associated with their
     input — clicking a label did nothing and screen readers announced the
     fields unnamed. */
  return (
    <label
      htmlFor={htmlFor}
      className="block text-[12px] font-semibold uppercase tracking-[0.08em] text-ink-tertiary mb-1.5"
    >
      {children}
    </label>
  );
}

function TextField({ id, type = 'text', placeholder, value, onChange, error, autoComplete, trailing }) {
  return (
    <div className="relative">
      <input
        id={id}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        autoComplete={autoComplete}
        aria-invalid={error ? true : undefined}
        className={`w-full px-4 py-3 ${trailing ? 'pr-11' : ''} bg-paper border rounded-[3px] text-[14px] text-ink placeholder-ink-muted
          focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent transition-colors
          ${error ? 'border-error' : 'border-rule-strong hover:border-ink-muted'}`}
      />
      {trailing}
    </div>
  );
}

export default function Login() {
  const { t } = useTranslation();
  const { login, signInWithGoogle } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  /* Where ProtectedRoute bounced us from. Carries its own router state, which
     is where a preset query from the landing page lives. */
  const from = location.state?.from;
  const destinationLabel = from ? DESTINATION_LABELS[from.pathname] : null;

  const goToDestination = () => {
    if (from?.pathname) {
      navigate(from.pathname + (from.search || ''), { state: from.state, replace: true });
    } else {
      navigate('/dashboard', { replace: true });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;
    if (!email || !password) { setError(t('login.fillFields', 'Please enter both email and password.')); return; }
    setLoading(true);
    setError('');
    try {
      await login(email, password);
      goToDestination();
    } catch (err) {
      setError(err.message || t('login.signInFailed', 'Failed to sign in. Please check your credentials.'));
      setLoading(false);
    }
  };

  const handleGoogle = async () => {
    if (loading) return;
    setLoading(true);
    setError('');
    try {
      await signInWithGoogle();
      goToDestination();
    } catch (err) {
      setError(err.message || t('login.googleFailed', 'Google sign-in failed. Please try again.'));
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-paper ledger-grid text-ink font-sans">
      <Navbar />
      <div className="flex items-center justify-center min-h-screen px-4 pt-[140px] lg:pt-28 pb-12">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
          className="w-full max-w-[420px] bg-white/90 backdrop-blur-sm border border-rule p-8 rounded-[4px] shadow-card"
        >
          {/* Case file header */}
          <div className="mb-6">
            <span className="stamp-badge px-2 py-0.5">
              {t('login.badge', 'CASE FILE ACCESS')}
            </span>
            <h1 className="font-serif text-heading font-bold text-ink mt-3">
              {t('login.signInTo', 'Sign in to')}<br />
              <span className="text-accent italic font-normal">{t('login.yourCaseFile', 'your case file.')}</span>
            </h1>
          </div>

          {/* Why the visitor is here, when they were bounced */}
          {destinationLabel && (
            <div className="mb-5 p-3 bg-accent-wash border-l-2 border-accent rounded-[2px] text-[13px] text-accent-deep leading-relaxed">
              {t('login.signInContinue', 'Sign in to continue to')} <span className="font-semibold">{t(destinationLabel, 'your destination')}</span>.
              {t('login.typedKept', ' What you typed has been preserved.')}
            </div>
          )}

          {error && (
            <div
              role="alert"
              className="mb-5 p-3 bg-error-bg border border-error/30 rounded-[2px] text-[13px] text-error flex items-start gap-2 leading-relaxed"
            >
              <AlertTriangle aria-hidden="true" className="w-4 h-4 mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <FieldLabel htmlFor="email">{t('login.emailLabel', 'Email address')}</FieldLabel>
              <TextField
                id="email"
                type="email"
                placeholder={t('login.emailPlaceholder', 'advocate@chamber.in or citizen@domain.in')}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>

            <div>
              <FieldLabel htmlFor="password">{t('login.passwordLabel', 'Password')}</FieldLabel>
              <TextField
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                trailing={
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    aria-label={showPassword ? t('login.hidePassword', 'Hide password') : t('login.showPassword', 'Show password')}
                    className="absolute right-1 top-1/2 -translate-y-1/2 p-2 rounded text-ink-muted hover:text-ink transition-colors focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none"
                  >
                    {showPassword
                      ? <EyeOff aria-hidden="true" className="w-4 h-4" />
                      : <Eye aria-hidden="true" className="w-4 h-4" />}
                  </button>
                }
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              aria-busy={loading}
              className="w-full py-3 mt-1 bg-dark hover:bg-dark-rule disabled:opacity-50 disabled:cursor-not-allowed text-paper font-semibold rounded-[3px] text-[14px] transition-colors shadow-stamp flex items-center justify-center gap-2 focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:outline-none"
            >
              {loading ? t('login.signingIn', 'Signing in…') : t('login.signInButton', 'Sign in')}
              {!loading && <ArrowRight aria-hidden="true" className="w-4 h-4" />}
            </button>
          </form>

          <div className="flex items-center gap-3 my-5">
            <div className="h-px bg-rule flex-grow" />
            <span className="text-[12px] font-semibold uppercase tracking-[0.08em] text-ink-muted">{t('login.or', 'OR')}</span>
            <div className="h-px bg-rule flex-grow" />
          </div>

          <button
            onClick={handleGoogle}
            disabled={loading}
            className="w-full py-3 bg-paper-sunken hover:bg-rule disabled:opacity-50 disabled:cursor-not-allowed border border-rule-strong rounded-[3px] text-[14px] font-medium text-ink transition-colors focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:outline-none"
          >
            {t('login.continueWithGoogle', 'Continue with Google')}
          </button>

          <p className="text-center text-[13px] text-ink-tertiary mt-6">
            {t('login.noAccount', "Don't have an account?")}{' '}
            <Link
              to="/signup"
              state={from ? { from } : undefined}
              className="text-accent-text hover:text-accent-deep hover:underline font-semibold rounded focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none"
            >
              {t('login.createOne', 'Create one')}
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
