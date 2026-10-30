import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AlertTriangle, Eye, EyeOff, ArrowRight, Check } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/common/Navbar';

function FieldLabel({ htmlFor, children }) {
  /* htmlFor was missing on every label on this form. */
  return (
    <label
      htmlFor={htmlFor}
      className="block text-[12px] font-semibold uppercase tracking-[0.08em] text-ink-tertiary mb-1.5"
    >
      {children}
    </label>
  );
}

function TextField({ id, type = 'text', placeholder, value, onChange, onBlur, error, autoComplete, trailing }) {
  return (
    <div>
      <div className="relative">
        <input
          id={id}
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          onBlur={onBlur}
          autoComplete={autoComplete}
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? `${id}-error` : undefined}
          className={`w-full px-4 py-3 ${trailing ? 'pr-11' : ''} bg-paper border rounded-[3px] text-[14px] text-ink placeholder-ink-muted
            focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent transition-colors
            ${error ? 'border-error' : 'border-rule-strong hover:border-ink-muted'}`}
        />
        {trailing}
      </div>
      {error && (
        <p id={`${id}-error`} className="mt-1.5 text-[12px] text-error">
          {error}
        </p>
      )}
    </div>
  );
}

export default function Signup() {
  const { t } = useTranslation();
  const { signup, signInWithGoogle } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formError, setFormError] = useState('');
  /* Per-field errors shown next to the field that caused them, rather than one
     banner that says only the first thing that went wrong. */
  const [fieldErrors, setFieldErrors] = useState({});
  const [touched, setTouched] = useState({});

  const from = location.state?.from;

  const validateField = (field, values) => {
    const v = { name, email, password, confirmPassword, ...values };
    switch (field) {
      case 'name':
        return v.name.trim() ? '' : t('signup.nameRequired', 'Full name is required');
      case 'email':
        if (!v.email) return t('signup.emailRequired', 'Email address is required');
        return /\S+@\S+\.\S+/.test(v.email) ? '' : t('signup.emailInvalid', 'Enter a valid email address');
      case 'password':
        return v.password.length >= 6 ? '' : t('signup.passwordMin', 'Password must be at least 6 characters');
      case 'confirmPassword':
        if (!v.confirmPassword) return t('signup.repeatPassword', 'Please repeat your password');
        return v.password === v.confirmPassword ? '' : t('signup.passwordsNotMatch', 'Passwords do not match');
      default:
        return '';
    }
  };

  const handleBlur = (field) => {
    setTouched((tState) => ({ ...tState, [field]: true }));
    setFieldErrors((e) => ({ ...e, [field]: validateField(field) }));
  };

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
    setFormError('');

    const next = {};
    ['name', 'email', 'password', 'confirmPassword'].forEach((f) => {
      const msg = validateField(f);
      if (msg) next[f] = msg;
    });
    setFieldErrors(next);
    setTouched({ name: true, email: true, password: true, confirmPassword: true });
    if (Object.keys(next).length > 0) return;

    setLoading(true);
    try {
      await signup(email, password, name);
      goToDestination();
    } catch (err) {
      setFormError(err.message || t('signup.createFailed', 'Failed to create account. Please try again.'));
      setLoading(false);
    }
  };

  const handleGoogle = async () => {
    if (loading) return;
    setFormError('');
    setLoading(true);
    try {
      await signInWithGoogle();
      goToDestination();
    } catch (err) {
      setFormError(err.message || t('signup.googleFailed', 'Google sign-up failed. Please try again.'));
      setLoading(false);
    }
  };

  const passwordStrongEnough = password.length >= 6;

  return (
    <div className="min-h-screen bg-paper ledger-grid text-ink font-sans">
      <Navbar />
      <div className="flex items-center justify-center min-h-screen px-4 pt-[140px] lg:pt-28 pb-12">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
          className="w-full max-w-[440px] bg-white/90 backdrop-blur-sm border border-rule p-8 rounded-[4px] shadow-card"
        >
          <div className="mb-6">
            <span className="stamp-badge px-2 py-0.5">
              {t('signup.badge', 'CREATE CASE FILE')}
            </span>
            <h1 className="font-serif text-heading font-bold text-ink mt-3">
              {t('signup.openYour', 'Open your')}<br />
              <span className="text-accent italic font-normal">{t('signup.caseFile', 'citizen case file.')}</span>
            </h1>
            <p className="text-[13px] text-ink-tertiary mt-2">
              {t('signup.freeHackathon', 'Free for citizens, researchers, and legal aid clinics.')}
            </p>
          </div>

          {from && (
            <div className="mb-5 p-3 bg-accent-wash border-l-2 border-accent rounded-[2px] text-[13px] text-accent-deep leading-relaxed">
              {t('signup.createContinue', 'Create an account to continue saving your queries.')}
            </div>
          )}

          {formError && (
            <div
              role="alert"
              className="mb-5 p-3 bg-error-bg border border-error/30 rounded-[2px] text-[13px] text-error flex items-start gap-2 leading-relaxed"
            >
              <AlertTriangle aria-hidden="true" className="w-4 h-4 mt-0.5 shrink-0" />
              <span>{formError}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-4">
            <div>
              <FieldLabel htmlFor="name">{t('signup.fullNameLabel', 'Full name')}</FieldLabel>
              <TextField
                id="name"
                placeholder={t('signup.fullNamePlaceholder', 'Justice Citizen')}
                value={name}
                onChange={(e) => setName(e.target.value)}
                onBlur={() => handleBlur('name')}
                error={touched.name ? fieldErrors.name : ''}
                autoComplete="name"
              />
            </div>

            <div>
              <FieldLabel htmlFor="email">{t('signup.emailLabel', 'Email address')}</FieldLabel>
              <TextField
                id="email"
                type="email"
                placeholder={t('signup.emailPlaceholder', 'citizen@domain.in')}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onBlur={() => handleBlur('email')}
                error={touched.email ? fieldErrors.email : ''}
                autoComplete="email"
              />
            </div>

            <div>
              <FieldLabel htmlFor="password">{t('signup.passwordLabel', 'Password')}</FieldLabel>
              <TextField
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder={t('signup.passwordPlaceholder', 'At least 6 characters')}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onBlur={() => handleBlur('password')}
                error={touched.password ? fieldErrors.password : ''}
                autoComplete="new-password"
                trailing={
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    aria-label={showPassword ? t('signup.hidePassword', 'Hide password') : t('signup.showPassword', 'Show password')}
                    className="absolute right-1 top-1/2 -translate-y-1/2 p-2 rounded text-ink-muted hover:text-ink transition-colors focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none"
                  >
                    {showPassword
                      ? <EyeOff aria-hidden="true" className="w-4 h-4" />
                      : <Eye aria-hidden="true" className="w-4 h-4" />}
                  </button>
                }
              />
              {/* Live requirement feedback, so the rule is visible before submit */}
              {password.length > 0 && !fieldErrors.password && (
                <p className={`mt-1.5 text-[12px] flex items-center gap-1 ${passwordStrongEnough ? 'text-success' : 'text-ink-tertiary'}`}>
                  {passwordStrongEnough && <Check aria-hidden="true" className="w-3 h-3" />}
                  {passwordStrongEnough ? t('signup.longEnough', '6+ characters (good)') : t('signup.moreCharsNeeded', { count: 6 - password.length, defaultValue: `${6 - password.length} more characters needed` })}
                </p>
              )}
            </div>

            <div>
              <FieldLabel htmlFor="confirmPassword">{t('signup.confirmPasswordLabel', 'Confirm password')}</FieldLabel>
              <TextField
                id="confirmPassword"
                type={showPassword ? 'text' : 'password'}
                placeholder={t('signup.confirmPasswordPlaceholder', 'Repeat password')}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                onBlur={() => handleBlur('confirmPassword')}
                error={touched.confirmPassword ? fieldErrors.confirmPassword : ''}
                autoComplete="new-password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              aria-busy={loading}
              className="w-full py-3 mt-1 bg-dark hover:bg-dark-rule disabled:opacity-50 disabled:cursor-not-allowed text-paper font-semibold rounded-[3px] text-[14px] transition-colors shadow-stamp flex items-center justify-center gap-2 focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:outline-none"
            >
              {loading ? t('signup.creatingAccount', 'Creating account…') : t('signup.createAccountButton', 'Create account')}
              {!loading && <ArrowRight aria-hidden="true" className="w-4 h-4" />}
            </button>
          </form>

          <div className="flex items-center gap-3 my-5">
            <div className="h-px bg-rule flex-grow" />
            <span className="text-[12px] font-semibold uppercase tracking-[0.08em] text-ink-muted">{t('signup.or', 'OR')}</span>
            <div className="h-px bg-rule flex-grow" />
          </div>

          <button
            onClick={handleGoogle}
            disabled={loading}
            className="w-full py-3 bg-paper-sunken hover:bg-rule disabled:opacity-50 disabled:cursor-not-allowed border border-rule-strong rounded-[3px] text-[14px] font-medium text-ink transition-colors focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:outline-none"
          >
            {t('signup.continueWithGoogle', 'Continue with Google')}
          </button>

          {/* An account-creation form on a legal product should say what the
              user is agreeing to, and be able to link to it. */}
          <p className="text-[12px] text-ink-tertiary leading-relaxed mt-5 text-center">
            {t('signup.byCreating', 'By creating an account you agree to our')}{' '}
            <Link to="/legal/terms" className="text-accent-text hover:text-accent-deep underline">{t('signup.terms', 'Terms of Service')}</Link>,{' '}
            <Link to="/legal/privacy" className="text-accent-text hover:text-accent-deep underline">{t('signup.privacy', 'Privacy Policy')}</Link>, {t('signup.and', 'and')}{' '}
            <Link to="/legal/disclaimer" className="text-accent-text hover:text-accent-deep underline">{t('signup.disclaimer', 'Legal Disclaimer')}</Link>.
            {t('signup.notLawFirm', ' NYAAY AI is not a law firm.')}
          </p>

          <p className="text-center text-[13px] text-ink-tertiary mt-5">
            {t('signup.alreadyHaveAccount', 'Already have an account?')}{' '}
            <Link
              to="/login"
              state={from ? { from } : undefined}
              className="text-accent-text hover:text-accent-deep hover:underline font-semibold rounded focus-visible:ring-2 focus-visible:ring-accent focus-visible:outline-none"
            >
              {t('signup.signIn', 'Sign in')}
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
