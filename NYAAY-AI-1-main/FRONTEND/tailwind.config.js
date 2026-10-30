/** @type {import('tailwindcss').Config} */

/*
 * NYAAY AI — Single source of colour truth.
 *
 * There is exactly ONE palette. Three families:
 *   paper.*  warm off-white surfaces (light mode canvas)
 *   dark.*   navy surfaces (inverted sections)
 *   ink.*    text on paper
 *   slate.*  text on dark
 *   accent.* rust — the only accent hue in the product
 *
 * Legacy token names (ink / paper / amber / primary / text-*) are kept as
 * ALIASES so untouched pages keep compiling, but they now resolve to the
 * canonical values above. That is deliberate: it collapses the abandoned
 * "Ink & Paper" ochre palette into the current rust one without editing
 * the ~330 call sites that still use the old class names.
 *
 * Contrast (WCAG 2.1 AA, verified against paper.DEFAULT #FAF7F2):
 *   ink.primary   #121820  →  16.1:1
 *   ink.secondary #475467  →   7.2:1
 *   ink.tertiary  #556377  →   5.7:1
 *   ink.muted     #667085  →   4.7:1   (was #7A8699 @ 3.45:1 — FAILED)
 *   accent.text   #A83C25  →   5.9:1   ← use for accent copy under 18px
 *   accent.DEFAULT #C84B31 →   4.4:1   ← icons / >=18px / bold only
 */

const PAPER = '#FAF7F2';
const PAPER_RAISED = '#FFFFFF';
const PAPER_SUNKEN = '#F2EFE9';

const DARK = '#121820';
const DARK_RAISED = '#1A222D';
const DARK_RULE = '#2B3542';

const RULE = '#E4DFD5';
const RULE_STRONG = '#D5CEC2';

const INK_PRIMARY = '#121820';
const INK_SECONDARY = '#475467';
const INK_TERTIARY = '#556377';
const INK_MUTED = '#667085';

const ACCENT = '#C84B31';
const ACCENT_TEXT = '#A83C25';
const ACCENT_DEEP = '#8C271E';
const ACCENT_WASH = '#FAEAE7';

