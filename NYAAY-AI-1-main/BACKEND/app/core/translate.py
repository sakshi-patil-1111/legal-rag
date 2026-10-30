"""
app/core/translate.py
─────────────────────────────────────────────────────────────────────────────
Two-layer translation module for NYAAY AI multilingual support.

ARCHITECTURE GUARANTEE:
  translate_in  — controlled entirely by detected_lang (query language heuristic)
  translate_out — controlled entirely by language (UI toggle / target language)
  These are NEVER combined. Each is called independently.

CITATION PROTECTION (structural, not prompt-only):
  Before translate_out:
    1. Extract all [[...]] citation spans → { "__CITE_0__": "[[original]]", ... }
    2. Replace spans with placeholder tokens in text
    3. Send placeholder-bearing text to Groq (model sees __CITE_0__, not [[...]])
    4. After Groq returns: substitute __CITE_0__ → original [[...]] back
  The prompt also instructs preservation as belt-and-suspenders, but
  re-insertion is structural — it works even if the model ignores the prompt.

CALL COUNT EXPECTATIONS (test matrix):
  English UI + English query  → 0 Groq calls
  Hindi UI   + English query  → 1 call (translate_out only)
  English UI + Hindi query    → 1 call (translate_in only)
  Hindi UI   + Hindi query    → 2 calls
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ─── Supported languages ─────────────────────────────────────────────────────

SUPPORTED_LANGS = {"hi", "bn", "ta"}

LANG_NAMES = {
    "hi": "Hindi",
    "bn": "Bengali",
    "ta": "Tamil",
}

# ─── Legal glossary ───────────────────────────────────────────────────────────

LEGAL_GLOSSARY: dict = {
    "hi": {
        "FIR":                    "प्राथमिकी (FIR)",
        "bail":                   "ज़मानत",
        "anticipatory bail":      "अग्रिम ज़मानत",
        "cognizable offence":     "संज्ञेय अपराध",
        "non-cognizable offence": "असंज्ञेय अपराध",
        "RTI":                    "सूचना का अधिकार (RTI)",
        "writ":                   "रिट",
        "PIL":                    "जनहित याचिका (PIL)",
        "security deposit":       "सुरक्षा जमा",
        "appellate authority":    "अपीलीय प्राधिकरण",
        "limitation period":      "परिसीमा अवधि",
        "affidavit":              "शपथपत्र",
    },
    "bn": {
        "FIR":                    "এফআইআর (FIR - প্রথম তথ্য প্রতিবেদন)",
        "bail":                   "জামিন",
        "anticipatory bail":      "অগ্রিম জামিন",
        "cognizable offence":     "আমলযোগ্য অপরাধ",
        "non-cognizable offence": "অ-আমলযোগ্য অপরাধ",
        "RTI":                    "তথ্য অধিকার (RTI)",
        "writ":                   "রিট",
        "PIL":                    "জনস্বার্থ মামলা (PIL)",
        "security deposit":       "নিরাপত্তা আমানত",
        "appellate authority":    "আপিল কর্তৃপক্ষ",
        "limitation period":      "সীমাবদ্ধতার মেয়াদ",
        "affidavit":              "হলফনামা",
    },
    "ta": {
        "FIR":                    "முதல் தகவல் அறிக்கை (FIR)",
        "bail":                   "ஜாமீன்",
        "anticipatory bail":      "முன்கூட்டிய ஜாமீன்",
        "cognizable offence":     "அறிவிக்கக்கூடிய குற்றம்",
        "non-cognizable offence": "அறிவிக்க முடியாத குற்றம்",
        "RTI":                    "தகவல் அறியும் உரிமை (RTI)",
        "writ":                   "ரிட்",
        "PIL":                    "பொது நல வழக்கு (PIL)",
        "security deposit":       "பாதுகாப்பு வைப்பு",
        "appellate authority":    "மேல்முறையீட்டு அதிகாரம்",
        "limitation period":      "வரம்பு காலம்",
        "affidavit":              "உறுதிமொழி",
    },
}

# ─── Citation placeholder helpers ────────────────────────────────────────────

# Matches [[...]] citation markers produced by the RAG pipeline.
_CITE_PATTERN = re.compile(r'\[\[.*?\]\]', re.DOTALL)


def _extract_citations(text: str) -> tuple:
    """
    Replace all [[...]] spans with sequential __CITE_N__ placeholder tokens.

    Returns:
        (protected_text, {token: original_span})

    Example:
        "Under [[RTI Act §7]], you must..." →
        "Under __CITE_0__, you must..."
        { "__CITE_0__": "[[RTI Act §7]]" }
    """
    mapping: dict = {}
    counter = 0

    def replacer(m: re.Match) -> str:
        nonlocal counter
        token = f"__CITE_{counter}__"
        mapping[token] = m.group(0)
        counter += 1
        return token

    protected = _CITE_PATTERN.sub(replacer, text)
    return protected, mapping


def _restore_citations(text: str, mapping: dict) -> str:
    """
    Substitute __CITE_N__ tokens back with their original [[...]] spans.
    Handles exact match first, then a whitespace-tolerant fallback.
    """
    for token, original in mapping.items():
        if token in text:
            text = text.replace(token, original)
        else:
            # Fallback: token may have gained surrounding spaces/punctuation
            flexible_pat = token.replace("_", r"_\s*")
            text = re.sub(flexible_pat, original, text)
    return text


# ─── Groq client (lazy singleton) ────────────────────────────────────────────

_groq_client = None


def _get_client():
    global _groq_client
    if _groq_client is None:
        from groq import Groq
        from app.core.config import settings
        if not settings.GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not configured. "
                "Set it in BACKEND/.env before using translation features."
            )
        # Key is passed directly — never stored in logs or variables beyond this scope
        _groq_client = Groq(api_key=settings.GROQ_API_KEY)
    return _groq_client


GROQ_MODEL = "qwen/qwen3.8-27b"


# ─── translate_in ─────────────────────────────────────────────────────────────

async def translate_in(text: str, detected_lang: str) -> str:
    """
    Translate a non-English user query into English before RAG.

    Called ONLY when detected_lang != 'en'.
    Controlled SOLELY by detected_lang — never by the UI language toggle.

    Fallback on any failure: returns original text (RAG degrades gracefully).
    """
    lang_name = LANG_NAMES.get(detected_lang, detected_lang)
    logger.info("translate_in: %s → en  [1 Groq call]", detected_lang)

    system_prompt = (
        f"You are a precise translator. "
        f"Translate the following {lang_name} legal query into English. "
        f"Preserve legal terms, proper nouns, Act names, and section references exactly. "
        f"Output the English translation only — no explanation, no commentary."
    )

    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": text},
            ],
            max_tokens=512,
            temperature=0.2,
        )
        translated = resp.choices[0].message.content.strip()
        logger.info("translate_in OK — %d tokens", resp.usage.total_tokens)
        return translated

    except Exception as e:
        logger.warning("translate_in FAILED (%s) — original query passed to RAG", _scrub(str(e)))
        return text  # Graceful fallback


# ─── translate_out ────────────────────────────────────────────────────────────

async def translate_out(text: str, target_lang: str) -> tuple:
    """
    Translate the assembled English RAG response into the target language.

    Called ONLY when target_lang != 'en'.
    Controlled SOLELY by target_lang (UI toggle) — never by detected_lang.

    Citation protection steps:
        1. _extract_citations: [[...]] → __CITE_N__ in text + mapping dict
        2. Send protected text to Groq
        3. _restore_citations: __CITE_N__ → [[...]] in Groq output
        Model never sees the raw [[...]] markers — placeholders are opaque.

    Returns:
        (translated_text, None)              — success
        (original_english_text, notice_str)  — on any Groq failure
    """
    lang_name = LANG_NAMES.get(target_lang, target_lang)
    glossary  = LEGAL_GLOSSARY.get(target_lang, {})
    logger.info("translate_out: en → %s  [1 Groq call]", target_lang)

    # ── Step 1: Protect citation markers ─────────────────────────────────────
    protected_text, cite_map = _extract_citations(text)
    logger.debug("translate_out: protected %d citation span(s)", len(cite_map))

    # ── Step 2: Build glossary injection ─────────────────────────────────────
    gloss_lines  = [f'  "{k}" → "{v}"' for k, v in glossary.items()]
    glossary_str = "\n".join(gloss_lines) if gloss_lines else "  (none)"

    system_prompt = (
        f"You are a legal translation assistant specialising in Indian law.\n"
        f"Translate the following English text into {lang_name}.\n\n"
        f"STRICT RULES:\n"
        f"1. Tokens of the form __CITE_N__ (e.g. __CITE_0__) are citation placeholders. "
        f"   Copy them EXACTLY as-is — do NOT translate or modify them.\n"
        f"2. Keep Act names, section numbers, and case references in English.\n"
        f"3. Use these verified legal term mappings:\n{glossary_str}\n"
        f"4. IF the input is a JSON string, you MUST output valid JSON and you MUST NOT "
        f"   translate the JSON keys. Translate ONLY the string values. Keep arrays and structure intact.\n"
        f"5. Output translated text (or JSON) only. No explanations, no markdown wrapper.\n"
    )

    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": protected_text},
            ],
            max_tokens=4096,
            temperature=0.2,
        )
        translated_protected = resp.choices[0].message.content.strip()
        logger.info("translate_out OK — %d tokens", resp.usage.total_tokens)

        # ── Step 3: Restore citation markers ─────────────────────────────────
        translated_final = _restore_citations(translated_protected, cite_map)

        return translated_final, None

    except Exception as e:
        logger.warning("translate_out FAILED (%s) — English response returned", _scrub(str(e)))
        notice = "Translation unavailable — showing English response."
        return text, notice  # Original English text + notice for frontend


# ─── Key scrubber ─────────────────────────────────────────────────────────────

def _scrub(s: str) -> str:
    """Remove GROQ_API_KEY value from any string before it enters logs."""
    try:
        from app.core.config import settings
        key = settings.GROQ_API_KEY
        if key and len(key) > 4 and key in s:
            s = s.replace(key, "[REDACTED]")
    except Exception:
        pass
    return s
