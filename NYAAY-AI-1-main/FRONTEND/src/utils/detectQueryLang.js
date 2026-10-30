export function detectQueryLang(query) {
  if (!query) return 'en';
  
  // Basic heuristic: check for Unicode ranges of supported languages
  const hindiRegex = /[\u0900-\u097F]/;
  const bengaliRegex = /[\u0980-\u09FF]/;
  const tamilRegex = /[\u0B80-\u0BFF]/;
  
  if (hindiRegex.test(query)) {
    return 'hi';
  }
  
  if (bengaliRegex.test(query)) {
    return 'bn';
  }
  
  if (tamilRegex.test(query)) {
    return 'ta';
  }
  
  // Default to English if no matching characters are found
  return 'en';
}