const ON_DARK = '#A2B1C6';
const ON_DARK_MUTED = '#7A8699';

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        // `serif` was MISSING here, so every `font-serif` in the app fell
        // through to Tailwind's default Georgia stack while Newsreader was
        // being downloaded and used only via inline styles. Two serifs
        // shipped side by side. Do not remove this key.
        serif: ['Newsreader', 'Georgia', 'Cambria', 'serif'],
        display: ['Newsreader', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'monospace'],
      },
      colors: {
        /* ---------- canonical ---------- */
        paper: {
          DEFAULT: PAPER,
          raised: PAPER_RAISED,
          sunken: PAPER_SUNKEN,
          // legacy aliases, retargeted
          warm: PAPER_SUNKEN,
          rule: RULE,
          border: RULE_STRONG,
        },
        dark: {
          DEFAULT: DARK,
          raised: DARK_RAISED,
          rule: DARK_RULE,
        },
        ink: {
          DEFAULT: INK_PRIMARY,
          primary: INK_PRIMARY,
          secondary: INK_SECONDARY,
          tertiary: INK_TERTIARY,
          muted: INK_MUTED,
          // legacy aliases, retargeted (#1A1814 warm-black -> canonical navy-black)
          soft: INK_SECONDARY,
          fog: INK_MUTED,
        },
        slate: {
          // text on dark surfaces
          DEFAULT: ON_DARK,
          on: ON_DARK,
          muted: ON_DARK_MUTED,
        },
        accent: {
          DEFAULT: ACCENT,
          text: ACCENT_TEXT,
          hover: ACCENT_TEXT,
          deep: ACCENT_DEEP,
          wash: ACCENT_WASH,
          light: ACCENT_WASH,
          dark: ACCENT_DEEP,
        },
        rule: {
          DEFAULT: RULE,
          strong: RULE_STRONG,
          dark: DARK_RULE,
        },

        /* ---------- legacy aliases (retargeted, do not add more) ---------- */
        // The old "Ink & Paper" ochre accent. Retargeted to rust so the
        // ~50 `bg-amber`/`text-amber` call sites stop shipping a second
        // accent hue. Tailwind deep-merges this into the default amber
        // scale, so `amber-50`..`amber-950` still resolve normally.
        amber: {
          DEFAULT: ACCENT,
          hover: ACCENT_TEXT,
          light: ACCENT_WASH,
          dark: ACCENT_DEEP,
        },
        'bg-dark': DARK,
        'bg-light': PAPER,
        'bg-warm': PAPER_SUNKEN,
        'border-subtle': RULE,
        'ink-primary': INK_PRIMARY,
        'ink-secondary': INK_SECONDARY,
        'ink-muted-new': INK_MUTED,

        background: PAPER_RAISED,
        surface: PAPER,
        primary: {
          DEFAULT: INK_PRIMARY,
          hover: DARK_RULE,
        },
        secondary: {
          DEFAULT: PAPER,
          hover: RULE,
        },
        border: {
          DEFAULT: RULE,
          hover: RULE_STRONG,
        },
        text: {
          primary: INK_PRIMARY,
          secondary: INK_TERTIARY,
          muted: INK_MUTED,
        },
        success: {
          DEFAULT: '#027A48',
          bg: '#E8F5EE',
        },
        warning: {
          DEFAULT: '#B54708',
          bg: '#FEF0C7',
        },
        error: {
          DEFAULT: '#B42318',
          bg: '#FEF3F2',
        },
      },
      fontSize: {
        /* Editorial scale. h1 and h2 are three steps apart, not one. */
        'display-2xl': ['clamp(3rem, 7vw, 6rem)', { lineHeight: '1.0', letterSpacing: '-0.04em' }],
        'display-xl': ['clamp(2.75rem, 6vw, 4.5rem)', { lineHeight: '1.05', letterSpacing: '-0.03em' }],
        'display-lg': ['clamp(2.25rem, 5vw, 3.5rem)', { lineHeight: '1.1', letterSpacing: '-0.025em' }],
        'display-md': ['clamp(1.875rem, 3.5vw, 2.5rem)', { lineHeight: '1.15', letterSpacing: '-0.02em' }],
        'heading': ['clamp(1.375rem, 2.5vw, 1.75rem)', { lineHeight: '1.25', letterSpacing: '-0.015em' }],
        /* 12px is the floor for uppercase tracked labels. */
        'label': ['12px', { lineHeight: '1.4', letterSpacing: '0.08em' }],
        'label-sm': ['12px', { lineHeight: '1.4', letterSpacing: '0.08em' }],
        'label-xs': ['12px', { lineHeight: '1.4', letterSpacing: '0.1em' }],
      },
      boxShadow: {
        'stamp': '0 1px 2px rgba(18,24,32,0.06), 0 0 0 1px rgba(18,24,32,0.04)',
        'card': '0 2px 8px rgba(18,24,32,0.08), 0 1px 2px rgba(18,24,32,0.04)',
        'lifted': '0 8px 24px rgba(18,24,32,0.10), 0 2px 6px rgba(18,24,32,0.06)',
        'modal': '0 24px 48px rgba(18,24,32,0.14), 0 8px 16px rgba(18,24,32,0.08)',
      },
      borderRadius: {
        'stamp': '2px',
        'card': '4px',
        'button': '3px',
        'input': '3px',
        'modal': '6px',
        'xl': '8px',
        '2xl': '10px',
        '3xl': '12px',
        'full': '9999px',
      },
      animation: {
        'stamp-in': 'stampIn 200ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'cursor-pulse': 'cursorPulse 900ms ease-in-out infinite',
        'fade-up': 'fadeUp 300ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'slide-in': 'slideIn 200ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'shimmer': 'shimmer 1.6s ease-in-out infinite',
      },
      keyframes: {
        stampIn: {
          '0%': { opacity: '0', transform: 'translateY(6px) scale(0.99)' },
          '100%': { opacity: '1', transform: 'translateY(0) scale(1)' },
        },
        cursorPulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-8px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        shimmer: {
          '0%, 100%': { opacity: '0.45' },
          '50%': { opacity: '0.85' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
