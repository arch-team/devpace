"""Interactive eval viewer server.

Zero-dependency HTTP server (Python stdlib only) for browsing eval results,
providing assertion-level feedback, and comparing iterations.

Usage:
    start_viewer(workspace_dir=Path("tests/evaluation/pace-dev/results"))
"""
from __future__ import annotations

import http.server
import json
import textwrap
import threading
import webbrowser
from pathlib import Path

from eval.core import EVAL_DATA_DIR
from . import feedback as fb


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict | list | None:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return None


def _load_workspace(workspace_dir: Path) -> dict:
    """Load all result data from a workspace directory."""
    data: dict = {}
    # Trigger results
    latest = workspace_dir / "latest.json"
    if latest.exists():
        data["trigger"] = _load_json(latest)
    # Behavior grading
    grading = workspace_dir / "grading" / "latest.json"
    if grading.exists():
        data["behavior"] = _load_json(grading)
    # Benchmark
    bench = workspace_dir / "benchmark" / "latest.json"
    if bench.exists():
        data["benchmark"] = _load_json(bench)
    # History
    history_dir = workspace_dir / "history"
    if history_dir.is_dir():
        history_files = sorted(history_dir.glob("*.json"), reverse=True)[:10]
        data["history"] = [
            {"file": f.name, "data": _load_json(f)} for f in history_files
        ]
    return data


