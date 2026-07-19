"use strict";

/* ---------- helpers ---------- */
const $ = (id) => document.getElementById(id);
const fmt = (n, d=2) => (n==null||isNaN(n)) ? "—" : "$"+Number(n).toLocaleString("en-US",{minimumFractionDigits:d,maximumFractionDigits:d});
const pct = (n) => (n==null||isNaN(n)) ? "—" : ((n>=0?"+":"")+Number(n).toFixed(2)+"%");
const cls = (n) => (n>=0?"up":"down");
const big = (n) => (n==null||isNaN(n)) ? "—" : Number(n).toLocaleString("en-US");
const GRADE_COLOR = {A:"gA",B:"gB",C:"gC",D:"gD",F:"gF"};

const LS_KEY = "investor.settings";
function loadSettings(){
  try{
    const s = JSON.parse(localStorage.getItem(LS_KEY) || "{}");
    if(s.region) $("set-region").value = s.region;
    if(typeof s.curated === "boolean") $("set-curated").checked = s.curated;
  }catch(e){ /* ignore */ }
}
function saveSettings(){
  try{
    localStorage.setItem(LS_KEY, JSON.stringify({
      region: $("set-region").value,
      curated: $("set-curated").checked,
    }));
  }catch(e){ /* ignore */ }
}

async function api(url, opts){
  const r = await fetch(url, opts);
  if(!r.ok){
    let e = "request failed";
    try { e = (await r.json()).detail || e; } catch(_){}
    throw new Error(e);
  }
  return r.json();
}
async function getj(url){ return api(url); }
async function postj(url, body){
  return api(url, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body||{})});
}
function toast(msg, kind){
  const t = $("toast");
  t.textContent = msg; t.className = "toast show " + (kind||"");
  clearTimeout(t._t); t._t = setTimeout(()=> t.className="toast", 2600);
}
function setNet(ok){
  $("net-dot").className = "net-dot " + (ok?"on":"off");
  $("net-label").textContent = ok ? "live market data" : "offline snapshot";
}
function kpi(lbl,val){return `<div class="kpi"><div class="lbl">${lbl}</div><div class="val">${val}</div></div>`;}

