/* Lightweight DOM regression checks for the inline Net Reports dashboards.
 * No external dependencies. Run from repository root: node netreports-dev/tests/test_dashboard.js
 */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

function inlineScript(filename) {
  const html = fs.readFileSync(filename, 'utf8');
  const match = html.match(/<script>([\s\S]*?)<\/script>/);
  assert.ok(match, 'Dashboard script missing from ' + filename);
  return match[1];
}
const prod = inlineScript('netreports.md');
const dev = inlineScript('netreports-dev/index.html');
assert.equal(prod, dev, 'Published and development dashboard logic must stay identical');
assert.doesNotMatch(prod, /POSSIBLY INCOMPLETE/i, 'Completed nets must not display a warning');
new vm.Script(prod);
const prodStyle=fs.readFileSync('netreports.md','utf8').match(/<style>([\s\S]*?)<\/style>/)[1];
const devStyle=fs.readFileSync('netreports-dev/index.html','utf8').match(/<style>([\s\S]*?)<\/style>/)[1];
assert.equal(prodStyle,devStyle,'Production and development styles must stay synchronized');
assert.match(prodStyle,/#net-db #weekly-table th button\s*\{\s*white-space:nowrap;\s*\}/,
  'Weekly report headings must stay on one line on desktop');
assert.match(prodStyle,/#net-db #weekly-table th:nth-child\(6\)\s*\{\s*width:8%;\s*\}/,
  'State column needs sufficient desktop space');

class Element {
  constructor(tag='div') {
    this.tag=tag; this.children=[]; this.attrs={}; this.listeners={};
    this._text=''; this.value=''; this.hidden=false; this.style={}; this.className='';
  }
  get firstChild() { return this.children[0] || null; }
  get textContent() { return this._text || this.children.map(c=>c.textContent).join(''); }
  set textContent(value) { this._text=String(value); this.children=[]; }
  appendChild(child) { this.children.push(child); return child; }
  removeChild(child) { this.children.splice(this.children.indexOf(child),1); return child; }
  setAttribute(key,value) { this.attrs[key]=String(value); }
  getAttribute(key) { return this.attrs[key]; }
  addEventListener(key,listener) { (this.listeners[key] ||= []).push(listener); }
  focus() { document.activeElement=this; }
  trigger(key) { (this.listeners[key] || []).forEach(listener=>listener({preventDefault(){}})); }
}
const elements=new Map();
function el(id) {
  if(!elements.has(id)) {
    const item=new Element(id.endsWith('-table')?'table':'div');
    item.id=id;
    if(id.endsWith('-table')) {
      item.tHead={rows:[new Element('tr')]};
      item.tBodies=[new Element('tbody')];
    }
    elements.set(id,item);
  }
  return elements.get(id);
}
const views=['weekly','stations','locations','trends'];
const tabs=views.map(view=>{
  const item=el('tab-'+view);item.setAttribute('data-view',view);
  return item;
});
const panels=views.map(view=>el('panel-'+view));
el('net-db').querySelectorAll=selector=>{
  if(selector==='[role="tab"]')return tabs;
  if(selector==='.panel')return panels;
  throw Error('Unexpected selector '+selector);
};
const document={getElementById:el,createElement:tag=>new Element(tag),activeElement:null};
function checkin(date,call,city,county,state,country) {
  return {date,number:1,callsign:call,name:call+' Operator',
    city,county,state,country,remarks:'RF'};
}
const checkins=[
  checkin('2023-10-03','KC2NJ','Roseland','Essex','NJ','United States'),
  checkin('2024-10-01','KC2NJ','Short Hills','Essex','NJ','United States'),
  checkin('2025-10-07','KC2NJ','Hallandale Beach','Broward','FL','United States'),
  checkin('2026-10-20','G4ABC','London','Greater London','England','United Kingdom'),
  checkin('2026-10-27','KC2NJ','Millburn','Essex','NJ','United States'),
  checkin('2026-10-27','G4ABC','London','Greater London','England','United Kingdom'),
  checkin('2026-10-27','KE2HPS','Roseland','Essex','NJ','United States')
];
checkins[0].name='Mike Abbey';
checkins[1].name='  Michael   Abbey  ';
checkins[2].name='Mike A. Abbey';
checkins[4].name='Mike Abbey';
const dates=[...new Set(checkins.map(row=>row.date))].sort();
const payload={kind:'netlogger-native-checkins',checkins,
  nets:dates.map(date=>({date,checkin_count:checkins.filter(row=>row.date===date).length,
    possibly_early_snapshot:true,source_time_et:'19:05'}))};
