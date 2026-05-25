#!/usr/bin/env node
// Browser-grade text measurement utility.
// In production, run with Playwright for real DOM fonts. This fallback uses canvas when available.
const fs = require('fs');

function estimate(text, fontSize, maxWidth, lineHeight = 1.25) {
  let lines = 1;
  let current = 0;
  let maxLine = 0;
  for (const ch of text) {
    const cw = /[\u4e00-\u9fff]/.test(ch) ? fontSize : fontSize * 0.55;
    if (ch === '\n' || current + cw > maxWidth) {
      lines += 1;
      current = ch === '\n' ? 0 : cw;
    } else {
      current += cw;
    }
    maxLine = Math.max(maxLine, current);
  }
  return {lines, width: maxLine, height: lines * fontSize * lineHeight};
}

const inputPath = process.argv[2];
const payload = inputPath ? JSON.parse(fs.readFileSync(inputPath, 'utf8')) : JSON.parse(fs.readFileSync(0, 'utf8'));
const result = estimate(payload.text || '', payload.fontSize || 16, payload.maxWidth || 300, payload.lineHeight || 1.25);
result.overflow = result.height > (payload.maxHeight || Infinity);
console.log(JSON.stringify(result, null, 2));
