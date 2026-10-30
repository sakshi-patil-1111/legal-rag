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
    } else if (file.endsWith('.jsx') || file.endsWith('.tsx') || file.endsWith('.js') || file.endsWith('.ts')) {
      results.push(full);
    }
  });
  return results;
}

const allSrc = walk(path.join(__dirname, '../src'));

let hrefHash = [];
let alertConfirm = [];
let fontBlackSerif = [];
let onStartDemoFlow = [];
let materialSymbols = [];
let hexCount = 0;
let fontMonoCount = 0;

allSrc.forEach(f => {
  const c = fs.readFileSync(f, 'utf8');
  if (c.includes('href="#"') || c.includes("href='#'")) hrefHash.push(f);
  if (/alert\(|window\.confirm\(/.test(c)) alertConfirm.push(f);
  if (/font-serif.*font-black|font-black.*font-serif/.test(c)) fontBlackSerif.push(f);
  if (c.includes('onStartDemoFlow')) onStartDemoFlow.push(f);
  if (c.includes('material-symbols') || c.includes('material-icons')) materialSymbols.push(f);

  const hexMatches = c.match(/#[0-9A-Fa-f]{6}/g);
  if (hexMatches) hexCount += hexMatches.length;

  const monoMatches = c.match(/font-mono/g);
  if (monoMatches) fontMonoCount += monoMatches.length;
});

console.log('=== AUDIT RESULTS ===');
console.log('Total files checked:', allSrc.length);
console.log('1. href="#" count:', hrefHash.length, hrefHash);
console.log('2. alert/confirm count:', alertConfirm.length, alertConfirm);
console.log('3. font-serif + font-black count:', fontBlackSerif.length, fontBlackSerif);
console.log('4. onStartDemoFlow count:', onStartDemoFlow.length, onStartDemoFlow);
console.log('5. Material symbols count:', materialSymbols.length, materialSymbols);
console.log('6. font-mono count:', fontMonoCount);
console.log('7. Hex literals count:', hexCount);
