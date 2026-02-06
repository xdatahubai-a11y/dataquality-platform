"""Inline CSS styles for the HTML data quality report."""


def get_report_css() -> str:
    """Return the complete CSS for the DQ report."""
    return """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
           background: #f1f5f9; color: #1e293b; line-height: 1.6; }
    .header { background: linear-gradient(135deg, #0f172a, #1e293b); color: white;
              padding: 2rem; text-align: center; }
    .header h1 { font-size: 1.8rem; margin-bottom: 0.5rem; }
    .header .subtitle { opacity: 0.7; font-size: 0.9rem; }
    .score-big { font-size: 4rem; font-weight: 800; margin: 1rem 0; }
    .score-label { font-size: 0.9rem; opacity: 0.8; text-transform: uppercase;
                   letter-spacing: 2px; }
    .container { max-width: 1100px; margin: 0 auto; padding: 1.5rem; }
    .cards-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
    .card { background: white; border-radius: 10px; padding: 1.2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); flex: 1; min-width: 150px; }
    .card h3 { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;
               color: #64748b; margin-bottom: 0.5rem; }
    .card .value { font-size: 2rem; font-weight: 700; }
    .card .detail { font-size: 0.75rem; color: #94a3b8; margin-top: 0.3rem; }
    .green { color: #22c55e; } .yellow { color: #eab308; } .red { color: #ef4444; }
    .blue { color: #3b82f6; }
    .bg-green { background: #dcfce7; } .bg-yellow { background: #fef9c3; }
    .bg-red { background: #fee2e2; }
    table { width: 100%; border-collapse: collapse; background: white;
            border-radius: 10px; overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1.5rem; }
    th { background: #f8fafc; text-align: left; padding: 0.8rem 1rem;
         font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;
         color: #64748b; border-bottom: 2px solid #e2e8f0; }
    td { padding: 0.7rem 1rem; border-bottom: 1px solid #f1f5f9;
         font-size: 0.9rem; }
    tr:hover { background: #f8fafc; }
    .badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 9999px;
             font-size: 0.75rem; font-weight: 600; }
    .badge-pass { background: #dcfce7; color: #166534; }
    .badge-fail { background: #fee2e2; color: #991b1b; }
    .badge-critical { background: #ef4444; color: white; }
    .badge-warning { background: #fef9c3; color: #854d0e; }
    .badge-info { background: #dbeafe; color: #1e40af; }
    .section { margin-bottom: 2rem; }
    .section h2 { font-size: 1.3rem; margin-bottom: 1rem; color: #0f172a;
                  border-bottom: 2px solid #3b82f6; padding-bottom: 0.5rem;
                  display: inline-block; }
    .bar-chart { margin: 0.8rem 0; }
    .bar-row { display: flex; align-items: center; margin-bottom: 0.4rem; }
    .bar-label { width: 120px; font-size: 0.8rem; color: #64748b; }
    .bar-track { flex: 1; background: #e2e8f0; border-radius: 6px; height: 22px;
                 overflow: hidden; }
    .bar-fill { height: 100%; border-radius: 6px; display: flex;
                align-items: center; padding-left: 8px; font-size: 0.7rem;
                color: white; font-weight: 600; min-width: 30px;
                transition: width 0.3s; }
    .footer { text-align: center; padding: 2rem; color: #94a3b8;
              font-size: 0.8rem; }
    .issues-list { list-style: none; }
    .issues-list li { background: white; border-radius: 8px; padding: 1rem;
                      margin-bottom: 0.5rem;
                      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                      border-left: 4px solid #ef4444; }
    .issues-list li.warning { border-left-color: #eab308; }
    """
