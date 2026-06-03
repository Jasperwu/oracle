#!/usr/bin/env node
// Reference-integrity validator for the single-file app.
//
// Why this exists: `node --check` only catches *syntax* errors. The bugs that
// actually white-screen this app are *broken references* — e.g. el.marketSource
// pointing at an id that was renamed, or $('foo') where no id="foo" exists.
// Those parse fine but crash at runtime. This script catches that whole class
// in ~1 second, WITHOUT touching index.html.
//
// Usage:   node tools/validate.mjs [index.html]
// Exit:    0 = clean, 1 = errors found (safe to gate commits / CI on this).

import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const file = process.argv[2] || 'index.html';
const html = readFileSync(file, 'utf8');
const errors = [];
const warnings = [];

// ── 1. Syntax-check every <script> block (same as `node --check`) ────────────
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
const tmp = mkdtempSync(join(tmpdir(), 'validate-'));
scripts.forEach((src, i) => {
  const f = join(tmp, `block${i}.js`);
  writeFileSync(f, src);
  try {
    execFileSync(process.execPath, ['--check', f], { stdio: 'pipe' });
  } catch (e) {
    errors.push(`Syntax error in <script> block #${i}:\n${(e.stderr || e.stdout || e.message).toString().trim()}`);
  }
});
const js = scripts.join('\n');

// ── 2. Element-id integrity: every $('id') / getElementById('id') must exist ─
// "Defined" ids = any id="..." in the file (HTML + innerHTML template strings)
// plus any assigned dynamically via `.id = '...'`.
const definedIds = new Set();
for (const m of html.matchAll(/\bid=["']([A-Za-z0-9_-]+)["']/g)) definedIds.add(m[1]);
for (const m of js.matchAll(/\.id\s*=\s*["']([A-Za-z0-9_-]+)["']/g)) definedIds.add(m[1]);

// "Referenced" ids = $('literal') or getElementById('literal'). Template/var
// args (e.g. $('scout' + i) or `scout-${id}`) are skipped — they're dynamic.
const idRefs = new Map();
for (const m of js.matchAll(/(?:\$|getElementById)\(\s*["']([A-Za-z0-9_-]+)["']\s*\)/g)) {
  idRefs.set(m[1], (idRefs.get(m[1]) || 0) + 1);
}
for (const id of [...idRefs.keys()].sort()) {
  if (!definedIds.has(id)) {
    errors.push(`Element id "${id}" is fetched via $()/getElementById (${idRefs.get(id)}×) but no id="${id}" exists in the HTML → runtime null.`);
  }
}

// ── 3. el.* integrity: catch typos like el.marketSource vs the el map keys ───
// (el is declared exactly once as `const el = { … }` and never reused as a
//  local variable in this codebase, so this check is false-positive-free.)
const elKeys = new Set();
const start = js.indexOf('const el = {');
if (start === -1) {
  warnings.push('Could not find `const el = {` — skipping el.* check.');
} else {
  // brace-match to find the object body
  let depth = 0, i = js.indexOf('{', start), end = -1;
  for (; i < js.length; i++) {
    if (js[i] === '{') depth++;
    else if (js[i] === '}') { depth--; if (depth === 0) { end = i; break; } }
  }
  const body = js.slice(start, end);
  for (const m of body.matchAll(/(\w+)\s*:/g)) elKeys.add(m[1]);
  for (const m of js.matchAll(/\bel\.(\w+)\s*=/g)) elKeys.add(m[1]); // dynamically-added props
  const elUses = new Map();
  for (const m of js.matchAll(/\bel\.(\w+)\b/g)) elUses.set(m[1], (elUses.get(m[1]) || 0) + 1);
  for (const k of [...elUses.keys()].sort()) {
    if (!elKeys.has(k)) {
      errors.push(`el.${k} is used (${elUses.get(k)}×) but is not a key in the el map → likely a typo / renamed element.`);
    }
  }
}

// ── report ──────────────────────────────────────────────────────────────────
const n = (a) => a.length;
if (warnings.length) {
  console.log(`\n⚠️  ${n(warnings)} warning(s):`);
  warnings.forEach((w) => console.log('   • ' + w));
}
if (errors.length) {
  console.log(`\n❌ ${n(errors)} error(s):\n`);
  errors.forEach((e) => console.log('   • ' + e + '\n'));
  console.log(`Validation FAILED for ${file}.`);
  process.exit(1);
}
console.log(`✅ ${file} passed: syntax OK · ${idRefs.size} element ids resolve · ${elKeys.size} el.* keys consistent.`);
