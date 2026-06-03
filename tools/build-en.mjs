#!/usr/bin/env node
// Build an English copy of the app WITHOUT touching index.html.
//
// Strategy: index.html (Traditional Chinese) stays the single source of truth.
// This reads it, applies an exact-string translation map (full, unique strings —
// never bare short words — so replacement can't collide), and writes index.en.html.
// It then reports any user-visible Chinese left untranslated so we can close gaps.
//
// It NEVER writes to index.html.  Usage: node tools/build-en.mjs

import { readFileSync, writeFileSync } from 'node:fs';

const SRC = 'index.html';
const OUT = 'index.en.html';
const map = JSON.parse(readFileSync('tools/i18n-en.json', 'utf8'));

let html = readFileSync(SRC, 'utf8');

// lang + a marker comment so it's obvious this is generated
html = html.replace(/<html lang="zh-Hant">/, '<html lang="en">');
html = '<!-- GENERATED from index.html by tools/build-en.mjs — do not edit by hand -->\n' + html;

// Apply replacements longest-first so a longer phrase wins over any substring.
const keys = Object.keys(map).sort((a, b) => b.length - a.length);
const missesByKey = [];
for (const zh of keys) {
  if (!html.includes(zh)) { missesByKey.push(zh); continue; }
  html = html.split(zh).join(map[zh]);
}

writeFileSync(OUT, html);

// ── report ───────────────────────────────────────────────────────────────────
// 1. stale map entries (string not found in source — likely source changed)
if (missesByKey.length) {
  console.log(`\n⚠️  ${missesByKey.length} map entr(ies) not found in ${SRC} (stale? source changed?):`);
  missesByKey.forEach((k) => console.log('   • ' + JSON.stringify(k.slice(0, 60))));
}

// 2. remaining visible Chinese in the HTML chrome (<body>, outside <script>) —
//    this is where leftover CJK would show as mixed-language UI.
const body = html.slice(html.indexOf('<body>'), html.indexOf('<script>'));
const cjkLines = body.split('\n')
  .map((l, i) => [l, i])
  .filter(([l]) => /[一-鿿]/.test(l));
if (cjkLines.length) {
  console.log(`\n❗ ${cjkLines.length} line(s) of untranslated Chinese remain in the visible HTML chrome:`);
  cjkLines.slice(0, 80).forEach(([l]) => console.log('   • ' + l.trim().slice(0, 100)));
}

// 3. count of remaining CJK in the script (UI strings + intentionally-kept prompt
//    internals are mixed here; this is just an awareness number, not all of it is a bug)
const script = html.slice(html.indexOf('<script>'));
const scriptCJK = (script.match(/[一-鿿]/g) || []).length;
console.log(`\nℹ️  ${scriptCJK} Chinese characters remain inside <script> (UI strings to check + prompt internals kept in Chinese on purpose).`);

console.log(`\n✅ wrote ${OUT} (${(html.length / 1024).toFixed(0)} KB). index.html was NOT modified.`);