const fetch=()=>Promise.resolve({ok:true,json:()=>Promise.resolve(payload)});
vm.runInNewContext(prod,{document,fetch,console});

(async()=>{
  // Allow fetch/json promises and initial render to settle.
  await new Promise(resolve=>setImmediate(resolve));
  assert.ok(el('weekly-count').textContent.includes('displayed check-ins'));
  assert.doesNotMatch(el('weekly-count').textContent,/INCOMPLETE|19:05/);
  const weeklyCall=el('weekly-table').tBodies[0].children.find(row=>row.children[1].textContent==='KC2NJ');
  assert.ok(weeklyCall,'Latest weekly report should show KC2NJ');
  assert.equal(weeklyCall.children[2].textContent,'Mike Abbey',
    'Weekly reports must continue displaying the complete stored operator name');

  el('tab-stations').trigger('click');
  el('search-call').value='KC2NJ';
  el('search-call').trigger('input');
  assert.equal(el('station-detail').hidden,false);
  assert.equal(el('station-list').hidden,true);
  assert.equal(el('stations-history-table').tBodies[0].children.length,4);
  const history=el('stations-history-table').tBodies[0].children.map(
    row=>row.children[0].textContent);
  assert.deepEqual(history,['2026-10-27','2025-10-07','2024-10-01','2023-10-03']);
  const headers=el('stations-history-table').tHead.rows[0].children.map(th=>th.textContent);
  assert.deepEqual(headers.map(h=>h.replace(/ [↑↓]$/,'')),
    ['Net date','First name','City','County','State','Country','Remarks'],
    'Station history must exclude check-in order and label first names');
  const firstNames=el('stations-history-table').tBodies[0].children.map(row=>row.children[1].textContent);
  assert.deepEqual(firstNames,['Mike','Mike','Michael','Mike'],
    'Station history must show first names only, trimming whitespace');
  const engagement=el('station-engagement').children.map(row=>row.attrs['aria-label']);
  assert.equal(engagement.length,4);
  assert.ok(engagement.some(value=>value==='2026: 1 of 2 documented nets, 50 percent'));

  // A keyboard-activated net date must move focus out of the hidden history
  // panel and onto the selected weekly report's visible date control.
  const historyLink=el('stations-history-table').tBodies[0].children[1].children[0].children[0];
  historyLink.focus();
  assert.equal(document.activeElement,historyLink);
  historyLink.trigger('click');
  assert.equal(el('select-date').value,'2025-10-07');
  assert.equal(el('panel-weekly').hidden,false);
  assert.equal(el('panel-stations').hidden,true);
  assert.equal(document.activeElement,el('select-date'),
    'Opening a weekly report from station history must focus the visible date selector');

  el('tab-locations').trigger('click');
  el('location-country').value='United States';
  el('location-country').trigger('change');
  el('location-state').value='NJ';
  el('location-state').trigger('change');
  const counties=el('location-county').children.map(item=>item.value);
  assert.ok(counties.includes('Essex'));
  assert.ok(!counties.includes('Broward'), 'County choices must honor selected state');
  el('location-county').value='Essex';
  el('location-county').trigger('change');
  el('location-city').value='Millburn';
  el('location-city').trigger('change');
  const locationRows=el('locations-table').tBodies[0].children;
  assert.equal(locationRows.length,1);
  assert.equal(locationRows[0].children[0].textContent,'KC2NJ');
  assert.equal(locationRows[0].children[6].textContent,'1');
  // Callsign links similarly move focus into the newly visible station view.
  const locationLink=locationRows[0].children[0].children[0];
  locationLink.focus();
  locationLink.trigger('click');
  assert.equal(el('station-detail').hidden,false);
  assert.equal(el('panel-stations').hidden,false);
  assert.equal(el('panel-locations').hidden,true);
  assert.equal(document.activeElement,el('search-call'),
    'Opening station history from location results must focus its search field');
  assert.ok(el('station-history-title').textContent.includes('KC2NJ'));

  el('tab-locations').trigger('click');
  el('location-country').value='United Kingdom';
  el('location-country').trigger('change');
  assert.equal(el('location-state').value,'', 'Changing country clears invalid descendant filters');
  const ukRows=el('locations-table').tBodies[0].children;
  assert.equal(ukRows.length,1);
  assert.equal(ukRows[0].children[0].textContent,'G4ABC');
  console.log('Net Reports dashboard: first names, no order column, one-line headers, history, engagement, filters and focus tests passed');
})().catch(error=>{console.error(error);process.exitCode=1;});