def _load_notes() -> list[dict]:
    """Load notes from notes.jsonl."""
    notes = fb._read_all_notes()
    return [n.to_dict() for n in notes]


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def _esc(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


_VIEWER_CSS = """\
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       background: #f5f5f5; color: #333; line-height: 1.5; }
header { background: #1a1a2e; color: #fff; padding: 12px 24px;
         display: flex; align-items: center; justify-content: space-between; }
header h1 { font-size: 1.15rem; font-weight: 600; }
header .info { font-size: 0.85rem; opacity: 0.8; display: flex; gap: 16px; }
.container { max-width: 1300px; margin: 0 auto; padding: 16px; }

/* Tabs */
.tabs { display: flex; background: #fff; border-bottom: 2px solid #e0e0e0; padding: 0 16px; }
.tab { padding: 10px 18px; cursor: pointer; border-bottom: 2px solid transparent;
       margin-bottom: -2px; font-weight: 500; color: #666; font-size: 0.9rem; }
.tab:hover { color: #333; }
.tab.active { color: #1a1a2e; border-bottom-color: #1a1a2e; }
.tab-panel { display: none; padding: 16px; background: #fff; }
.tab-panel.active { display: block; }

/* Case navigation */
.case-nav { display: flex; align-items: center; gap: 12px; padding: 12px 0;
            border-bottom: 1px solid #eee; margin-bottom: 12px; }
.case-nav button { padding: 6px 14px; border: 1px solid #ccc; border-radius: 4px;
                   background: #fff; cursor: pointer; font-size: 0.85rem; }
.case-nav button:hover { background: #f0f0f0; }
.case-nav button:disabled { opacity: 0.4; cursor: default; }
.case-nav .counter { font-weight: 600; font-size: 0.9rem; }

/* Case detail */
.case-detail { margin: 12px 0; }
.case-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 4px; }
.case-prompt { background: #f9f9f9; padding: 10px 14px; border-radius: 6px;
               border-left: 3px solid #1a1a2e; margin-bottom: 12px; font-size: 0.9rem; }
.case-score { font-weight: 700; margin-bottom: 8px; }

/* Assertions */
.assertion-item { padding: 6px 10px; margin: 4px 0; border-radius: 4px; font-size: 0.85rem;
                  display: flex; align-items: flex-start; gap: 8px; }
.assertion-item.pass { background: #e8f5e9; }
.assertion-item.fail { background: #ffebee; }
.badge { display: inline-block; padding: 1px 6px; border-radius: 3px;
         font-size: 0.72rem; font-weight: 700; color: #fff; flex-shrink: 0; }
.badge.pass { background: #4caf50; }
.badge.fail { background: #ef5350; }
.grade-tag { font-size: 0.72rem; color: #888; flex-shrink: 0; }
.grade-tag.g1 { color: #2e7d32; }
.grade-tag.g2 { color: #1565c0; }
.grade-tag.g3 { color: #6a1b9a; }
.assertion-text { flex: 1; }
.evidence { font-size: 0.8rem; color: #666; font-style: italic; margin-top: 2px; }
.note-btn { font-size: 0.72rem; padding: 2px 8px; border: 1px solid #bbb;
            border-radius: 3px; background: #fff; cursor: pointer; flex-shrink: 0; }
.note-btn:hover { background: #f0f0f0; }

/* Note form */
.note-form { margin-top: 6px; padding: 8px; background: #fff; border: 1px solid #ddd;
             border-radius: 4px; display: none; }
.note-form.open { display: block; }
.note-form textarea { width: 100%; height: 60px; padding: 6px; border: 1px solid #ccc;
                      border-radius: 4px; font-size: 0.85rem; resize: vertical; }
.note-form select { padding: 4px 8px; border: 1px solid #ccc; border-radius: 4px;
                    font-size: 0.85rem; margin-right: 8px; }
.note-form .actions { margin-top: 6px; display: flex; gap: 8px; align-items: center; }
.note-form button { padding: 4px 12px; border: 1px solid #ccc; border-radius: 4px;
                    font-size: 0.85rem; cursor: pointer; }
.note-form button.primary { background: #1a1a2e; color: #fff; border-color: #1a1a2e; }
.saved-msg { color: #2e7d32; font-size: 0.8rem; display: none; }

/* Previous iteration comparison (collapsed) */
.prev-section { margin-top: 12px; }
.prev-toggle { cursor: pointer; font-size: 0.85rem; color: #1565c0; }
.prev-toggle:hover { text-decoration: underline; }
.prev-content { display: none; margin-top: 8px; padding: 8px; background: #f5f5f5;
                border-radius: 4px; font-size: 0.85rem; }
.prev-content.open { display: block; }

/* Benchmark tab */
.bench-table { width: 100%; border-collapse: collapse; }
.bench-table th, .bench-table td { padding: 8px 12px; text-align: left;
                                    border-bottom: 1px solid #eee; }
.bench-table th { background: #fafafa; font-weight: 600; }

/* Regression tab */
.reg-status { padding: 10px 16px; border-radius: 6px; font-weight: 700; margin-bottom: 12px; }
.reg-status.ok { background: #e8f5e9; color: #2e7d32; }
.reg-status.regressed { background: #ffebee; color: #c62828; }

/* Notes tab */
.notes-list { list-style: none; }
.notes-list li { padding: 8px 12px; border-bottom: 1px solid #eee; font-size: 0.85rem; }
.notes-list .note-meta { color: #888; font-size: 0.8rem; }
.notes-list .resolved { text-decoration: line-through; opacity: 0.6; }

/* Transcript tab */
.transcript { font-family: 'SF Mono', Consolas, monospace; font-size: 0.82rem;
              background: #1e1e1e; color: #d4d4d4; padding: 16px; border-radius: 6px;
              overflow-x: auto; white-space: pre-wrap; max-height: 600px; overflow-y: auto; }

.empty-msg { color: #999; font-style: italic; padding: 20px 0; }
"""


def _build_viewer_js() -> str:
    """Generate the viewer JS (tab switching, case navigation, feedback)."""
    return textwrap.dedent("""\
    (function() {
      var resultsData = null;
      var previousData = null;
      var notesData = [];
      var currentCase = 0;

      function esc(s) {
        var d = document.createElement('div');
        d.textContent = s || '';
        return d.innerHTML;
      }

      function init() {
        fetch('/api/results').then(r => r.json()).then(function(d) {
          resultsData = d;
          renderCases();
        }).catch(function() { document.getElementById('cases-content').innerHTML = '<p class="empty-msg">No results loaded.</p>'; });
        fetch('/api/previous').then(r => r.json()).then(function(d) {
          previousData = d;
        }).catch(function() {});
        fetch('/api/notes').then(r => r.json()).then(function(d) {
          notesData = d || [];
          renderNotes();
        }).catch(function() {});

        // Tab switching
        document.querySelectorAll('.tab').forEach(function(tab) {
          tab.addEventListener('click', function() {
            var target = this.getAttribute('data-tab');
            document.querySelectorAll('.tab').forEach(function(t) { t.classList.remove('active'); });
            document.querySelectorAll('.tab-panel').forEach(function(p) { p.classList.remove('active'); });
            this.classList.add('active');
            document.getElementById('panel-' + target).classList.add('active');
          });
        });

        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
          if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') return;
          if (e.key === 'ArrowLeft') navigateCase(-1);
          if (e.key === 'ArrowRight') navigateCase(1);
        });
      }

      function getCases() {
        if (!resultsData) return [];
        if (resultsData.behavior && resultsData.behavior.cases) return resultsData.behavior.cases;
        return [];
      }

      function navigateCase(delta) {
        var cases = getCases();
        if (!cases.length) return;
        currentCase = Math.max(0, Math.min(cases.length - 1, currentCase + delta));
        renderCases();
      }

      function renderCases() {
        var container = document.getElementById('cases-content');
        var cases = getCases();
        if (!cases.length) {
          container.innerHTML = '<p class="empty-msg">No behavior evaluation cases found.</p>';
          document.getElementById('case-counter').textContent = '0/0';
          return;
        }
        document.getElementById('case-counter').textContent = (currentCase + 1) + '/' + cases.length;
        document.getElementById('btn-prev').disabled = currentCase === 0;
        document.getElementById('btn-next').disabled = currentCase === cases.length - 1;
        var c = cases[currentCase];
        var total = (c.assertions || []).length;
        var passed = (c.assertions || []).filter(function(a) { return a.pass; }).length;
        var rate = total ? ((passed / total * 100).toFixed(1) + '%') : 'N/A';
        var html = '<div class="case-detail">';
        html += '<div class="case-title">' + esc(c.name || ('Case ' + (c.id || currentCase + 1))) + '</div>';
        if (c.prompt) html += '<div class="case-prompt">' + esc(c.prompt) + '</div>';
        html += '<div class="case-score">' + passed + '/' + total + ' (' + rate + ')</div>';
        html += '<div class="assertions-list">';
        (c.assertions || []).forEach(function(a, idx) {
          var pc = a.pass ? 'pass' : 'fail';
          var grade = a.grade || a.type || 'G?';
          var gc = grade.toLowerCase().replace(/[^a-z0-9]/g, '');
          if (gc.startsWith('g1') || gc === 'file_check' || gc === 'content_check') gc = 'g1';
          else if (gc.startsWith('g2') || gc === 'behavior_check') gc = 'g2';
          else if (gc.startsWith('g3') || gc === 'output_check') gc = 'g3';
          html += '<div class="assertion-item ' + pc + '">';
          html += '<span class="badge ' + pc + '">' + (a.pass ? 'PASS' : 'FAIL') + '</span>';
          html += '<span class="grade-tag ' + gc + '">' + esc(grade) + '</span>';
          html += '<span class="assertion-text">' + esc(a.text || a.assertion || '') + '</span>';
          html += '<button class="note-btn" onclick="toggleNote(' + currentCase + ',' + idx + ')">+note</button>';
          html += '</div>';
          if (a.evidence) html += '<div class="evidence">' + esc(a.evidence) + '</div>';
          html += '<div class="note-form" id="note-form-' + currentCase + '-' + idx + '">';
          html += '<textarea placeholder="Enter feedback..."></textarea>';
          html += '<div class="actions"><select>';
          html += '<option value="observation">observation</option>';
          html += '<option value="fix_suggestion">fix_suggestion</option>';
          html += '<option value="assertion_issue">assertion_issue</option>';
          html += '<option value="skip_reason">skip_reason</option>';
          html += '</select>';
          html += '<button class="primary" onclick="saveNote(' + currentCase + ',' + idx + ')">Save</button>';
          html += '<span class="saved-msg" id="saved-' + currentCase + '-' + idx + '">Saved!</span>';
          html += '</div></div>';
        });
        html += '</div></div>';
        container.innerHTML = html;

        // Render benchmark and regression in their panels
        renderBenchmark();
        renderRegression();
        renderTranscript();
      }

      window.toggleNote = function(caseIdx, assertIdx) {
        var form = document.getElementById('note-form-' + caseIdx + '-' + assertIdx);
        if (form) form.classList.toggle('open');
      };

      window.saveNote = function(caseIdx, assertIdx) {
        var form = document.getElementById('note-form-' + caseIdx + '-' + assertIdx);
        var textarea = form.querySelector('textarea');
        var select = form.querySelector('select');
        var cases = getCases();
        var c = cases[caseIdx];
        var body = {
          skill: (resultsData.behavior || resultsData.trigger || {}).skill || 'unknown',
          eval_id: c.id || caseIdx + 1,
          eval_name: c.name || '',
          assertion_idx: assertIdx,
          note: textarea.value,
          note_type: select.value,
          author: 'viewer'
        };
        fetch('/api/feedback', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(body)
        }).then(function(r) {
          if (r.ok) {
            var msg = document.getElementById('saved-' + caseIdx + '-' + assertIdx);
            msg.style.display = 'inline';
            setTimeout(function() { msg.style.display = 'none'; }, 2000);
            textarea.value = '';
            form.classList.remove('open');
            // Refresh notes
            fetch('/api/notes').then(r2 => r2.json()).then(function(d) { notesData = d || []; renderNotes(); });
          }
        });
      };

      function renderBenchmark() {
        var panel = document.getElementById('benchmark-content');
        if (!resultsData || !resultsData.benchmark) {
          panel.innerHTML = '<p class="empty-msg">No benchmark data. Run <code>make eval-benchmark</code>.</p>';
          return;
        }
        var b = resultsData.benchmark;
        var configs = b.configurations || {};
        var wp = configs.with_plugin || {};
        var wop = configs.without_plugin || {};
        var delta = configs.delta || {};
        function fmtStat(v) {
          if (!v || typeof v !== 'object') return esc(String(v || 'N/A'));
          var s = String(v.mean != null ? v.mean : 'N/A');
          if (v.stddev != null) s += ' +/- ' + v.stddev;
          return esc(s);
        }
        var html = '<table class="bench-table"><thead><tr><th>Metric</th><th>With Plugin</th><th>Without Plugin</th><th>Delta</th></tr></thead><tbody>';
        html += '<tr><td>Pass Rate</td><td>' + fmtStat(wp.pass_rate) + '</td><td>' + fmtStat(wop.pass_rate) + '</td><td><strong>' + esc(delta.pass_rate || '') + '</strong></td></tr>';
        html += '<tr><td>Duration (s)</td><td>' + fmtStat(wp.duration) + '</td><td>' + fmtStat(wop.duration) + '</td><td></td></tr>';
        html += '<tr><td>Tokens</td><td>' + fmtStat(wp.tokens) + '</td><td>' + fmtStat(wop.tokens) + '</td><td>' + esc(delta.token_overhead || '') + '</td></tr>';
        html += '</tbody></table>';
        panel.innerHTML = html;
      }

      function renderRegression() {
        var panel = document.getElementById('regression-content');
        if (!resultsData || !resultsData.regression) {
          panel.innerHTML = '<p class="empty-msg">No regression data. Run <code>make eval-regress</code>.</p>';
          return;
        }
        // Regression data is loaded from the global regress directory, not per-workspace
        panel.innerHTML = '<p class="empty-msg">Regression data available via static dashboard.</p>';
      }

      function renderNotes() {
        var panel = document.getElementById('notes-content');
        if (!notesData || !notesData.length) {
          panel.innerHTML = '<p class="empty-msg">No feedback notes yet. Click [+note] on assertions to add.</p>';
          return;
        }
        var html = '<ul class="notes-list">';
        notesData.forEach(function(n) {
          var cls = n.resolved ? 'resolved' : '';
          html += '<li class="' + cls + '">';
          html += '<strong>' + esc(n.skill) + '#' + n.eval_id + '</strong>';
          if (n.assertion_idx != null) html += ' @assertion-' + n.assertion_idx;
          html += ' <span class="note-meta">[' + esc(n.note_type) + '] ' + esc(n.timestamp || '').substring(0, 19) + ' by ' + esc(n.author) + '</span>';
          html += '<br>' + esc(n.note);
          if (n.resolved) html += ' <em>(resolved: ' + esc(n.resolved_by || '') + ')</em>';
          html += '</li>';
        });
        html += '</ul>';
        panel.innerHTML = html;
      }

      function renderTranscript() {
        var panel = document.getElementById('transcript-content');
        // Transcript data comes from behavior execution logs if available
        if (!resultsData || !resultsData.behavior) {
          panel.innerHTML = '<p class="empty-msg">No transcript data available.</p>';
          return;
        }
        var cases = getCases();
        var c = cases[currentCase];
        if (!c || !c.transcript) {
          panel.innerHTML = '<p class="empty-msg">No transcript for this case.</p>';
          return;
        }
        var html = '<div class="transcript">';
        if (Array.isArray(c.transcript)) {
          c.transcript.forEach(function(turn, i) {
            html += 'Turn ' + (i + 1) + ': ' + esc(JSON.stringify(turn)) + '\\n';
          });
        } else {
          html += esc(typeof c.transcript === 'string' ? c.transcript : JSON.stringify(c.transcript, null, 2));
        }
        html += '</div>';
        panel.innerHTML = html;
      }

      window.navigateCase = navigateCase;
      document.addEventListener('DOMContentLoaded', init);
    })();
    """)


def _build_viewer_html(skill_name: str, port: int) -> str:
    """Build the main viewer HTML page."""
    return textwrap.dedent(f"""\
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>devpace Eval Viewer - {_esc(skill_name)}</title>
      <style>{_VIEWER_CSS}</style>
    </head>
    <body>
      <header>
        <h1>devpace Eval Viewer</h1>
        <div class="info">
          <span>Skill: <strong>{_esc(skill_name)}</strong></span>
          <span>Port: {port}</span>
        </div>
      </header>
      <div class="container">
        <div class="tabs">
          <div class="tab active" data-tab="cases">Cases</div>
          <div class="tab" data-tab="benchmark">Benchmark</div>
          <div class="tab" data-tab="regression">Regression</div>
          <div class="tab" data-tab="notes">Notes</div>
          <div class="tab" data-tab="transcript">Transcript</div>
        </div>
        <div id="panel-cases" class="tab-panel active">
          <div class="case-nav">
            <button id="btn-prev" onclick="navigateCase(-1)">Prev</button>
            <span class="counter" id="case-counter">0/0</span>
            <button id="btn-next" onclick="navigateCase(1)">Next</button>
          </div>
          <div id="cases-content"><p class="empty-msg">Loading...</p></div>
        </div>
        <div id="panel-benchmark" class="tab-panel">
          <div id="benchmark-content"><p class="empty-msg">Loading...</p></div>
        </div>
        <div id="panel-regression" class="tab-panel">
          <div id="regression-content"><p class="empty-msg">Loading...</p></div>
        </div>
        <div id="panel-notes" class="tab-panel">
          <div id="notes-content"><p class="empty-msg">Loading...</p></div>
        </div>
        <div id="panel-transcript" class="tab-panel">
          <div id="transcript-content"><p class="empty-msg">Loading...</p></div>
        </div>
      </div>
      <script>{_build_viewer_js()}</script>
    </body>
    </html>
    """)


# ---------------------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------------------

class EvalViewerHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the eval viewer."""

    def log_message(self, fmt, *args):
        # Quieter logging
        pass

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._serve_html()
        elif self.path == "/api/results":
            self._serve_json(self.server.results_data)
        elif self.path == "/api/previous":
            self._serve_json(self.server.previous_data or {})
        elif self.path == "/api/notes":
            self._serve_json(_load_notes())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/feedback":
            self._handle_feedback()
        else:
            self.send_error(404)

    def _serve_html(self):
        html = _build_viewer_html(self.server.skill_name, self.server.server_port)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _serve_json(self, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_feedback(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            fb.append_note(
                skill=body["skill"],
                eval_id=body["eval_id"],
                eval_name=body.get("eval_name", ""),
                assertion_idx=body.get("assertion_idx"),
                note=body["note"],
                author=body.get("author", "viewer"),
                note_type=body.get("note_type", "observation"),
            )
            self._serve_json({"status": "ok"})
        except Exception as e:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class EvalViewerServer(http.server.HTTPServer):
    """Extended HTTPServer that carries eval data."""
    results_data: dict
    previous_data: dict | None
    skill_name: str


def start_viewer(
    workspace_dir: Path,
    previous_workspace: Path | None = None,
    port: int = 8420,
    auto_open: bool = True,
) -> None:
    """Start the interactive eval viewer server.

    Args:
        workspace_dir: Path to results directory (e.g. tests/evaluation/pace-dev/results/)
        previous_workspace: Optional path to previous iteration results for comparison
        port: HTTP server port (default 8420)
        auto_open: Whether to open browser automatically
    """
    # Infer skill name from workspace_dir
    # workspace_dir is typically tests/evaluation/<skill>/results/
    skill_name = workspace_dir.parent.name if workspace_dir.name == "results" else workspace_dir.name

    results_data = _load_workspace(workspace_dir)
    previous_data = _load_workspace(previous_workspace) if previous_workspace else None

    server = EvalViewerServer(("127.0.0.1", port), EvalViewerHandler)
    server.results_data = results_data
    server.previous_data = previous_data
    server.skill_name = skill_name

    url = f"http://127.0.0.1:{port}"
    print(f"devpace Eval Viewer: {url}  (Skill: {skill_name})")
    print("Press Ctrl+C to stop.")

    if auto_open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nViewer stopped.")
    finally:
        server.server_close()
