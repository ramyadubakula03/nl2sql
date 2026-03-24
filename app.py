import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, render_template_string
from core.database import init_db, get_table_info
from core.engine import NL2SQLEngine

app = Flask(__name__)
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
engine = NL2SQLEngine(api_key=API_KEY if API_KEY else None)
init_db()

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>NL2SQL Engine</title>
<link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet"/>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#0d1117;--surface:#161b22;--surface2:#21262d;
  --border:#30363d;--text:#e6edf3;--muted:#7d8590;
  --accent:#58a6ff;--green:#3fb950;--orange:#d29922;--red:#f85149;
  --purple:#bc8cff;--font:'Fira Code',monospace;--sans:'DM Sans',sans-serif;
}
body{background:var(--bg);color:var(--text);font-family:var(--sans);min-height:100vh;}
.wrap{max-width:1100px;margin:0 auto;padding:2rem;}

header{margin-bottom:2rem;padding-bottom:1.5rem;border-bottom:1px solid var(--border);}
.logo{font-family:var(--font);font-size:1.5rem;font-weight:600;color:var(--accent);letter-spacing:-.5px;}
.logo span{color:var(--green);}
.tagline{color:var(--muted);font-size:.8rem;margin-top:.3rem;}

/* search bar */
.search-wrap{
  background:var(--surface);border:1px solid var(--border);border-radius:12px;
  padding:1.5rem;margin-bottom:1.5rem;
}
.search-label{font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-bottom:.75rem;}
.search-row{display:flex;gap:.75rem;align-items:flex-end;}
.search-input{
  flex:1;padding:.75rem 1rem;font-family:var(--sans);font-size:.95rem;
  background:var(--surface2);border:1px solid var(--border);border-radius:8px;
  color:var(--text);outline:none;transition:border-color .15s;
}
.search-input:focus{border-color:var(--accent);}
.search-input::placeholder{color:var(--muted);}
.search-btn{
  padding:.75rem 1.5rem;background:var(--accent);border:none;border-radius:8px;
  color:#000;font-family:var(--sans);font-size:.85rem;font-weight:700;
  cursor:pointer;white-space:nowrap;transition:opacity .15s;
}
.search-btn:hover{opacity:.85;}
.search-btn:disabled{opacity:.4;cursor:not-allowed;}

/* suggestions */
.suggestions{margin-top:1rem;}
.sugg-label{font-size:.7rem;color:var(--muted);margin-bottom:.5rem;text-transform:uppercase;letter-spacing:.08em;}
.sugg-chips{display:flex;flex-wrap:wrap;gap:.4rem;}
.chip{
  padding:.3rem .75rem;background:var(--surface2);border:1px solid var(--border);
  border-radius:20px;font-size:.75rem;cursor:pointer;color:var(--muted);transition:all .15s;
}
.chip:hover{border-color:var(--accent);color:var(--accent);}

/* results */
.result-card{
  background:var(--surface);border:1px solid var(--border);border-radius:12px;
  overflow:hidden;margin-bottom:1.5rem;
}
.result-header{padding:1rem 1.25rem;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:.75rem;}
.result-q{font-size:.9rem;font-weight:500;flex:1;}
.badge{display:inline-block;padding:.2rem .6rem;border-radius:4px;font-size:.65rem;font-weight:600;
  letter-spacing:.06em;text-transform:uppercase;}
