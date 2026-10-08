// Render every .dot under <dir> to .svg and every .svg to .png (2x, capped width).
// Usage: node render.mjs <dir>   (run where @viz-js/viz and @resvg/resvg-js are installed)
import { instance } from '@viz-js/viz';
import { Resvg } from '@resvg/resvg-js';
import fs from 'node:fs';
import path from 'node:path';

const root = process.argv[2];
const viz = await instance();

function* walk(d) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, e.name);
    if (e.isDirectory()) yield* walk(p); else yield p;
  }
}

let n = 0;
const failures = [];
for (const f of walk(root)) {
  if (f.endsWith('.dot')) {
    try {
      const svg = viz.renderString(fs.readFileSync(f, 'utf8'), { format: 'svg' });
      fs.writeFileSync(f.replace(/\.dot$/, '.svg'), svg);
    } catch (e) { failures.push(f + ': ' + e.message.split('\n')[0]); }
  }
}
for (const f of walk(root)) {
  if (f.endsWith('.svg')) {
    try {
      const svg = fs.readFileSync(f, 'utf8');
      const w = parseFloat((svg.match(/<svg[^>]*width="([\d.]+)pt"/) || [])[1] || 1000);
      const target = Math.min(Math.round(w * 2), 5200);
      const png = new Resvg(svg, { fitTo: { mode: 'width', value: target }, background: 'white', font: { loadSystemFonts: true, defaultFontFamily: 'Helvetica' } }).render().asPng();
      fs.writeFileSync(f.replace(/\.svg$/, '.png'), png);
      n++;
    } catch (e) { failures.push(f + ': ' + e.message.split('\n')[0]); }
  }
}
console.log('rendered', n, 'png;', failures.length, 'failures');
failures.forEach(x => console.log('  FAIL', x));
