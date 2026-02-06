"""HTML section builders for the data quality report."""

from datetime import datetime
from typing import Any


def _score_color(score: float) -> str:
    """Return CSS class name based on score threshold."""
    if score >= 90:
        return "green"
    if score >= 70:
        return "yellow"
    return "red"


def _bar_color(score: float) -> str:
    """Return hex color for bar charts."""
    if score >= 90:
        return "#22c55e"
    if score >= 70:
        return "#eab308"
    return "#ef4444"


def build_header(project: str, source: str, score: float, timestamp: str) -> str:
    """Build the report header with overall score."""
    color = _score_color(score)
    return f"""
    <div class="header">
      <h1>📊 {project}</h1>
      <p class="subtitle">Data Source: {source} | {timestamp}</p>
      <p class="score-label">Overall Quality Score</p>
      <p class="score-big {color}">{score:.1f}%</p>
    </div>"""


def build_score_cards(dimension_scores: dict[str, dict]) -> str:
    """Build the score cards row for each dimension."""
    cards = ""
    for dim, info in sorted(dimension_scores.items()):
        score = info["score"]
        passed = info["passed"]
        total = info["total"]
        color = _score_color(score)
        cards += f"""
        <div class="card">
          <h3>{dim}</h3>
          <div class="value {color}">{score:.1f}%</div>
          <div class="detail">{passed}/{total} rules passed</div>
        </div>"""
    return f'<div class="cards-row">{cards}</div>'


def build_summary_table(results: list[dict]) -> str:
    """Build the summary table of all rules."""
    rows = ""
    for r in results:
        status_cls = "badge-pass" if r["passed"] else "badge-fail"
        status_txt = "✅ Pass" if r["passed"] else "❌ Fail"
        sev_cls = f"badge-{r.get('severity', 'warning')}"
        threshold = f"{r['threshold']:.1f}%" if r["threshold"] is not None else "—"
        rows += f"""
        <tr>
          <td><strong>{r['rule_name']}</strong></td>
          <td>{r['dimension']}</td>
          <td>{r.get('column') or '—'}</td>
          <td>{threshold}</td>
          <td>{r['metric_value']:.2f}%</td>
          <td><span class="badge {status_cls}">{status_txt}</span></td>
          <td><span class="badge {sev_cls}">{r.get('severity', 'warning')}</span></td>
        </tr>"""

    return f"""
    <div class="section">
      <h2>All Rules</h2>
      <table>
        <thead><tr>
          <th>Rule</th><th>Dimension</th><th>Column</th>
          <th>Threshold</th><th>Actual</th><th>Status</th><th>Severity</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""


def build_dimension_breakdown(dimension_scores: dict[str, dict], results: list[dict]) -> str:
    """Build per-dimension sections with bar charts and rule lists."""
    html = ""
    for dim in sorted(dimension_scores.keys()):
        score = dimension_scores[dim]["score"]
        dim_results = [r for r in results if r["dimension"] == dim]
        bar_color = _bar_color(score)
        width = max(score, 2)

        rules_html = ""
        for r in dim_results:
            icon = "✅" if r["passed"] else "❌"
            rules_html += (
                f'<div style="margin:0.3rem 0;font-size:0.9rem;">'
                f'{icon} <strong>{r["rule_name"]}</strong> — '
                f'{r["metric_value"]:.2f}%'
                f' (threshold: {r["threshold"]:.1f}%)' if r["threshold"] is not None else ""
            )
            rules_html += "</div>"

        html += f"""
        <div class="section">
          <h2>{dim.title()}</h2>
          <div class="bar-chart">
            <div class="bar-row">
              <span class="bar-label">Score</span>
              <div class="bar-track">
                <div class="bar-fill" style="width:{width}%;background:{bar_color};">
                  {score:.1f}%
                </div>
              </div>
            </div>
          </div>
          {rules_html}
        </div>"""
    return html


def build_issues_section(results: list[dict]) -> str:
    """Build the issues section with failed rules sorted by severity."""
    failed = [r for r in results if not r["passed"]]
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    failed.sort(key=lambda r: severity_order.get(r.get("severity", "warning"), 9))

    if not failed:
        return """
        <div class="section">
          <h2>Issues</h2>
          <p style="color:#22c55e;font-weight:600;">🎉 No issues found! All rules passed.</p>
        </div>"""

    items = ""
    for r in failed:
        sev = r.get("severity", "warning")
        cls = "warning" if sev != "critical" else ""
        items += f"""
        <li class="{cls}">
          <strong>[{sev.upper()}] {r['rule_name']}</strong><br>
          Dimension: {r['dimension']} | Column: {r.get('column') or '—'}<br>
          Expected ≥ {r['threshold']:.1f}% | Got {r['metric_value']:.2f}%
        </li>"""

    return f"""
    <div class="section">
      <h2>⚠️ Issues ({len(failed)} failed)</h2>
      <ul class="issues-list">{items}</ul>
    </div>"""


def build_footer() -> str:
    """Build the report footer."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""
    <div class="footer">
      Generated by DataQuality Platform | {ts}
    </div>"""
