---
layout: page
title: Net Reports
cover-img: /assets/img/FT-736R.jpg
subtitle: Weekly Net Reports
---


<p class="box-note">
Since August 30, 2023, the Community Amateur Radio Social Net has brought amateur radio operators together every Tuesday at 7:00 PM Eastern. The net is an informal, welcoming gathering where conversations range from everyday topics like weather, food, and gardening to amateur radio and technology. Whether you're a longtime operator or newly licensed, everyone is welcome to check in, join the conversation, and connect with fellow hams throughout Essex County, New Jersey, and beyond.
</p>

### How to Join

The net meets every Tuesday at 7:00 PM Eastern and can be accessed through either of two linked repeaters or via EchoLink.

- **Livingston – KC2TXA (SBARC):** [146.595 MHz (+1.0 MHz offset), 100.0 Hz PL](https://www.repeaterbook.com/repeaters/details.php?state_id=34&ID=2845)
- **Newark – K2MFF (NJIT):** [147.225 MHz (+0.6 MHz offset), 141.3 Hz PL](https://www.repeaterbook.com/repeaters/details.php?state_id=34&ID=2847)
- **EchoLink:** KC2TXA-R

<style>
#net-db { --ink:#203149; --muted:#536276; --line:#dbe4ec; --accent:#155e86; --soft:#eef5fa; color:var(--ink); }
#net-db * { box-sizing:border-box; }
#net-db .metrics { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.75rem; margin:1.3rem 0; }
#net-db .metric { border:1px solid var(--line); background:#f2f7fb; border-radius:.65rem; padding:1rem; }
#net-db .metric strong { display:block; font-size:1.6rem; letter-spacing:-.03em; }
#net-db .metric span { font-size:.86rem; color:var(--muted); }
#net-db .tabs { display:flex; flex-wrap:wrap; gap:.5rem; margin:1.25rem 0 .8rem; border-bottom:1px solid var(--line); padding-bottom:.65rem; }
#net-db button, #net-db select, #net-db input { font:inherit; }
#net-db .tab { border:1px solid #bdcbd9; border-radius:.45rem; background:#fff; color:var(--ink); padding:.5rem .8rem; cursor:pointer; }
#net-db .tab[aria-selected="true"] { background:var(--accent); color:#fff; border-color:var(--accent); }
#net-db [hidden] { display:none !important; }
#net-db .controls { display:flex; gap:1rem; align-items:end; flex-wrap:wrap; margin:.9rem 0; }
#net-db label { display:flex; flex-direction:column; gap:.3rem; font-weight:600; font-size:.92rem; }
#net-db input, #net-db select { min-height:2.5rem; border:1px solid #9caec0; border-radius:.4rem; background:#fff; color:var(--ink); padding:.4rem .6rem; max-width:100%; }
#net-db input[type=search] { width:min(100%,19rem); }
#net-db .muted { color:var(--muted); font-size:.9rem; }
#net-db .tablewrap { width:100%; overflow-x:auto; border:1px solid var(--line); border-radius:.55rem; margin:1rem 0; }
#net-db table { border-collapse:collapse; width:100%; background:#fff; font-size:.86rem; margin:0; }
#net-db th, #net-db td { text-align:left; vertical-align:top; border-bottom:1px solid var(--line); padding:.55rem .45rem; overflow-wrap:anywhere; }
#net-db th { background:#ecf3f8; }
#net-db th button { border:0; padding:0; background:transparent; font-weight:700; color:inherit; cursor:pointer; text-align:left; }
#net-db tbody tr:nth-child(even) { background:#f9fbfd; }
#net-db a { color:#11658c; }
#net-db .call { font-weight:600; text-decoration:underline; text-decoration-thickness:1px; text-underline-offset:.1em; }
#net-db .chart { display:flex; gap:.35rem; align-items:end; overflow-x:hidden; min-height:220px; padding:1rem .5rem; border:1px solid var(--line); border-radius:.55rem; }
#net-db .barbox { flex:1 1 0; min-width:0; text-align:center; font-size:.74rem; }
#net-db .bar { background:#2479a5; border-radius:.22rem .22rem 0 0; width:60%; max-width:68px; min-height:2px; margin:auto; }
#net-db .barbox strong { display:block; margin-bottom:.45rem; }
#net-db .barbox span { display:block; margin-top:.3rem; }
@media(min-width:761px) {
  #net-db .tablewrap { overflow-x:visible; }
  #net-db table { table-layout:fixed; font-size:clamp(.73rem,.78vw,.87rem); }
  #net-db th, #net-db td { white-space:normal; padding:.5rem .28rem; }
  #net-db #weekly-table th:nth-child(1) { width:4%; }
  #net-db #weekly-table th:nth-child(2) { width:11%; }
  #net-db #weekly-table th:nth-child(3) { width:21%; }
  #net-db #weekly-table th:nth-child(4) { width:17%; }
  #net-db #weekly-table th:nth-child(5) { width:12%; }
  #net-db #weekly-table th:nth-child(6) { width:6%; }
  #net-db #weekly-table th:nth-child(7) { width:14%; }
  #net-db #weekly-table th:nth-child(8) { width:15%; }
}
@media(max-width:760px) {
  #net-db #weekly-table { min-width:760px; }
  #net-db .chart { overflow-x:auto; }
  #net-db .barbox { flex:1 0 60px; }
}
@media(max-width:650px) {
  #net-db .metrics { grid-template-columns:repeat(2,minmax(0,1fr)); }
  #net-db .metric strong { font-size:1.35rem; }
  #net-db .controls { display:block; }
  #net-db .controls label { margin-bottom:.8rem; }
  #net-db input[type=search], #net-db select { width:100%; }
}
</style>

<div id="net-db">
  <p id="load-message" class="muted" role="status">Loading check-ins…</p>
  <div class="metrics" aria-label="Imported source data summary">
    <div class="metric"><strong id="total-nets">—</strong><span>Documented nets</span></div>
    <div class="metric"><strong id="total-rows">—</strong><span>Recorded check-ins</span></div>
    <div class="metric"><strong id="total-calls">—</strong><span>Distinct callsigns</span></div>
  </div>
  <div class="tabs" role="tablist" aria-label="Net report views">
    <button class="tab" role="tab" id="tab-weekly" aria-controls="panel-weekly" aria-selected="true" data-view="weekly">Weekly reports</button>
    <button class="tab" role="tab" id="tab-stations" aria-controls="panel-stations" aria-selected="false" data-view="stations">Station history</button>
    <button class="tab" role="tab" id="tab-trends" aria-controls="panel-trends" aria-selected="false" data-view="trends">Participation trends</button>
  </div>
  <section id="panel-weekly" class="panel" role="tabpanel" aria-labelledby="tab-weekly">
    <div class="controls">
      <label>Choose net date <select id="select-date"></select></label>
      <label>Search this net <input type="search" id="search-weekly" placeholder="Callsign, name or location" autocomplete="off"></label>
    </div>
    <p id="weekly-count" class="muted" aria-live="polite"></p>
    <div class="tablewrap"><table id="weekly-table"><thead><tr></tr></thead><tbody></tbody></table></div>
    <p class="muted">Select a callsign to see its check-in history.</p>
  </section>
  <section id="panel-stations" class="panel" role="tabpanel" aria-labelledby="tab-stations" hidden>
    <div class="controls"><label>Find a callsign <input type="search" id="search-call" list="all-calls" placeholder="Type a callsign" autocomplete="off"><datalist id="all-calls"></datalist></label></div>
    <p id="station-summary" class="muted"></p>
    <div class="tablewrap"><table id="stations-table"><thead><tr></tr></thead><tbody></tbody></table></div>
  </section>
  <section id="panel-trends" class="panel" role="tabpanel" aria-labelledby="tab-trends" hidden>
    <p class="muted">Compare participation across years without penalizing years with fewer available reports.</p>
    <div class="controls">
      <label>Trend view
        <select id="trend-view">
          <option value="annual">Annual average check-ins per net</option>
          <option value="monthly">Monthly check-ins</option>
        </select>
      </label>
      <label id="trend-year-control" hidden>View year <select id="trend-year"></select></label>
    </div>
    <div class="chart" id="trend-chart" role="img" aria-label="Average check-ins per documented net by year"></div>
    <p id="trend-note" class="muted"></p>
    <h3>Annual summary (documented nets)</h3>
    <div class="tablewrap"><table id="year-table"><thead><tr></tr></thead><tbody></tbody></table></div>
  </section>
</div>

<script>
(function () {
  'use strict';
  var root=document.getElementById('net-db'), data=null,selectedDate='',weeklySearch='',weeklySort={key:'number',asc:true},stationSort={key:'total',asc:false};
  var columns=[['number','#'],['callsign','Call sign'],['name','Name'],['city','City'],['county','County'],['state','State'],['country','Country'],['remarks','Remarks']];
  var stationColumns=[['callsign','Call sign'],['total','Nets'],['first','First seen'],['last','Last seen']];
  function el(id){return document.getElementById(id);}
  function text(id,value){el(id).textContent=String(value);}
  function node(tag,value){var n=document.createElement(tag);if(value!==undefined)n.textContent=String(value);return n;}
  function clear(element){while(element.firstChild)element.removeChild(element.firstChild);}
  function sorted(rows,spec){return rows.slice().sort(function(a,b){
    var x=a[spec.key],y=b[spec.key];if(x==null)x='';if(y==null)y='';
    var d=typeof x==='number'&&typeof y==='number'?x-y:String(x).localeCompare(String(y),undefined,{sensitivity:'base',numeric:true});
    return spec.asc?d:-d;
  });}
  function table(id,fields,rows,sort,onSort,onCall){
    var t=el(id),thead=t.tHead.rows[0],tbody=t.tBodies[0];clear(thead);clear(tbody);
    fields.forEach(function(col){
      var th=node('th');th.scope='col';
      var b=node('button',col[1]+(sort&&sort.key===col[0]?(sort.asc?' ↑':' ↓'):''));
      b.type='button';b.addEventListener('click',function(){onSort(col[0]);});th.appendChild(b);thead.appendChild(th);
    });
    if(!rows.length){var empty=node('tr'),td=node('td','No matching records.');td.colSpan=fields.length;empty.appendChild(td);tbody.appendChild(empty);return;}
    rows.forEach(function(row){var tr=node('tr');
      fields.forEach(function(field){
        var cell=node('td',row[field[0]]==null?'':row[field[0]]);
        if(field[0]==='callsign'&&onCall){
          clear(cell);var link=node('a',row.callsign);link.href='#panel-stations';link.className='call';
          link.addEventListener('click',function(e){e.preventDefault();onCall(row.callsign);});cell.appendChild(link);
        }
        tr.appendChild(cell);
      });
      tbody.appendChild(tr);
    });
  }
  function dates(){return data.nets.slice().sort(function(a,b){return b.date.localeCompare(a.date);});}
  function weeklyRows(){return data.checkins.filter(function(row){
    return row.date===selectedDate&&(!weeklySearch||columns.some(function(col){
      return String(row[col[0]]==null?'':row[col[0]]).toUpperCase().includes(weeklySearch);
    }));
  });}
  function renderWeekly(){
    var net=data.nets.find(function(n){return n.date===selectedDate;});
    var rows=sorted(weeklyRows(),weeklySort);
    text('weekly-count',rows.length+' displayed check-ins'+
      (net?' · '+net.checkin_count+(net.manual?' in approved manual reconstruction':' in original NetLogger roster')+
      (net.possibly_early_snapshot?' · POSSIBLY INCOMPLETE (saved '+net.source_time_et+' ET)':''):''));
    table('weekly-table',columns,rows,weeklySort,function(k){weeklySort={key:k,asc:weeklySort.key===k?!weeklySort.asc:true};renderWeekly();},openCall);
  }
  function totals(){
    var byCall=new Map();
    data.checkins.forEach(function(row){if(!row.callsign)return;
      var call=row.callsign.toUpperCase();
      if(!byCall.has(call))byCall.set(call,new Set());
      byCall.get(call).add(row.date);
    });
    return Array.from(byCall).map(function(entry){
      var ds=Array.from(entry[1]).sort();
      return {callsign:entry[0],total:ds.length,first:ds[0],last:ds[ds.length-1]};
    });
  }
  function openCall(call){el('search-call').value=call;activate('stations');}
  function renderStations(){
    var query=el('search-call').value.trim().toUpperCase();
    var records=sorted(totals().filter(function(r){return !query||r.callsign.includes(query);}),stationSort);
    text('station-summary',records.length+' matching callsigns.');
    table('stations-table',stationColumns,records,stationSort,function(k){stationSort={key:k,asc:stationSort.key===k?!stationSort.asc:true};renderStations();},openCall);
  }
  function renderTrends(){
    var years=Array.from(new Set(data.nets.map(function(n){return n.date.slice(0,4);}))).sort();
    var picker=el('trend-year'),chosen=picker.value;
    if(!years.includes(chosen))chosen=years[years.length-1];
    clear(picker);
    years.slice().reverse().forEach(function(y){var opt=node('option',y);opt.value=y;picker.appendChild(opt);});
    picker.value=chosen;
    var monthly=el('trend-view').value==='monthly';
    el('trend-year-control').hidden=!monthly;
    el('trend-note').hidden=!monthly;
    var months={},groups={};
    data.nets.forEach(function(net){
      var year=net.date.slice(0,4),m=net.date.slice(5,7);
      if(!groups[year])groups[year]={year:year,nets:0,checkins:0};
      groups[year].nets++;
      groups[year].checkins+=net.checkin_count;
      if(year===chosen){
        if(!months[m])months[m]={checkins:0,nets:0};
        months[m].checkins+=net.checkin_count;
        months[m].nets++;
      }
    });
    var annual=Object.values(groups).sort(function(a,b){return a.year.localeCompare(b.year);});
    annual.forEach(function(r){r.average=(r.checkins/r.nets).toFixed(1);});
    var series,chart=el('trend-chart');
    if(monthly){
      var labels=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      series=Object.keys(months).sort().map(function(m){
        var item=months[m];
        return {label:labels[Number(m)-1],value:item.checkins,display:String(item.checkins),
          detail:chosen+'-'+m+': '+item.checkins+' check-ins in '+item.nets+' documented nets'};
      });
      chart.setAttribute('aria-label','Monthly check-in totals for '+chosen+' (documented nets only)');
      text('trend-note','Monthly totals include only documented nets for '+chosen+'.');
    }else{
      series=annual.map(function(r){
        return {label:r.year,value:r.checkins/r.nets,display:r.average,
          detail:r.year+': '+r.average+' average check-ins per net ('+r.checkins+
            ' check-ins across '+r.nets+' documented nets)'};
      });
      chart.setAttribute('aria-label','Average check-ins per documented net for each year');
    }
    var max=Math.max(1,...series.map(function(r){return r.value;}));
    clear(chart);
    series.forEach(function(item){
      var box=node('div');box.className='barbox';
      box.appendChild(node('strong',item.display));
      var bar=node('div');bar.className='bar';
      bar.style.height=Math.max(2,140*item.value/max)+'px';
      bar.title=item.detail;
      box.appendChild(bar);
      box.appendChild(node('span',item.label));
      chart.appendChild(box);
    });
    table('year-table',[['year','Year'],['nets','Documented nets'],['checkins','Check-ins'],['average','Average per net']],annual,{key:'year',asc:true},function(){});
  }
  function activate(which){
    root.querySelectorAll('[role="tab"]').forEach(function(t){t.setAttribute('aria-selected',t.getAttribute('data-view')===which?'true':'false');});
    root.querySelectorAll('.panel').forEach(function(p){p.hidden=p.id!=='panel-'+which;});
    if(which==='weekly')renderWeekly();
    if(which==='stations')renderStations();
    if(which==='trends')renderTrends();
  }
  function init(payload){
    if(!payload||payload.kind!=='netlogger-native-checkins'||!Array.isArray(payload.nets)||!Array.isArray(payload.checkins))throw Error('Invalid native check-in data');
    data=payload;var nets=dates();if(!nets.length)throw Error('No native log files have been imported yet');
    selectedDate=nets[0].date;
    var selector=el('select-date');nets.forEach(function(n){
      var opt=node('option',n.date+' ('+n.checkin_count+' check-ins)');opt.value=n.date;selector.appendChild(opt);
    });
    var unique=Array.from(new Set(data.checkins.map(function(r){return r.callsign;}).filter(Boolean))).sort();
    var datalist=el('all-calls');unique.forEach(function(call){var o=node('option');o.value=call;datalist.appendChild(o);});
    text('total-nets',nets.length);text('total-rows',data.checkins.length);text('total-calls',unique.length);
    var counts=data.source_counts||{};
    el('load-message').hidden=true;
    selector.addEventListener('change',function(){selectedDate=this.value;renderWeekly();});
    el('search-weekly').addEventListener('input',function(){weeklySearch=this.value.trim().toUpperCase();renderWeekly();});
    el('search-call').addEventListener('input',renderStations);
    el('trend-year').addEventListener('change',renderTrends);
    el('trend-view').addEventListener('change',renderTrends);
    root.querySelectorAll('[role="tab"]').forEach(function(b){b.addEventListener('click',function(){activate(b.getAttribute('data-view'));});});
    activate('weekly');
  }
  fetch("{{ '/netreports-dev/data/netlogger.json' | relative_url }}",{cache:'no-store'})
    .then(function(r){if(!r.ok)throw Error('HTTP '+r.status);return r.json();})
    .then(init)
    .catch(function(e){text('load-message','Check-in data is unavailable: '+e.message);
      text('total-nets',0);text('total-rows',0);text('total-calls',0);});
})();
</script>
