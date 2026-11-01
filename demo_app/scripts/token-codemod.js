import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function walk(dir) {
  let results = [];
  if (!fs.existsSync(dir)) return results;
  const list = fs.readdirSync(dir);
  list.forEach(file => {
    const full = path.join(dir, file);
    const stat = fs.statSync(full);
    if (stat && stat.isDirectory()) {
      results = results.concat(walk(full));
    } else if (file.endsWith('.jsx') || file.endsWith('.tsx')) {
      results.push(full);
    }
  });
  return results;
}

// Ordered token replacements (longest/most specific first)
const REPLACEMENTS = [
  // Focus / ring states
  { from: /focus-visible:ring-\[#C84B31\]/g, to: 'focus-visible:ring-accent' },
  { from: /focus-visible:ring-\[#121820\]/g, to: 'focus-visible:ring-dark' },
  { from: /focus:ring-\[#C84B31\]/g, to: 'focus:ring-accent' },
  { from: /focus:ring-\[#121820\]/g, to: 'focus:ring-dark' },
  { from: /focus:border-\[#C84B31\]/g, to: 'focus:border-accent' },
  { from: /focus:border-\[#121820\]/g, to: 'focus:border-dark' },
  { from: /ring-\[#C84B31\]/g, to: 'ring-accent' },
  { from: /ring-\[#121820\]/g, to: 'ring-dark' },

  // Hover states
  { from: /hover:bg-\[#2B3542\]/g, to: 'hover:bg-dark-rule' },
  { from: /hover:bg-\[#121820\]/g, to: 'hover:bg-dark' },
  { from: /hover:bg-\[#1A222D\]/g, to: 'hover:bg-dark-raised' },
  { from: /hover:bg-\[#F2EFE9\]/g, to: 'hover:bg-paper-sunken' },
  { from: /hover:bg-\[#FAF7F2\]/g, to: 'hover:bg-paper' },
  { from: /hover:bg-\[#C84B31\]/g, to: 'hover:bg-accent' },
  { from: /hover:bg-\[#A83C25\]/g, to: 'hover:bg-accent-hover' },
  { from: /hover:bg-\[#8C271E\]/g, to: 'hover:bg-accent-deep' },
  { from: /hover:bg-\[#E4DFD5\]/g, to: 'hover:bg-rule' },
  { from: /hover:border-\[#121820\]/g, to: 'hover:border-dark' },
  { from: /hover:border-\[#C84B31\]/g, to: 'hover:border-accent' },
  { from: /hover:border-\[#E4DFD5\]/g, to: 'hover:border-rule' },
  { from: /hover:border-\[#D5CEC2\]/g, to: 'hover:border-rule-strong' },
  { from: /hover:border-\[#667085\]/g, to: 'hover:border-ink-muted' },
  { from: /hover:text-\[#8C271E\]/g, to: 'hover:text-accent-deep' },
  { from: /hover:text-\[#A83C25\]/g, to: 'hover:text-accent-hover' },
  { from: /hover:text-\[#C84B31\]/g, to: 'hover:text-accent' },
  { from: /hover:text-\[#121820\]/g, to: 'hover:text-ink' },
  { from: /hover:text-\[#FAF7F2\]/g, to: 'hover:text-paper' },
  { from: /hover:text-\[#667085\]/g, to: 'hover:text-ink-muted' },

  // Background colors
  { from: /bg-\[#FAF7F2\]/g, to: 'bg-paper' },
  { from: /bg-\[#F2EFE9\]/g, to: 'bg-paper-sunken' },
  { from: /bg-\[#121820\]/g, to: 'bg-dark' },
  { from: /bg-\[#1A222D\]/g, to: 'bg-dark-raised' },
  { from: /bg-\[#2B3542\]/g, to: 'bg-dark-rule' },
  { from: /bg-\[#C84B31\]/g, to: 'bg-accent' },
  { from: /bg-\[#A83C25\]/g, to: 'bg-accent-hover' },
  { from: /bg-\[#8C271E\]/g, to: 'bg-accent-deep' },
  { from: /bg-\[#FAEAE7\]/g, to: 'bg-accent-wash' },
  { from: /bg-\[#E4DFD5\]/g, to: 'bg-rule' },
  { from: /bg-\[#D5CEC2\]/g, to: 'bg-rule-strong' },
  { from: /bg-\[#FEF3F2\]/g, to: 'bg-error-bg' },
  { from: /bg-\[#E8F5EE\]/g, to: 'bg-success-bg' },

  // Text colors
  { from: /text-\[#121820\]/g, to: 'text-ink' },
  { from: /text-\[#475467\]/g, to: 'text-ink-secondary' },
  { from: /text-\[#556377\]/g, to: 'text-ink-tertiary' },
  { from: /text-\[#667085\]/g, to: 'text-ink-muted' },
  { from: /text-\[#A83C25\]/g, to: 'text-accent-text' },
  { from: /text-\[#C84B31\]/g, to: 'text-accent' },
  { from: /text-\[#8C271E\]/g, to: 'text-accent-deep' },
  { from: /text-\[#A2B1C6\]/g, to: 'text-slate' },
  { from: /text-\[#7A8699\]/g, to: 'text-slate-muted' },
  { from: /text-\[#FAF7F2\]/g, to: 'text-paper' },
  { from: /text-\[#D5CEC2\]/g, to: 'text-rule-strong' },
  { from: /text-\[#E4DFD5\]/g, to: 'text-rule' },
  { from: /text-\[#B42318\]/g, to: 'text-error' },
  { from: /text-\[#027A48\]/g, to: 'text-success' },
  { from: /text-\[#B54708\]/g, to: 'text-warning' },

  // Borders
  { from: /border-\[#E4DFD5\]/g, to: 'border-rule' },
  { from: /border-\[#D5CEC2\]/g, to: 'border-rule-strong' },
  { from: /border-\[#2B3542\]/g, to: 'border-rule-dark' },
  { from: /border-\[#121820\]/g, to: 'border-dark' },
  { from: /border-\[#C84B31\]/g, to: 'border-accent' },
  { from: /border-\[#A83C25\]/g, to: 'border-accent-hover' },
  { from: /border-\[#8C271E\]/g, to: 'border-accent-deep' },
  { from: /border-\[#F2EFE9\]/g, to: 'border-paper-sunken' },
  { from: /border-\[#FAF7F2\]/g, to: 'border-paper' },
  { from: /border-\[#B42318\]/g, to: 'border-error' },
  { from: /border-l-\[#C84B31\]/g, to: 'border-l-accent' },
  { from: /border-l-\[#121820\]/g, to: 'border-l-dark' },
  { from: /border-r-\[#E4DFD5\]/g, to: 'border-r-rule' },
  { from: /border-t-\[#E4DFD5\]/g, to: 'border-t-rule' },
  { from: /border-b-\[#E4DFD5\]/g, to: 'border-b-rule' },
  { from: /border-t-\[#2B3542\]/g, to: 'border-t-rule-dark' },
  { from: /border-b-\[#2B3542\]/g, to: 'border-b-rule-dark' },
  { from: /border-t-\[#F2EFE9\]/g, to: 'border-t-paper-sunken' },
  { from: /border-b-\[#F2EFE9\]/g, to: 'border-b-paper-sunken' },
  { from: /border-b-\[#C84B31\]/g, to: 'border-b-accent' },
  { from: /border-l-\[#E4DFD5\]/g, to: 'border-l-rule' },

  // Placeholder
  { from: /placeholder-\[#667085\]/g, to: 'placeholder-ink-muted' },
  { from: /placeholder-\[#556377\]/g, to: 'placeholder-ink-tertiary' }
];

const files = walk(path.join(__dirname, '../src'));
let totalReplaced = 0;

files.forEach(f => {
  let content = fs.readFileSync(f, 'utf8');
  let original = content;

  REPLACEMENTS.forEach(({ from, to }) => {
    const matches = content.match(from);
    if (matches) {
      totalReplaced += matches.length;
      content = content.replace(from, to);
    }
  });

  if (content !== original) {
    fs.writeFileSync(f, content, 'utf8');
    const rel = path.relative(path.join(__dirname, '..'), f);
    console.log(`Updated tokens in ${rel}`);
  }
});

console.log(`\nCodemod completed! Total replacements made: ${totalReplaced}`);
