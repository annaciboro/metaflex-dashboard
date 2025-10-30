# This file contains the KPI card updates with hover effects and subdued scrollbars
# To be integrated into dashboard_page.py

# CSS to add at the top of render_executive_dashboard function:
css_block = """
    <style>
    /* KPI card hover effects */
    .kpi-card {
        background: #ffffff;
        padding: 48px 32px;
        border-radius: 12px;
        border: 1px solid #e8eaed;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: default;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border-color: #d1d5db;
    }
    </style>
"""

# Example KPI card with class and better centering:
kpi_card_template = """
    <div class='kpi-card'>
        <p style='margin: 0 0 20px 0; font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.12em; color: #9ca3af;'>Open Tasks</p>
        <h2 style='margin: 0; font-size: 2.75rem; font-weight: 300; color: #1f2937; line-height: 1; letter-spacing: -0.02em;'>{value}</h2>
    </div>
"""
