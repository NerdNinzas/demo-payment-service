"""Customer-facing status page, served at / by the payment service itself.
No build step, no dependencies — one HTML string polling /health and /logs."""
import os

def deploy_ref() -> str:
    sha = os.environ.get("RENDER_GIT_COMMIT", "")
    return sha[:7] if sha else "local-dev"

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>PayFlow Status</title>
<style>
  :root { --ok:#16a34a; --warn:#d97706; --bad:#dc2626; --ink:#0f172a; --mut:#64748b; --line:#e2e8f0; }
  * { box-sizing:border-box; margin:0 }
  body { font-family:-apple-system,'Segoe UI',Roboto,sans-serif; background:#f8fafc; color:var(--ink); }
  .wrap { max-width:860px; margin:0 auto; padding:40px 24px }
  header { display:flex; align-items:center; gap:12px; margin-bottom:28px }
  .logo { width:38px; height:38px; border-radius:10px; background:var(--ink); color:#fff; display:grid; place-items:center; font-weight:800 }
  h1 { font-size:20px } .sub { color:var(--mut); font-size:13px }
  .chip { margin-left:auto; font-family:ui-monospace,monospace; font-size:12px; color:var(--mut); border:1px solid var(--line); border-radius:999px; padding:4px 12px; background:#fff }
  .hero { border-radius:14px; padding:26px 28px; color:#fff; display:flex; align-items:center; gap:14px; transition:background .5s }
  .hero.ok{background:var(--ok)} .hero.warn{background:var(--warn)} .hero.bad{background:var(--bad)}
  .dot { width:14px; height:14px; border-radius:50%; background:#fff; animation:pulse 1.5s infinite }
  @keyframes pulse { 50% { opacity:.4 } }
  .hero b { font-size:22px } .hero span { opacity:.9; font-size:14px }
  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:14px; margin:22px 0 }
  .card { background:#fff; border:1px solid var(--line); border-radius:12px; padding:16px 18px }
  .card .k { font-size:12px; color:var(--mut); text-transform:uppercase; letter-spacing:.06em }
  .card .v { font-size:30px; font-weight:700; margin-top:6px; font-variant-numeric:tabular-nums }
  .bar { height:6px; border-radius:4px; background:#f1f5f9; margin-top:10px; overflow:hidden }
  .bar i { display:block; height:100%; transition:width .5s, background .5s }
  canvas { width:100%; height:70px }
  h2 { font-size:14px; margin:26px 0 10px; color:var(--mut); text-transform:uppercase; letter-spacing:.08em }
  .logs { background:#0f172a; color:#fca5a5; border-radius:12px; padding:14px 16px; font-family:ui-monospace,monospace; font-size:12px; min-height:52px; max-height:180px; overflow-y:auto }
  .logs .ok { color:#86efac }
  button { background:var(--ink); color:#fff; border:0; border-radius:10px; padding:12px 22px; font-size:14px; font-weight:600; cursor:pointer }
  button:active { transform:scale(.98) }
  #payres { font-family:ui-monospace,monospace; font-size:13px; margin-left:12px }
  footer { margin-top:34px; color:var(--mut); font-size:12px; display:flex; justify-content:space-between }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="logo">P</div>
    <div><h1>PayFlow</h1><div class="sub">Payment infrastructure · system status</div></div>
    <div class="chip">deploy&nbsp;<b id="ref">__REF__</b></div>
  </header>

  <div id="hero" class="hero ok"><div class="dot"></div><div><b id="headline">All systems operational</b><br><span id="subline">Payments are processing normally.</span></div></div>

  <div class="grid">
    <div class="card"><div class="k">Payment success</div><div class="v" id="psr">—</div><div class="bar"><i id="psrbar"></i></div></div>
    <div class="card"><div class="k">DB pool utilization</div><div class="v" id="pool">—</div><div class="bar"><i id="poolbar"></i></div></div>
    <div class="card"><div class="k">Connections in use</div><div class="v" id="conns">—</div></div>
    <div class="card"><div class="k">Payments processed</div><div class="v" id="total">—</div></div>
  </div>

  <div class="card"><div class="k" style="margin-bottom:8px">Success rate — live</div><canvas id="chart" width="800" height="70"></canvas></div>

  <h2>Live checkout test</h2>
  <div><button onclick="tryPay()">Attempt a payment</button><span id="payres"></span></div>

  <h2>Service logs</h2>
  <div class="logs" id="logs"><span class="ok">no recent errors</span></div>

  <footer><span>PayFlow demo service · NerdNinzas</span><span>monitored by 🛡 Sentinel</span></footer>
</div>
<script>
const hist = [];
async function tick() {
  try {
    const h = await (await fetch('/health')).json();
    const psr = h.payment_success_rate ?? 100, pool = h.db_connection_utilization ?? 0;
    hist.push(psr); if (hist.length > 120) hist.shift();
    document.getElementById('psr').textContent = psr.toFixed(1) + '%';
    document.getElementById('pool').textContent = pool.toFixed(0) + '%';
    document.getElementById('conns').textContent = h.db_connections_in_use + ' / ' + h.pool_size;
    document.getElementById('total').textContent = h.payments_total;
    const psrbar = document.getElementById('psrbar'), poolbar = document.getElementById('poolbar');
    psrbar.style.width = psr + '%'; psrbar.style.background = psr < 50 ? 'var(--bad)' : psr < 95 ? 'var(--warn)' : 'var(--ok)';
    poolbar.style.width = pool + '%'; poolbar.style.background = pool >= 95 ? 'var(--bad)' : pool > 70 ? 'var(--warn)' : 'var(--ok)';
    const hero = document.getElementById('hero'), head = document.getElementById('headline'), sub = document.getElementById('subline');
    if (psr < 50) { hero.className = 'hero bad'; head.textContent = 'Major outage — payments failing'; sub.textContent = 'Our team is responding. Database connection pool exhausted.'; }
    else if (psr < 95 || pool > 80) { hero.className = 'hero warn'; head.textContent = 'Degraded performance'; sub.textContent = 'Elevated payment failures detected. Investigating.'; }
    else { hero.className = 'hero ok'; head.textContent = 'All systems operational'; sub.textContent = 'Payments are processing normally.'; }
    const lg = await (await fetch('/logs?limit=8')).json();
    const el = document.getElementById('logs');
    el.innerHTML = (lg.logs && lg.logs.length)
      ? lg.logs.map(l => `<div>[${new Date(l.ts*1000).toLocaleTimeString()}] ${l.level} ${l.msg}</div>`).join('')
      : '<span class="ok">no recent errors</span>';
    const c = document.getElementById('chart'), x = c.getContext('2d');
    x.clearRect(0,0,c.width,c.height);
    x.beginPath(); x.lineWidth = 2; x.strokeStyle = psr < 50 ? '#dc2626' : psr < 95 ? '#d97706' : '#16a34a';
    hist.forEach((v,i) => { const px = i/(Math.max(hist.length-1,1))*c.width, py = c.height-4-(v/100)*(c.height-8); i ? x.lineTo(px,py) : x.moveTo(px,py); });
    x.stroke();
  } catch (e) { document.getElementById('headline').textContent = 'Status unavailable'; }
}
async function tryPay() {
  const r = document.getElementById('payres'); r.textContent = '…';
  try {
    const res = await fetch('/pay', { method:'POST' });
    const d = await res.json();
    r.textContent = res.ok ? ('✓ ' + d.charge_id) : ('✗ ' + res.status + ' ' + (d.detail || 'failed'));
    r.style.color = res.ok ? '#16a34a' : '#dc2626';
  } catch { r.textContent = '✗ network error'; r.style.color = '#dc2626'; }
}
tick(); setInterval(tick, 2000);
</script>
</body>
</html>"""

def html() -> str:
    return PAGE.replace("__REF__", deploy_ref())