function sparklineSVG(closes, w=90, h=28){
  if(!closes || closes.length < 2) return "";
  const min = Math.min(...closes), max = Math.max(...closes), range = (max-min)||1;
  const x = i => (i/(closes.length-1))*(w-2)+1;
  const y = v => h-1 - ((v-min)/range)*(h-2);
  const pts = closes.map((v,i)=>`${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  const up = closes[closes.length-1] >= closes[0];
  const stroke = up ? "var(--up)" : "var(--down)";
  const gid = "sg" + Math.random().toString(36).slice(2,8);
  return `<svg class="spark" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
    <defs><linearGradient id="${gid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${stroke}" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="${stroke}" stop-opacity="0"/>
    </linearGradient></defs>
    <polygon points="1,${h-1} ${pts} ${w-1},${h-1}" fill="url(#${gid})"/>
    <polyline points="${pts}" fill="none" stroke="${stroke}" stroke-width="1.5"/>
  </svg>`;
}

/* ---------- nav ---------- */
document.querySelectorAll(".nav-item").forEach(n=>{
  n.addEventListener("click", ()=>{
    document.querySelectorAll(".nav-item").forEach(x=>x.classList.remove("active"));
    document.querySelectorAll(".view").forEach(x=>x.classList.remove("active"));
    n.classList.add("active");
    const v = $("view-"+n.dataset.view);
    v.classList.add("active");
    if(n.dataset.view==="home") loadTop();
    if(n.dataset.view==="trending") loadTrending();
    if(n.dataset.view==="traders") loadTraders();
    if(n.dataset.view==="alerts") loadAlerts();
  });
});

/* ---------- HOME: TOP 25 skyrocket list ---------- */
function homeParams(){
  const region = $("set-region").value;
  const curated = $("set-curated").checked;
  return `region=${encodeURIComponent(region)}&include_curated=${curated}`;
}

async function loadTrackRecord(){
  try{
    const d = await getj("/api/backtest?" + homeParams());
    if(!d || !d.universe_size){ return; }
    $("track-record").style.display = "block";
    $("tk-agree").textContent = (d.signal_agreement_pct!=null ? d.signal_agreement_pct+"%" : "—");
    $("tk-ret").textContent = (d.avg_return_1y_pct!=null ? pct(d.avg_return_1y_pct) : "—");
    $("tk-size").textContent = d.universe_size;
  }catch(e){ /* non-critical */ }
}

async function loadTop(){
  const el = $("top-list");
  el.innerHTML = '<div class="loading">Scoring the market…</div>';
  try{
    const data = await getj("/api/top-picks?limit=25&" + homeParams());
    const offline = data.some(p=>p.offline);
    setNet(!offline);
    if(offline){
      el.insertAdjacentHTML("beforebegin",
        `<div class="offline-banner">⚠ Live market data unavailable — showing curated offline snapshot. Scores are illustrative, not live.</div>`);
    }
    loadTrackRecord();
    if(!data.length){ el.innerHTML = '<div class="loading">No tickers scored. Check your connection.</div>'; return; }
    el.innerHTML = data.map((p,i)=>{
      const g = p.grade || "C";
      const top = i<3 ? "top3" : "";
      const off = p.offline ? '<span class="offline-chip">offline</span>' : '';
      return `<div class="rank-row ${top}" data-sym="${p.symbol}">
        <div class="rank">${i+1}</div>
        <div class="rk-sym">
          <div class="sym">${p.symbol} ${off}</div>
          <div class="rname">${p.name||""}</div>
        </div>
        <div class="rk-spark" data-sym="${p.symbol}"><span class="muted" style="font-size:.7rem">…</span></div>
        <div class="rk-score ${GRADE_COLOR[g]}">
          <div class="sc">${p.score}</div>
          <div class="gr">${g}</div>
        </div>
        <div class="rk-price">
          <div>${fmt(p.price)}</div>
          <div class="${cls(p.change_percent)}">${pct(p.change_percent)}</div>
        </div>
        <div class="rk-reasons">${(p.reasons||[]).slice(0,2).map(r=>`<span class="r">${r}</span>`).join("")}</div>
        <div class="rk-act"><span class="badge ${p.action}">${p.action}</span></div>
      </div>`;
    }).join("");
    el.querySelectorAll(".rank-row").forEach(r=>{
      r.addEventListener("click", ()=>{
        document.querySelector('.nav-item[data-view="research"]').click();
        $("sym-input").value = r.dataset.sym; loadStock(r.dataset.sym);
      });
    });
    // fill sparklines
    el.querySelectorAll(".rk-spark").forEach(async (cell)=>{
      const sym = cell.dataset.sym;
      try{
        const s = await getj("/api/spark/"+encodeURIComponent(sym));
        cell.innerHTML = sparklineSVG(s.closes);
      }catch(e){ cell.innerHTML = ""; }
    });
  }catch(err){
    setNet(false);
    if((loadTop._tries = (loadTop._tries||0) + 1) <= 15){
      setTimeout(loadTop, 1000 * Math.min(loadTop._tries, 5));
      el.innerHTML = '<div class="loading">Connecting to engine\u2026 ('+loadTop._tries+')</div>';
    } else {
      el.innerHTML = '<div class="loading down">'+err.message+'</div>';
    }
  }
}
$("refresh-top").addEventListener("click", loadTop);
$("set-region").addEventListener("change", ()=>{ saveSettings(); loadTop(); });
$("set-curated").addEventListener("change", ()=>{ saveSettings(); loadTop(); });

/* ---------- TRENDING ---------- */
async function loadTrending(){
  const el = $("trending-content");
  el.innerHTML = '<div class="loading">Loading…</div>';
  try{
    const data = await getj("/api/trending?limit=25");
    setNet(true);
    el.innerHTML = data.map(q=>`
      <div class="mini-card" data-sym="${q.symbol}">
        <div class="mc-top"><span class="sym">${q.symbol}</span>
        <span class="rank-badge">#${q.rank!=null?q.rank:"–"}</span></div>
        <div class="mc-name">${q.short_name||""}</div>
      </div>`).join("");
    el.querySelectorAll(".mini-card").forEach(c=>c.addEventListener("click",()=>{
      document.querySelector('.nav-item[data-view="research"]').click();
      $("sym-input").value=c.dataset.sym; loadStock(c.dataset.sym);
    }));
  }catch(err){ setNet(false); el.innerHTML='<div class="loading down">'+err.message+'</div>'; }
}
$("refresh-trending").addEventListener("click", loadTrending);

/* ---------- RESEARCH ---------- */
$("search-btn").addEventListener("click",()=>loadStock($("sym-input").value.trim()));
$("sym-input").addEventListener("keydown",e=>{ if(e.key==="Enter") loadStock($("sym-input").value.trim()); });

async function loadStock(sym){
  if(!sym) return;
  $("research-content").innerHTML = '<p class="muted">Loading '+sym+'…</p>';
  try{
    const d = await getj("/api/stock/"+encodeURIComponent(sym)+"?period=1y");
    renderStock(d);
  }catch(err){
    $("research-content").innerHTML = '<p class="down">'+err.message+'</p>';
  }
}
function renderStock(d){
  const q = d.quote || {};
  const up = (q.change||0) >= 0;
  const sig = d.signal || {};
  const v = d.valuation||{}, p = d.profile||{}, a = d.analyst||{}, r52 = d.range_52w||{};
  const logo = d.logo_url ? `<img class="logo" src="${d.logo_url}" onerror="this.style.display='none'" alt=""/>` : "";
  const reasons = (sig.reasons||[]).map(r=>`<li>${r}</li>`).join("");
  const offTag = d.offline ? '<span class="offline-chip" style="margin-left:8px">offline snapshot</span>' : '';

  $("research-content").innerHTML = `
  <div class="card">
    <div class="head">
      ${logo}
      <div><div class="name">${d.name}</div><div class="sym">${d.symbol} · ${d.currency}${offTag}</div></div>
      <div style="margin-left:auto;text-align:right">
        <div class="big-price ${up?'up':'down'}">${fmt(q.price)}</div>
        <div class="${up?'up':'down'}">${fmt(q.change)} (${pct(q.change_percent)})</div>
      </div>
    </div>
    <div class="signal ${sig.action}">
      <div class="action">${sig.action}</div>
      <div><div class="meta">Score ${sig.score} · confidence: <b>${sig.confidence||"—"}</b></div>
      <ul class="reasons">${reasons}</ul></div>
    </div>
  </div>
  <div class="card">
    <h3>Price Chart (1Y)</h3>
    <canvas id="chart"></canvas>
    <div class="rangebar"><div class="dot" style="left:${r52.position_pct||0}%"></div></div>
    <div class="muted" style="display:flex;justify-content:space-between;font-size:.8rem;margin-top:4px">
      <span>52w low: ${fmt(r52.low)}</span><span>52w high: ${fmt(r52.high)}</span></div>
  </div>
  <div class="card">
    <h3>Key Metrics</h3>
    <div class="row">
      ${kpi("Market Cap", big(v.market_cap))}
      ${kpi("P/E (trailing)", v.trailing_pe!=null?v.trailing_pe.toFixed(1):"—")}
      ${kpi("P/E (forward)", v.forward_pe!=null?v.forward_pe.toFixed(1):"—")}
      ${kpi("P/B", v.price_to_book!=null?v.price_to_book.toFixed(1):"—")}
      ${kpi("Div Yield", v.dividend_yield!=null?(v.dividend_yield*100).toFixed(2)+"%":"—")}
      ${kpi("Beta", v.beta!=null?v.beta.toFixed(2):"—")}
      ${kpi("Profit Margin", v.profit_margin!=null?(v.profit_margin*100).toFixed(1)+"%":"—")}
      ${kpi("Rev Growth", v.revenue_growth!=null?(v.revenue_growth*100).toFixed(1)+"%":"—")}
      ${kpi("EPS Growth", v.earnings_growth!=null?(v.earnings_growth*100).toFixed(1)+"%":"—")}
      ${kpi("RSI(14)", d.indicators?d.indicators.rsi:"—")}
      ${kpi("50d Avg", fmt(d.indicators?d.indicators.sma50:null))}
      ${kpi("200d Avg", fmt(d.indicators?d.indicators.sma200:null))}
    </div>
  </div>
  <div class="card">
    <h3>Company</h3>
    <div class="row">
      ${kpi("Sector", p.sector||"—")}${kpi("Industry", p.industry||"—")}
      ${kpi("Country", p.country||"—")}${kpi("Employees", p.employees?big(p.employees):"—")}
    </div>
    ${p.website?`<p style="margin-top:10px"><a href="${p.website}" target="_blank">${p.website}</a></p>`:""}
    ${p.summary?`<p class="muted" style="margin-top:8px">${p.summary}</p>`:""}
  </div>
  <div class="card">
    <h3>Wall Street</h3>
    <div class="row">
      ${kpi("Analyst Target", fmt(a.target_mean))}
      ${kpi("Rating", (a.recommendation_key||"—").toUpperCase())}
      ${kpi("Consensus (1-5)", a.recommendation_mean!=null?a.recommendation_mean.toFixed(1):"—")}
      ${kpi("Analysts", a.num_analysts||"—")}
    </div>
    ${a.target_mean?`<p class="muted" style="margin-top:10px">Implied: ${pct((a.target_mean-(q.price||0))/(q.price||1)*100)} vs current ${fmt(q.price)}</p>`:""}
  </div>`;
  drawChart(d.chart||[]);
}
function drawChart(chart){
  const c = $("chart"); if(!c || !chart.length) return;
  const dpr = window.devicePixelRatio||1, w=c.clientWidth, h=300;
  c.width=w*dpr; c.height=h*dpr;
  const ctx=c.getContext("2d"); ctx.scale(dpr,dpr); ctx.clearRect(0,0,w,h);
  const vals=chart.map(p=>p.close), min=Math.min(...vals), max=Math.max(...vals), range=(max-min)||1, pad=10;
  const x=i=>pad+(i/(vals.length-1))*(w-2*pad);
  const y=v=>h-pad-((v-min)/range)*(h-2*pad);
  ctx.strokeStyle="#222e42"; ctx.lineWidth=1;
  for(let g=0;g<=4;g++){const yy=pad+g*(h-2*pad)/4;ctx.beginPath();ctx.moveTo(pad,yy);ctx.lineTo(w-pad,yy);ctx.stroke();}
  const grad=ctx.createLinearGradient(0,pad,0,h-pad);
  grad.addColorStop(0,"rgba(91,157,255,.35)"); grad.addColorStop(1,"rgba(91,157,255,0)");
  ctx.beginPath(); ctx.moveTo(x(0),y(vals[0])); vals.forEach((v,i)=>ctx.lineTo(x(i),y(v)));
  ctx.lineTo(x(vals.length-1),h-pad); ctx.lineTo(x(0),h-pad); ctx.closePath();
  ctx.fillStyle=grad; ctx.fill();
  ctx.beginPath(); ctx.moveTo(x(0),y(vals[0])); vals.forEach((v,i)=>ctx.lineTo(x(i),y(v)));
  ctx.strokeStyle="#5b9dff"; ctx.lineWidth=2; ctx.stroke();
  ctx.fillStyle="#5b9dff"; ctx.beginPath(); ctx.arc(x(vals.length-1),y(vals[vals.length-1]),3,0,7); ctx.fill();
}

/* ---------- COPY TRADING ---------- */
async function loadTraders(filter){
  filter = filter || "All";
  const el = $("traders-content");
  el.innerHTML = '<div class="loading">Loading\u2026</div>';
  try{
    const list = await getj("/api/traders");
    const shown = filter==="All" ? list : list.filter(t=>(t.platform||"Investor")===filter);
    const platforms = ["All", ...Array.from(new Set(list.map(t=>t.platform||"Investor")))];
    const tabs = platforms.map(p=>`<span class="chip ${p===filter?'on':''}" data-pf="${p}">${p}</span>`).join("");
    el.innerHTML = `<div class="filter-row">${tabs}</div>` + shown.map(t=>`
      <div class="mini-card trader" data-id="${t.id}">
        <div class="mc-top"><span class="sym">${t.name}</span>
          <span class="pf-badge pf-${(t.platform||"Investor").toLowerCase()}">${t.platform||"Investor"}</span>
          ${t.followed?'<span class="badge BUY">following</span>':'<span class="follow-btn" data-id="'+t.id+'">+ Follow</span>'}</div>
        <div class="mc-name">${t.style}</div>
        <div class="muted" style="font-size:.8rem;margin-top:6px">${t.known_for||""}</div>
      </div>`).join("");
    el.querySelectorAll(".chip[data-pf]").forEach(c=>c.addEventListener("click",()=>loadTraders(c.dataset.pf)));
    el.querySelectorAll(".mini-card.trader").forEach(c=>c.addEventListener("click",(e)=>{
      if(e.target.classList.contains("follow-btn")) return;
      showTrader(c.dataset.id);
    }));
    el.querySelectorAll(".follow-btn").forEach(b=>b.addEventListener("click",async(e)=>{
      e.stopPropagation();
      await postj("/api/follow/"+b.dataset.id);
      toast("Now following "+b.dataset.id, "ok"); loadTraders(filter);
    }));
  }catch(err){ el.innerHTML='<div class="loading down">'+err.message+'</div>'; }
}
async function showTrader(id){
  const d = await getj("/api/traders/"+id);
  const t = d.profile;
  const ideas = d.ideas&&d.ideas.length ? d.ideas.map(i=>`
    <div class="idea"><span class="badge ${i.action.toUpperCase()}">${i.action}</span>
      <b>${i.symbol}</b> ${i.target?("→ "+fmt(i.target)):""} <span class="muted">${i.note||""}</span>
      <span class="muted" style="float:right">${i.date||""}</span></div>`).join("")
    : '<p class="muted">No ideas logged yet.</p>';
  $("trader-detail").innerHTML = `
    <div class="card">
      <div class="head"><div><div class="name">${t.name}</div>
      <div class="sym">${t.style}</div></div>
      <button class="btn" id="add-idea">+ Log idea</button></div>
      <p class="muted">${t.known_for||""}</p>
      <div class="muted" style="font-size:.85rem">${t.theme||""}</div>
      <div class="muted" style="font-size:.8rem;margin-top:6px">Source: ${t.source||""}</div>
      <h3 style="margin-top:14px">Tracked Ideas</h3>
      <div id="idea-list">${ideas}</div>
    </div>`;
  $("add-idea").addEventListener("click", async ()=>{
    const sym = prompt("Symbol?"); if(!sym) return;
    const action = confirm("Sell? OK = sell, Cancel = buy") ? "sell":"buy";
    const target = prompt("Target price (blank = none)?");
    await postj("/api/traders/"+id+"/ideas", {symbol:sym, action, target: target||null, note:""});
    toast("Idea logged", "ok"); showTrader(id);
  });
}

/* ---------- ALERTS ---------- */
async function loadAlerts(){
  const list = await getj("/api/alerts");
  const el = $("alerts-list");
  if(!list.length){ el.innerHTML='<p class="muted">No alerts yet.</p>'; }
  else el.innerHTML = list.map(a=>`
    <div class="alert-row">
      <span class="sym">${a.symbol}</span>
      <span class="muted">${a.condition} ${fmt(a.price)}</span>
      ${a.fired?'<span class="badge SELL">fired</span>':(a.active?'<span class="badge BUY">active</span>':'<span class="badge HOLD">off</span>')}
      <button class="x" data-id="${a.id}">✕</button>
    </div>`).join("");
  el.querySelectorAll(".x").forEach(b=>b.addEventListener("click",async()=>{
    await api("/api/alerts/"+b.dataset.id,{method:"DELETE"}); loadAlerts();
  }));
}
$("al-add").addEventListener("click", async ()=>{
  const symbol=$("al-symbol").value.trim(); const condition=$("al-cond").value;
  const price=parseFloat($("al-price").value);
  if(!symbol||isNaN(price)) return toast("Fill symbol + price","err");
  await postj("/api/alerts",{symbol,condition,price}); toast("Alert added","ok"); loadAlerts();
});
$("check-alerts").addEventListener("click", async ()=>{
  const r = await postj("/api/check-alerts");
  if(r.count>0) toast(r.count+" alert(s) fired!","ok"); else toast("No alerts triggered","");
  loadAlerts();
});

/* ---------- PORTFOLIO ---------- */
$("pf-btn").addEventListener("click", async ()=>{
  const posText=$("pf-positions").value.trim(), priceText=$("pf-prices").value.trim();
  const positions=[];
  for(const line of posText.split("\n")){
    const parts=line.split(",").map(s=>s.trim()); if(parts.length<3) continue;
    positions.push({symbol:parts[0],quantity:parseFloat(parts[1]),cost_basis:parseFloat(parts[2]),category:parts[3]||"Other"});
  }
  const prices={};
  for(const seg of priceText.split(",")){
    const [s,val]=seg.split("=").map(x=>x.trim()); if(s&&val) prices[s.toUpperCase()]=parseFloat(val);
  }
  try{
    const pv=await postj("/api/portfolio",{positions,prices});
    const alloc=(await postj("/api/allocation",{positions,prices})).map(a=>`<span class="chip">${a.category}: ${a.weight}%</span>`).join("");
    const rows=pv.positions.map(p=>`<tr><td class="sym">${p.symbol}</td><td>${p.quantity}</td><td>${fmt(p.avg_cost)}</td>
      <td>${fmt(p.price)}</td><td>${fmt(p.market_value)}</td><td class="${cls(p.gain)}">${fmt(p.gain)} (${pct(p.gain_percent)})</td></tr>`).join("");
    $("pf-result").innerHTML=`
      <div class="big-price ${cls(pv.total_gain)}">${fmt(pv.market_value)}</div>
      <p class="muted">Cost ${fmt(pv.cost_basis_total)} · Gain ${fmt(pv.total_gain)} (${pct(pv.total_gain_pct)})</p>
      <table style="margin-top:8px"><tr><th>Sym</th><th>Qty</th><th>Avg</th><th>Price</th><th>Value</th><th>Gain</th></tr>${rows}</table>
      <div style="margin-top:10px">${alloc}</div>`;
  }catch(err){ $("pf-result").innerHTML='<p class="down">'+err.message+'</p>'; }
});

/* ---------- boot ---------- */
loadSettings();
loadTop();
