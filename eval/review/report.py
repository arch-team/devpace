"""Static HTML dashboard generator for eval results.

Produces a single-file HTML dashboard with all CSS/JS inlined.
No external dependencies — can be opened offline or uploaded as CI artifact.
"""
from __future__ import annotations

import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path

from eval.core import EVAL_DATA_DIR


def _read_json(path: Path) -> dict | None:
    """Read a JSON file, returning None on any error."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _collect_all_results() -> tuple[dict[str, dict], dict[str, dict], dict | None, dict | None]:
    """Single-pass collection of trigger, behavior, benchmark, and regression results.

    Returns (trigger_results, behavior_results, benchmark_results, regression_report).
    """
    trigger: dict[str, dict] = {}
    behavior: dict[str, dict] = {}
    benchmark: dict | None = None

    for skill_dir in sorted(EVAL_DATA_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("_"):
            continue
        results_dir = skill_dir / "results"
        if not results_dir.is_dir():
            continue

        name = skill_dir.name

        data = _read_json(results_dir / "latest.json")
        if data is not None:
            trigger[name] = data

        data = _read_json(results_dir / "grading" / "latest.json")
        if data is not None:
            behavior[name] = data

        if benchmark is None:
            data = _read_json(results_dir / "benchmark" / "latest.json")
            if data is not None:
                benchmark = data

    regression = _read_json(EVAL_DATA_DIR / "regress" / "latest-report.json")

    return trigger, behavior, benchmark, regression


# ---------------------------------------------------------------------------
# HTML generation helpers
# ---------------------------------------------------------------------------

def _esc(s: str) -> str:
    """Escape HTML special characters."""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _pct(num: int | float, denom: int | float) -> str:
    """Format as percentage string."""
    if denom == 0:
        return "N/A"
    return f"{num / denom * 100:.1f}%"


def _status_class(rate: float) -> str:
    """CSS class based on pass rate."""
    if rate >= 0.9:
        return "pass"
    if rate >= 0.7:
        return "warn"
    return "fail"


def _render_summary_card(
    trigger_results: dict[str, dict],
    behavior_results: dict[str, dict],
    regression_report: dict | None,
) -> str:
    """Render the Summary tab content."""
    skill_count = len(trigger_results)
    # Trigger aggregate
    trigger_total = sum(
        r.get("summary", {}).get("total", 0) for r in trigger_results.values()
    )
    trigger_passed = sum(
        r.get("summary", {}).get("passed", 0) for r in trigger_results.values()
    )
    trigger_rate = trigger_passed / max(trigger_total, 1)

    # Behavior aggregate
    behavior_total = 0
    behavior_passed = 0
    for r in behavior_results.values():
        for case in r.get("cases", []):
            for a in case.get("assertions", []):
                behavior_total += 1
                if a.get("passed"):
                    behavior_passed += 1
    behavior_rate = behavior_passed / max(behavior_total, 1)

    # Regression status
    if regression_report:
        reg_status = regression_report.get("status", "unknown")
        reg_class = "pass" if reg_status == "ok" else "fail"
    else:
        reg_status = "no data"
        reg_class = "neutral"

    return textwrap.dedent(f"""\
        <div class="summary-grid">
          <div class="card">
            <div class="card-label">Skills Evaluated</div>
            <div class="card-value">{skill_count}</div>
          </div>
          <div class="card">
            <div class="card-label">Trigger Accuracy</div>
            <div class="card-value {_status_class(trigger_rate)}">{_pct(trigger_passed, trigger_total)}</div>
            <div class="card-detail">{trigger_passed}/{trigger_total} queries</div>
          </div>
          <div class="card">
            <div class="card-label">Behavior Score</div>
            <div class="card-value {_status_class(behavior_rate)}">{_pct(behavior_passed, behavior_total)}</div>
            <div class="card-detail">{behavior_passed}/{behavior_total} assertions</div>
          </div>
          <div class="card">
            <div class="card-label">Regression</div>
            <div class="card-value {reg_class}">{_esc(reg_status.upper())}</div>
          </div>
        </div>
    """)


def _render_trigger_tab(trigger_results: dict[str, dict]) -> str:
    """Render the Trigger tab with per-skill table."""
    if not trigger_results:
        return '<p class="empty">No trigger evaluation results found.</p>'

    rows = []
    for skill, data in sorted(trigger_results.items()):
        summary = data.get("summary", {})
        total = summary.get("total", 0)
        passed = summary.get("passed", 0)
        rate = passed / max(total, 1)
        pos = data.get("positive", {})
        neg = data.get("negative", {})
        fn_count = len(data.get("false_negatives", []))
        fp_count = len(data.get("false_positives", []))
        ci = ""
        # Try to get CI from first raw result
        raws = data.get("raw_results", [])
        if raws and "confidence_interval" in raws[0]:
            lo, hi = raws[0]["confidence_interval"]
            ci = f"[{lo:.2f}, {hi:.2f}]"
        ts = data.get("timestamp", "")[:19].replace("T", " ")

        rows.append(textwrap.dedent(f"""\
            <tr>
              <td><strong>{_esc(skill)}</strong></td>
              <td class="{_status_class(rate)}">{_pct(passed, total)}</td>
              <td>{passed}/{total}</td>
              <td>{pos.get('passed', 0)}/{pos.get('total', 0)}</td>
              <td>{neg.get('passed', 0)}/{neg.get('total', 0)}</td>
              <td class="{"fail" if fn_count else ""}">{fn_count}</td>
              <td class="{"fail" if fp_count else ""}">{fp_count}</td>
              <td class="mono">{ci}</td>
              <td class="ts">{_esc(ts)}</td>
            </tr>"""))

    return textwrap.dedent("""\
        <table>
          <thead>
            <tr>
              <th>Skill</th><th>Rate</th><th>Pass/Total</th>
              <th>Positive</th><th>Negative</th>
              <th>FN</th><th>FP</th><th>CI (sample)</th><th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
    """) + "\n".join(rows) + "\n      </tbody>\n    </table>"


def _render_behavior_tab(behavior_results: dict[str, dict]) -> str:
    """Render the Behavior tab with per-case assertion details."""
    if not behavior_results:
        return '<p class="empty">No behavior evaluation results found.</p>'

    sections = []
    for skill, data in sorted(behavior_results.items()):
        cases_html = []
        for case in data.get("cases", []):
            name = case.get("name", f"case-{case.get('id', '?')}")
            assertions = case.get("assertions", [])
            total = len(assertions)
            passed = sum(1 for a in assertions if a.get("passed"))
            rate = passed / max(total, 1)

            assertion_rows = []
            for i, a in enumerate(assertions):
                grade = a.get("grade", "G?")
                status = "PASS" if a.get("passed") else "FAIL"
                sc = "pass" if a.get("passed") else "fail"
                text = _esc(a.get("text", a.get("assertion", "")))
                evidence = _esc(a.get("evidence", ""))
                ev_html = f'<div class="evidence">{evidence}</div>' if evidence else ""
                assertion_rows.append(
                    f'<div class="assertion {sc}">'
                    f'<span class="badge {sc}">{status}</span> '
                    f'<span class="grade">{grade}</span> '
                    f'{text}{ev_html}</div>'
                )

            cases_html.append(textwrap.dedent(f"""\
                <div class="case">
                  <div class="case-header">
                    <span class="case-name">{_esc(name)}</span>
                    <span class="case-score {_status_class(rate)}">{passed}/{total} ({_pct(passed, total)})</span>
                  </div>
                  <div class="assertions">
                    {"".join(assertion_rows)}
                  </div>
                </div>"""))

        sections.append(
            f'<div class="skill-section">'
            f'<h3>{_esc(skill)}</h3>'
            f'{"".join(cases_html)}'
            f'</div>'
        )

    return "\n".join(sections)


def _render_benchmark_tab(benchmark_results: dict | None) -> str:
    """Render the Benchmark tab with with/without comparison."""
    if not benchmark_results:
        return '<p class="empty">No benchmark results found. Run <code>make eval-benchmark</code> to generate.</p>'

    configs = benchmark_results.get("configurations", {})
    wp = configs.get("with_plugin", {})
    wop = configs.get("without_plugin", {})
    delta = configs.get("delta", {})

    def _stat_row(label: str, wp_val: dict | str, wop_val: dict | str, delta_val: str = "") -> str:
        if isinstance(wp_val, dict):
            wp_str = f"{wp_val.get('mean', 'N/A')}"
            if "stddev" in wp_val:
                wp_str += f" +/- {wp_val['stddev']}"
        else:
            wp_str = str(wp_val)
        if isinstance(wop_val, dict):
            wop_str = f"{wop_val.get('mean', 'N/A')}"
            if "stddev" in wop_val:
                wop_str += f" +/- {wop_val['stddev']}"
        else:
            wop_str = str(wop_val)
        return (
            f"<tr><td>{_esc(label)}</td>"
            f"<td>{_esc(wp_str)}</td>"
            f"<td>{_esc(wop_str)}</td>"
            f"<td><strong>{_esc(str(delta_val))}</strong></td></tr>"
        )

    rows = []
    rows.append(_stat_row(
        "Pass Rate",
        wp.get("pass_rate", "N/A"),
        wop.get("pass_rate", "N/A"),
        delta.get("pass_rate", ""),
    ))
    rows.append(_stat_row(
        "Duration (s)",
        wp.get("duration", "N/A"),
        wop.get("duration", "N/A"),
    ))
    rows.append(_stat_row(
        "Tokens",
        wp.get("tokens", "N/A"),
        wop.get("tokens", "N/A"),
        delta.get("token_overhead", ""),
    ))

    return textwrap.dedent("""\
        <table>
          <thead>
            <tr>
              <th>Metric</th><th>With Plugin</th><th>Without Plugin</th><th>Delta</th>
            </tr>
          </thead>
          <tbody>
    """) + "\n".join(rows) + "\n      </tbody>\n    </table>"


def _render_regression_tab(regression_report: dict | None) -> str:
    """Render the Regression tab."""
    if not regression_report:
        return '<p class="empty">No regression report found. Run <code>make eval-regress</code> to generate.</p>'

    status = regression_report.get("status", "unknown")
    details = regression_report.get("details", [])
    status_class = "pass" if status == "ok" else "fail"

    header = f'<div class="reg-status {status_class}">Regression Status: {_esc(status.upper())}</div>'

    if not details:
        return header + '<p>No regression details available.</p>'

    rows = []
    for d in details:
        skill = d.get("skill", "?")
        dimension = d.get("dimension", "?")
        baseline_val = d.get("baseline", "?")
        current_val = d.get("current", "?")
        regressed = d.get("regressed", False)
        rc = "fail" if regressed else "pass"
        rows.append(
            f'<tr class="{rc}">'
            f"<td>{_esc(skill)}</td>"
            f"<td>{_esc(dimension)}</td>"
            f"<td>{_esc(str(baseline_val))}</td>"
            f"<td>{_esc(str(current_val))}</td>"
            f'<td class="{rc}">{"REGRESSED" if regressed else "OK"}</td>'
            f"</tr>"
        )

    table = textwrap.dedent("""\
        <table>
          <thead>
            <tr><th>Skill</th><th>Dimension</th><th>Baseline</th><th>Current</th><th>Status</th></tr>
          </thead>
          <tbody>
    """) + "\n".join(rows) + "\n      </tbody>\n    </table>"

    return header + table


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

_CSS = """\
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       background: #f5f5f5; color: #333; line-height: 1.5; }
.container { max-width: 1200px; margin: 0 auto; padding: 20px; }
header { background: #1a1a2e; color: #fff; padding: 16px 24px; display: flex;
         align-items: center; justify-content: space-between; }
