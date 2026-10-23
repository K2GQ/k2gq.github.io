/* Offline regression tests for development OCR v2 display. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const view = require('../scripts/view-data.js');
const folder = path.resolve(__dirname, '../data');
const read = name => JSON.parse(fs.readFileSync(path.join(folder, name), 'utf8'));
const v2 = read('cell-ocr-archive.json');
const old = read('preview.json');
const ref = read('reviewed.json');
const originals = [JSON.stringify(v2),JSON.stringify(old),JSON.stringify(ref)];
const result = view.build(v2, old, ref);
const dates = rows => new Set(rows.map(row => row.date));
const reviewedDays = dates(ref.rows);
assert.equal(v2.kind, 'cell-ocr-v2-full-archive-experimental');
assert.equal(result.nets.length, 162);
assert.equal(result.checkins.length, 1724);
assert.equal(result.comparison.length, 162);
assert.equal(result.stats.original_rows, 1436);
assert.equal(result.stats.cell_rows, 1724);
assert.equal(result.stats.displayed_rows, 1724);
assert.equal(result.stats.verified_rows, 38);
assert.equal(result.stats.provisional_rows, 1686);
assert.equal(result.stats.verified_nets, 4);
assert.equal(result.stats.increased_nets, 137);
assert.equal(result.stats.unchanged_nets, 25);
assert.equal(result.stats.decreased_nets, 0);
assert.equal(result.stats.cell_review_flags, 1128);
assert.equal(new Set(result.nets.map(n => n.date)).size, 162);
assert.equal(result.comparison.reduce((sum, n) => sum + n.delta, 0), 288);
assert.equal(result.comparison.reduce((sum, n) => sum + n.original, 0), 1436);
assert.equal(result.comparison.reduce((sum, n) => sum + n.improved, 0), 1724);
for (const original of ref.rows) {
  const displayed = result.checkins.find(r => r.date === original.date && r.number === original.number);
  assert(displayed, 'Missing reviewed date '+original.date+' row '+original.number);
  for (const field of ['date','number','callsign','name','city','county','state','country','remarks']) {
    assert.equal(displayed[field], original[field], 'Reviewed override '+original.date+' #'+original.number+' '+field);
  }
  assert.equal(displayed.reviewed, true);
}
for (const net of result.nets) {
  const rows = result.checkins.filter(r => r.date === net.date);
  assert.equal(rows.length, net.ocr_rows);
  assert.equal(net.reviewed, reviewedDays.has(net.date));
  assert.match(net.image, /^\/assets\/img\/net-\d{4}-\d\d-\d\d\.png$/);
  if (net.reviewed) assert(rows.every(r => r.reviewed && !r.needs_review));
  else assert(rows.every(r => !r.reviewed));
}
assert.deepEqual([...dates(result.checkins)].sort(), [...dates(v2.checkins)].sort());
assert.equal(JSON.stringify(v2), originals[0], 'Cell source mutated');
assert.equal(JSON.stringify(old), originals[1], 'Legacy source mutated');
assert.equal(JSON.stringify(ref), originals[2], 'Reviewed source mutated');

function small() {
  return [
    {kind:'cell-ocr-v2-full-archive-experimental',
      nets:[{date:'2026-10-20',image:'/assets/img/net-2026-10-20.png',ocr_rows:1}],
      checkins:[{date:'2026-10-20', image_row:1, callsign:'KC2N',name:'Michael A Abbey',
                 needs_review:true,raw_callsign:'KC2N'}]},
    {nets:[{date:'2026-10-20',ocr_rows:1}],checkins:[{date:'2026-10-20'}]},
    {rows:[{date:'2026-10-20',number:1,callsign:'KC2NJ',name:'Michael A Abbey',reviewed:true}]}
  ];
}
const [mini,prior,manual]=small();
const transformed=view.build(mini,prior,manual);
assert.equal(transformed.checkins[0].callsign,'KC2NJ','Manual value overrides OCR');
assert.equal(transformed.checkins[0].reviewed,true);
assert.equal(transformed.comparison[0].improved,1,'Compare raw OCR, not overlay');
assert.equal(transformed.stats.cell_review_flags,1,'Flag raw OCR independently');
assert.throws(() => {const [x,y,z]=small(); z.rows[0].reviewed=false; view.build(x,y,z);},
              /verification/);
assert.throws(() => {const [x,y,z]=small(); z.rows.push({...z.rows[0], number:3}); view.build(x,y,z);},
              /Incomplete reviewed roster/);
assert.throws(() => {const [x,y,z]=small(); x.nets[0].ocr_rows=2; view.build(x,y,z);},
              /row count/);
assert.throws(() => {const [x,y,z]=small(); y.nets[0].date='2026-10-13'; view.build(x,y,z);},
              /different net dates/);
assert.throws(() => {const [x,y,z]=small(); x.checkins[0].date='2026-13-02'; view.build(x,y,z);},
              /Invalid net date/);
const html=fs.readFileSync(path.resolve(__dirname,'../index.html'),'utf8');
assert.match(html, /netreports-dev\/scripts\/view-data\.js/);
assert.match(html, /netreports-dev\/data\/cell-ocr-archive\.json/);
assert.match(html, /netreports-dev\/data\/preview\.json/);
assert.match(html, /netreports-dev\/data\/reviewed\.json/);
assert.match(html, /id="nr-panel-compare"/);
assert.doesNotMatch(html, /nr-export|exportCSV|text\/csv|\['status','Status'\]|\['review_status','Review status'\]/);
const inline=html.match(/<script>([\s\S]*?)<\/script>/);
assert(inline, 'UI script required');
new Function(inline[1]);
console.log('PASS: 162 nets; 1724 candidates; 38 verified; 288 additional OCR rows; 1128 review flags.');