.badge-ai{background:#1c2d4e;color:var(--accent);}
.badge-rule{background:#1c2e1c;color:var(--green);}
.badge-error{background:#2d1c1c;color:var(--red);}
.count-badge{background:var(--surface2);color:var(--muted);padding:.2rem .5rem;border-radius:4px;font-size:.7rem;font-family:var(--font);}

/* sql block */
.sql-block{
  background:#0d1117;padding:1rem 1.25rem;font-family:var(--font);font-size:.78rem;
  color:#e6edf3;border-bottom:1px solid var(--border);line-height:1.6;overflow-x:auto;
  white-space:pre;
}
.kw{color:#ff7b72;}
.fn{color:#d2a8ff;}
.str{color:#a5d6ff;}
.num{color:#79c0ff;}

/* table */
.table-wrap{overflow-x:auto;max-height:340px;overflow-y:auto;}
table{width:100%;border-collapse:collapse;font-size:.78rem;}
thead th{
  padding:.6rem 1rem;text-align:left;font-family:var(--font);font-size:.7rem;
  color:var(--muted);text-transform:uppercase;letter-spacing:.08em;
  background:var(--surface2);position:sticky;top:0;border-bottom:1px solid var(--border);
}
tbody tr:hover{background:var(--surface2);}
tbody td{padding:.55rem 1rem;border-bottom:1px solid var(--border);color:var(--text);}
.td-num{color:var(--accent);font-family:var(--font);}

/* schema panel */
.schema-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;margin-bottom:1.5rem;}
.schema-card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:1rem;}
.schema-title{font-family:var(--font);font-size:.8rem;color:var(--purple);font-weight:600;margin-bottom:.5rem;}
.col-row{display:flex;gap:.5rem;padding:.25rem 0;border-bottom:1px solid var(--border);font-size:.72rem;}
.col-name{color:var(--text);flex:1;}
.col-type{color:var(--orange);font-family:var(--font);font-size:.65rem;}

.empty-state{text-align:center;padding:3rem;color:var(--muted);font-size:.85rem;line-height:2;}
.spinner{display:inline-block;width:14px;height:14px;border:2px solid var(--border);
  border-top-color:var(--accent);border-radius:50%;animation:spin .7s linear infinite;vertical-align:middle;}
@keyframes spin{to{transform:rotate(360deg)}}

.error-msg{background:#2d1c1c;border:1px solid #5c1a1a;border-radius:6px;
  padding:.75rem 1rem;color:var(--red);font-size:.78rem;font-family:var(--font);}

.tabs{display:flex;gap:0;border-bottom:1px solid var(--border);margin-bottom:1.5rem;}
.tab{padding:.5rem 1.25rem;font-size:.8rem;cursor:pointer;border:none;background:none;
  color:var(--muted);border-bottom:2px solid transparent;margin-bottom:-1px;transition:color .15s;}
.tab.active{color:var(--text);border-bottom-color:var(--accent);}
.tab-panel{display:none;}.tab-panel.active{display:block;}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="logo">nl<span>2</span>sql<span style="color:var(--muted)">.</span>engine</div>
    <div class="tagline">Ask questions in plain English · Get SQL + results instantly · </div>
  </header>

  <div class="search-wrap">
    <div class="search-label">Ask a question about your data</div>
    <div class="search-row">
      <input class="search-input" id="question" type="text"
        placeholder="e.g. What is the average salary by department?"
        onkeydown="if(event.key==='Enter') runQuery()"/>
      <button class="search-btn" id="run-btn" onclick="runQuery()">Run Query →</button>
    </div>
    <div class="suggestions">
      <div class="sugg-label">Try these</div>
      <div class="sugg-chips">
        <span class="chip" onclick="ask(this)">Average salary by department</span>
        <span class="chip" onclick="ask(this)">Top 5 highest paid employees</span>
        <span class="chip" onclick="ask(this)">Total revenue by product</span>
        <span class="chip" onclick="ask(this)">How many employees per department</span>
        <span class="chip" onclick="ask(this)">Show all pending orders</span>
        <span class="chip" onclick="ask(this)">Products with low stock</span>
        <span class="chip" onclick="ask(this)">Department budgets</span>
        <span class="chip" onclick="ask(this)">Recently hired employees</span>
        <span class="chip" onclick="ask(this)">Total sales by region</span>
        <span class="chip" onclick="ask(this)">Most expensive products</span>
      </div>
    </div>
  </div>

  <div class="tabs">
    <button class="tab active" onclick="showTab('results', this)">Results</button>
    <button class="tab" onclick="showTab('schema', this); loadSchema()">Schema</button>
    <button class="tab" onclick="showTab('history', this)">History</button>
  </div>

  <div class="tab-panel active" id="tab-results">
    <div id="results-area">
      <div class="empty-state">
        Ask a question above to see results here.<br/>
        <span style="font-size:.75rem">No SQL knowledge needed — just plain English.</span>
      </div>
    </div>
  </div>

  <div class="tab-panel" id="tab-schema">
    <div id="schema-area"><div class="empty-state">Loading schema...</div></div>
  </div>

  <div class="tab-panel" id="tab-history">
    <div id="history-area"><div class="empty-state">No queries yet.</div></div>
  </div>
</div>

<script>
let history = [];

function showTab(name, el) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  el.classList.add('active');
}

function ask(el) {
  document.getElementById('question').value = el.textContent;
  runQuery();
}

function highlightSQL(sql) {
  const keywords = ['SELECT','FROM','WHERE','GROUP BY','ORDER BY','HAVING','JOIN','LEFT','INNER',
    'ON','AS','AND','OR','NOT','IN','LIKE','BETWEEN','LIMIT','DISTINCT','COUNT','SUM','AVG',
    'MAX','MIN','ROUND','BY','DESC','ASC','INSERT','UPDATE','DELETE','CREATE','TABLE'];
  let s = sql.replace(/</g,'&lt;').replace(/>/g,'&gt;');
  keywords.forEach(kw => {
    s = s.replace(new RegExp('\\b'+kw+'\\b','g'), `<span class="kw">${kw}</span>`);
  });
  s = s.replace(/'([^']*)'/g, `<span class="str">'$1'</span>`);
  s = s.replace(/\b(\d+\.?\d*)\b/g, `<span class="num">$1</span>`);
  return s;
}

async function runQuery() {
  const q = document.getElementById('question').value.trim();
  if (!q) return;
  const btn = document.getElementById('run-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Running...';

  const area = document.getElementById('results-area');
  area.innerHTML = '<div style="padding:2rem;text-align:center;color:var(--muted)"><span class="spinner"></span> Generating SQL...</div>';

  try {
    const r = await fetch('/api/query', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({question: q})
    });
    const d = await r.json();
    history.unshift(d);
    renderResult(d, area);
    renderHistory();
  } catch(e) {
    area.innerHTML = `<div class="error-msg">Request failed: ${e.message}</div>`;
  }

  btn.disabled = false;
  btn.innerHTML = 'Run Query →';
}

function renderResult(d, container) {
  const badgeClass = d.error ? 'badge-error' : (d.source === 'claude' ? 'badge-ai' : 'badge-rule');
  const badgeLabel = d.error ? 'error' : (d.source === 'claude' ? 'AI generated' : 'rule-based');

  let tableHTML = '';
  if (d.error) {
    tableHTML = `<div class="error-msg" style="margin:1rem">${d.error}</div>`;
  } else if (d.rows.length === 0) {
    tableHTML = `<div class="empty-state" style="padding:1.5rem">No results returned</div>`;
  } else {
    tableHTML = `<div class="table-wrap"><table>
      <thead><tr>${d.columns.map(c => `<th>${c}</th>`).join('')}</tr></thead>
      <tbody>${d.rows.map(row =>
        `<tr>${d.columns.map(c => {
          const v = row[c];
          const isNum = typeof v === 'number';
          return `<td class="${isNum ? 'td-num' : ''}">${v ?? '—'}</td>`;
        }).join('')}</tr>`
      ).join('')}</tbody>
    </table></div>`;
  }

  container.innerHTML = `
    <div class="result-card">
      <div class="result-header">
        <div class="result-q">${d.question}</div>
        <span class="badge ${badgeClass}">${badgeLabel}</span>
        ${!d.error ? `<span class="count-badge">${d.count} rows</span>` : ''}
      </div>
      <div class="sql-block">${highlightSQL(d.sql)}</div>
      ${tableHTML}
    </div>`;
}

function renderHistory() {
  const el = document.getElementById('history-area');
  if (!history.length) { el.innerHTML = '<div class="empty-state">No queries yet.</div>'; return; }
  el.innerHTML = history.map((d, i) => `
    <div style="display:flex;align-items:center;gap:.75rem;padding:.75rem;border-bottom:1px solid var(--border);cursor:pointer;font-size:.82rem;"
      onclick="showHistoryResult(${i})">
      <span style="color:var(--accent);font-family:var(--font);font-size:.7rem;">#${history.length - i}</span>
      <span style="flex:1;">${d.question}</span>
      <span class="count-badge">${d.count} rows</span>
    </div>`).join('');
}

function showHistoryResult(i) {
  showTab('results', document.querySelector('.tab'));
  document.querySelectorAll('.tab')[0].classList.add('active');
  document.getElementById('tab-results').classList.add('active');
  renderResult(history[i], document.getElementById('results-area'));
}

async function loadSchema() {
  const r = await fetch('/api/schema');
  const schema = await r.json();
  const el = document.getElementById('schema-area');
  el.innerHTML = `<div class="schema-grid">${Object.entries(schema).map(([table, cols]) => `
    <div class="schema-card">
      <div class="schema-title">${table}</div>
      ${cols.map(c => `<div class="col-row"><span class="col-name">${c.name}</span><span class="col-type">${c.type}</span></div>`).join('')}
    </div>`).join('')}</div>`;
}
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/query", methods=["POST"])
def query():
    data = request.json
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400
    result = engine.run(question)
    return jsonify(result)

@app.route("/api/schema")
def schema():
    return jsonify(get_table_info())

@app.route("/api/history")
def history():
    return jsonify(engine.query_history[-20:])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    print(f"\n🚀 NL2SQL Engine running at http://localhost:{port}")
    print(f"   API Key: {'✅ Set (Claude AI)' if API_KEY else '⚠️  Not set (rule-based fallback)'}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