header h1 { font-size: 1.25rem; font-weight: 600; }
header .meta { font-size: 0.85rem; opacity: 0.8; }

/* Tabs */
.tabs { display: flex; background: #fff; border-bottom: 2px solid #e0e0e0;
        padding: 0 20px; }
.tab { padding: 12px 20px; cursor: pointer; border-bottom: 2px solid transparent;
       margin-bottom: -2px; font-weight: 500; color: #666; }
.tab:hover { color: #333; }
.tab.active { color: #1a1a2e; border-bottom-color: #1a1a2e; }
.tab-content { display: none; padding: 20px; background: #fff;
               border-radius: 0 0 8px 8px; }
.tab-content.active { display: block; }

/* Summary cards */
.summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px; margin: 20px 0; }
.card { background: #fafafa; border: 1px solid #e0e0e0; border-radius: 8px;
        padding: 20px; text-align: center; }
.card-label { font-size: 0.85rem; color: #888; text-transform: uppercase;
              letter-spacing: 0.05em; margin-bottom: 8px; }
.card-value { font-size: 2rem; font-weight: 700; }
.card-detail { font-size: 0.8rem; color: #999; margin-top: 4px; }

/* Status colors */
.pass { color: #2e7d32; }
.warn { color: #f57f17; }
.fail { color: #c62828; }
.neutral { color: #666; }

/* Tables */
table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 0.9rem; }
th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #eee; }
th { background: #fafafa; font-weight: 600; color: #555; }
tr:hover { background: #f9f9f9; }
.mono { font-family: 'SF Mono', Consolas, monospace; font-size: 0.85rem; }
.ts { font-size: 0.8rem; color: #999; }

/* Behavior tab */
.skill-section { margin-bottom: 24px; }
.skill-section h3 { font-size: 1.1rem; margin-bottom: 12px; padding-bottom: 4px;
                    border-bottom: 1px solid #e0e0e0; }
.case { margin-bottom: 16px; padding: 12px; background: #fafafa;
        border-radius: 6px; border: 1px solid #eee; }
.case-header { display: flex; justify-content: space-between; align-items: center;
               margin-bottom: 8px; }
.case-name { font-weight: 600; }
.case-score { font-weight: 600; font-size: 0.9rem; }
.assertions { display: flex; flex-direction: column; gap: 4px; }
.assertion { padding: 4px 8px; font-size: 0.85rem; border-radius: 4px; }
.assertion.pass { background: #e8f5e9; }
.assertion.fail { background: #ffebee; }
.badge { display: inline-block; padding: 1px 6px; border-radius: 3px;
         font-size: 0.75rem; font-weight: 700; color: #fff; margin-right: 4px; }
.badge.pass { background: #4caf50; }
.badge.fail { background: #ef5350; }
.grade { font-size: 0.75rem; color: #888; margin-right: 4px; }
.evidence { font-size: 0.8rem; color: #666; margin-top: 2px; padding-left: 50px; font-style: italic; }

/* Regression */
.reg-status { padding: 12px 16px; border-radius: 6px; font-weight: 700;
              font-size: 1.1rem; margin-bottom: 16px; }
.reg-status.pass { background: #e8f5e9; color: #2e7d32; }
.reg-status.fail { background: #ffebee; color: #c62828; }

.empty { color: #999; font-style: italic; padding: 24px 0; }
"""

# ---------------------------------------------------------------------------
# JS
# ---------------------------------------------------------------------------

_JS = """\
document.addEventListener('DOMContentLoaded', function() {
  var tabs = document.querySelectorAll('.tab');
  var contents = document.querySelectorAll('.tab-content');
  tabs.forEach(function(tab) {
    tab.addEventListener('click', function() {
      var target = this.getAttribute('data-tab');
      tabs.forEach(function(t) { t.classList.remove('active'); });
      contents.forEach(function(c) { c.classList.remove('active'); });
      this.classList.add('active');
      document.getElementById('tab-' + target).classList.add('active');
    });
  });
});
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_dashboard(
    trigger_results: dict[str, dict] | None = None,
    behavior_results: dict[str, dict] | None = None,
    benchmark_results: dict | None = None,
    regression_report: dict | None = None,
) -> str:
    """Generate a comprehensive eval dashboard as a single-file HTML string.

    All parameters are optional. If not provided, results are auto-collected
    from ``tests/evaluation/*/results/`` directories.

    Returns the complete HTML string.
    """
    if any(x is None for x in (trigger_results, behavior_results, benchmark_results, regression_report)):
        t, b, bm, rr = _collect_all_results()
        if trigger_results is None:
            trigger_results = t
        if behavior_results is None:
            behavior_results = b
        if benchmark_results is None:
            benchmark_results = bm
        if regression_report is None:
            regression_report = rr

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    summary_html = _render_summary_card(trigger_results, behavior_results, regression_report)
    trigger_html = _render_trigger_tab(trigger_results)
    behavior_html = _render_behavior_tab(behavior_results)
    benchmark_html = _render_benchmark_tab(benchmark_results)
    regression_html = _render_regression_tab(regression_report)

    return textwrap.dedent(f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>devpace Eval Dashboard</title>
          <style>{_CSS}</style>
        </head>
        <body>
          <header>
            <h1>devpace Eval Dashboard</h1>
            <span class="meta">Generated: {now}</span>
          </header>
          <div class="container">
            <div class="tabs">
              <div class="tab active" data-tab="summary">Summary</div>
              <div class="tab" data-tab="trigger">Trigger</div>
              <div class="tab" data-tab="behavior">Behavior</div>
              <div class="tab" data-tab="benchmark">Benchmark</div>
              <div class="tab" data-tab="regression">Regression</div>
            </div>
            <div id="tab-summary" class="tab-content active">
              {summary_html}
            </div>
            <div id="tab-trigger" class="tab-content">
              {trigger_html}
            </div>
            <div id="tab-behavior" class="tab-content">
              {behavior_html}
            </div>
            <div id="tab-benchmark" class="tab-content">
              {benchmark_html}
            </div>
            <div id="tab-regression" class="tab-content">
              {regression_html}
            </div>
          </div>
          <script>{_JS}</script>
        </body>
        </html>
    """)


def write_dashboard(output_path: Path | None = None, **kwargs) -> Path:
    """Generate and write dashboard HTML to disk.

    Defaults to ``tests/evaluation/_results/dashboard.html``.
    Returns the output path.
    """
    if output_path is None:
        output_path = EVAL_DATA_DIR / "_results" / "dashboard.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = generate_dashboard(**kwargs)
    output_path.write_text(html)
    return output_path
