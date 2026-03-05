#!/usr/bin/env python3
"""
Generate separate TMX Dashboard HTML files per year from CSV data.
Each year gets its own standalone HTML file with embedded data.
Also generates an index page with links to all years.
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def parse_date(date_str):
    """Parse date string in various formats."""
    for fmt in ('%Y-%m-%d', '%m/%d/%y', '%m/%d/%Y'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unable to parse date: {date_str}")

def load_csv_data(csv_path):
    """Load and process CSV data, returning data grouped by year."""
    daily_data = defaultdict(lambda: {'account_creation': 0, 'login': 0, 'payment': 0, 'other': 0})
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = parse_date(row['Date'])
            date_str = date.strftime('%Y-%m-%d')
            events = int(row['Events'].replace(',', '')) if row['Events'] else 0
            event_type = row['Event Type'].lower().replace(' ', '_')
            
            if event_type == 'transaction_other':
                event_type = 'other'
            
            if event_type in daily_data[date_str]:
                daily_data[date_str][event_type] = events
    
    # Group by year
    years_data = defaultdict(list)
    for date_str in sorted(daily_data.keys()):
        year = date_str[:4]
        record = {'date': date_str, **daily_data[date_str]}
        years_data[year].append(record)
    
    return dict(years_data)

def generate_year_html(year, data, all_years, all_data):
    """Generate a standalone HTML dashboard for a single year."""
    data_json = json.dumps(data)
    all_data_json = json.dumps(all_data)  # All years data for TMX progress calculation
    
    # Build year navigation links (will be updated by JS to include current settings)
    year_links = []
    for y in sorted(all_years, reverse=True):
        if y == year:
            year_links.append(f'<span class="year-link active">{y}</span>')
        else:
            year_links.append(f'<a href="dashboard_{y}.html" class="year-link" data-year="{y}">{y}</a>')
    year_nav = ' '.join(year_links)
    
    # Calculate date range for this year
    first_date = data[0]['date'] if data else f'{year}-01-01'
    last_date = data[-1]['date'] if data else f'{year}-12-31'
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Square TMX Dashboard - {year}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f4f8; min-height: 100vh; padding: 24px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        header {{ margin-bottom: 24px; }}
        header h1 {{ font-size: 28px; color: #1e293b; margin-bottom: 8px; }}
        header p {{ color: #64748b; font-size: 14px; }}
        
        .controls {{ display: flex; gap: 24px; align-items: center; margin-bottom: 24px; flex-wrap: wrap; }}
        .control-group {{ background: white; padding: 16px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
        .control-group h3 {{ font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; }}
        
        .year-nav {{ display: flex; gap: 8px; align-items: center; }}
        .year-link {{ padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 14px; font-weight: 500; color: #64748b; background: #f1f5f9; transition: all 0.2s; }}
        .year-link:hover {{ background: #e2e8f0; color: #1e293b; }}
        .year-link.active {{ background: #3b82f6; color: white; }}
        
        .toggle-group {{ display: flex; gap: 0; }}
        .toggle-btn {{ 
            padding: 8px 16px; border: 1px solid #cbd5e1; background: white; font-size: 13px; cursor: pointer;
            transition: all 0.2s;
        }}
        .toggle-btn:first-child {{ border-radius: 6px 0 0 6px; }}
        .toggle-btn:last-child {{ border-radius: 0 6px 6px 0; }}
        .toggle-btn:not(:first-child) {{ border-left: none; }}
        .toggle-btn.active {{ background: #3b82f6; color: white; border-color: #3b82f6; }}
        .toggle-btn:hover:not(.active) {{ background: #f1f5f9; }}
        
        .checkbox-group {{ display: flex; gap: 16px; flex-wrap: wrap; }}
        .checkbox-label {{ display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 13px; color: #475569; }}
        .checkbox-label input {{ display: none; }}
        .checkbox-box {{ width: 16px; height: 16px; border-radius: 4px; border: 2px solid #cbd5e1; transition: all 0.2s; }}
        .checkbox-box.blue {{ border-color: #3b82f6; background: #3b82f6; }}
        .checkbox-box.green {{ border-color: #10b981; background: #10b981; }}
        .checkbox-box.purple {{ border-color: #8b5cf6; background: #8b5cf6; }}
        .checkbox-box.orange {{ border-color: #f59e0b; background: #f59e0b; }}
        .checkbox-label input:not(:checked) + .checkbox-box {{ background: white; }}
        
        .summary-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
        .summary-card {{ display: flex; align-items: center; gap: 14px; }}
        .card-icon {{ width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }}
        .card-icon.blue {{ background: #dbeafe; }}
        .card-icon.green {{ background: #d1fae5; }}
        .card-icon.purple {{ background: #ede9fe; }}
        .card-icon.orange {{ background: #fef3c7; }}
        .card-content h3 {{ font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }}
        .card-content .value {{ font-size: 24px; font-weight: 700; color: #1e293b; }}
        
        .chart-section {{ margin-bottom: 24px; }}
        .card-header {{ margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }}
        .card-title {{ font-size: 16px; font-weight: 600; color: #1e293b; }}
        .chart-container {{ position: relative; height: 350px; }}
        .charts-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }}
        @media (max-width: 900px) {{ .charts-row {{ grid-template-columns: 1fr; }} }}
        .chart-container-small {{ position: relative; height: 280px; }}
        
        .last-updated {{ font-size: 12px; color: #94a3b8; margin-bottom: 16px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Square TMX Dashboard - Usage By Event Type</h1>
            <p id="dateRangeText">Event analytics for {year}</p>
        </header>
        <div class="last-updated">Data last updated: {datetime.now().strftime('%B %d, %Y')}</div>
        
        <div class="controls">
            <div class="control-group">
                <h3>Year</h3>
                <div class="year-nav">{year_nav}</div>
            </div>
            
            <div class="control-group">
                <h3>Aggregation</h3>
                <div class="toggle-group">
                    <button class="toggle-btn" data-agg="day" onclick="setAggregation('day')">Day</button>
                    <button class="toggle-btn active" data-agg="week" onclick="setAggregation('week')">Week</button>
                    <button class="toggle-btn" data-agg="month" onclick="setAggregation('month')">Month</button>
                </div>
            </div>
            
            <div class="control-group">
                <h3>Event Types</h3>
                <div class="checkbox-group">
                    <label class="checkbox-label"><input type="checkbox" checked onchange="toggleEventType('account_creation')" data-event="account_creation"><span class="checkbox-box blue"></span>Account Creation</label>
                    <label class="checkbox-label"><input type="checkbox" checked onchange="toggleEventType('login')" data-event="login"><span class="checkbox-box green"></span>Login</label>
                    <label class="checkbox-label"><input type="checkbox" checked onchange="toggleEventType('payment')" data-event="payment"><span class="checkbox-box purple"></span>Payment</label>
                    <label class="checkbox-label"><input type="checkbox" checked onchange="toggleEventType('other')" data-event="other"><span class="checkbox-box orange"></span>Other</label>
                </div>
            </div>
        </div>

        <div class="summary-cards">
            <div class="card summary-card">
                <div class="card-icon blue">👤</div>
                <div class="card-content"><h3>Account Creations</h3><div class="value" id="totalAccountCreation">-</div></div>
            </div>
            <div class="card summary-card">
                <div class="card-icon green">🔑</div>
                <div class="card-content"><h3>Logins</h3><div class="value" id="totalLogin">-</div></div>
            </div>
            <div class="card summary-card">
                <div class="card-icon purple">💳</div>
                <div class="card-content"><h3>Payments</h3><div class="value" id="totalPayment">-</div></div>
            </div>
            <div class="card summary-card">
                <div class="card-icon orange">🔄</div>
                <div class="card-content"><h3>Other</h3><div class="value" id="totalOther">-</div></div>
            </div>
        </div>
        
        <div class="card tmx-progress-card" style="margin-bottom: 24px;">
            <div class="card-header" style="margin-bottom: 12px;">
                <h2 class="card-title">📊 TMX Agreement Progress (Since Apr 1, 2025)</h2>
                <a href="https://docs.google.com/document/d/1z74-3KJhNEOadiCZmX2S5g0zMWfSfvz6MwNYfW0eOXg/edit?tab=t.0" target="_blank" style="font-size: 12px; color: #3b82f6; text-decoration: none;">View Agreement →</a>
            </div>
            <div style="display: flex; align-items: center; gap: 24px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 300px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="font-size: 14px; color: #475569;">Progress to 100M events</span>
                        <span id="tmxPercentage" style="font-size: 14px; font-weight: 600; color: #3b82f6;">-</span>
                    </div>
                    <div style="background: #e2e8f0; border-radius: 8px; height: 24px; overflow: hidden;">
                        <div id="tmxProgressBar" style="background: linear-gradient(90deg, #3b82f6, #8b5cf6); height: 100%; border-radius: 8px; transition: width 0.5s ease; width: 0%;"></div>
                    </div>
                </div>
                <div style="display: flex; gap: 24px; flex-wrap: wrap;">
                    <div style="text-align: center;">
                        <div style="font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">Total Events</div>
                        <div id="tmxTotalEvents" style="font-size: 20px; font-weight: 700; color: #1e293b;">-</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">Remaining</div>
                        <div id="tmxRemaining" style="font-size: 20px; font-weight: 700; color: #64748b;">-</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">Est. Completion</div>
                        <div id="tmxEstCompletion" style="font-size: 20px; font-weight: 700; color: #10b981;">-</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="chart-section">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Event Trends Over Time</h2>
                    <span id="chartAggLabel" style="font-size:12px;color:#64748b;">Weekly</span>
                </div>
                <div class="chart-container"><canvas id="lineChart"></canvas></div>
            </div>
        </div>

        <div class="charts-row">
            <div class="card">
                <div class="card-header"><h2 class="card-title">Event Distribution</h2></div>
                <div class="chart-container-small"><canvas id="donutChart"></canvas></div>
            </div>
            <div class="card">
                <div class="card-header"><h2 class="card-title">Monthly Totals</h2></div>
                <div class="chart-container-small"><canvas id="barChart"></canvas></div>
            </div>
        </div>
    </div>

    <script>
        const rawData = {data_json};
        const allData = {all_data_json};
        const TMX_TARGET = 100000000;
        const TMX_START_DATE = '2025-04-01';
        let currentAggregation = 'week';
        let activeEventTypes = {{ account_creation: true, login: true, payment: true, other: true }};
        let lineChart, donutChart, barChart;
        const colors = {{ blue: '#3b82f6', green: '#10b981', purple: '#8b5cf6', orange: '#f59e0b' }};
        
        // TMX Agreement Progress Calculation
        function updateTmxProgress() {{
            // Filter data from April 1, 2025 onwards
            const tmxData = allData.filter(d => d.date >= TMX_START_DATE);
            
            if (tmxData.length === 0) {{
                document.getElementById('tmxTotalEvents').textContent = '0';
                document.getElementById('tmxRemaining').textContent = formatNum(TMX_TARGET);
                document.getElementById('tmxPercentage').textContent = '0%';
                document.getElementById('tmxProgressBar').style.width = '0%';
                document.getElementById('tmxEstCompletion').textContent = 'N/A';
                return;
            }}
            
            // Calculate total events since Apr 1, 2025 (excluding "other" events)
            const totalEvents = tmxData.reduce((sum, d) => {{
                return sum + d.account_creation + d.login + d.payment;
            }}, 0);
            
            const remaining = Math.max(0, TMX_TARGET - totalEvents);
            const percentage = Math.min(100, (totalEvents / TMX_TARGET) * 100);
            
            // Calculate daily average and estimate completion
            const firstDate = new Date(tmxData[0].date + 'T00:00:00');
            const lastDate = new Date(tmxData[tmxData.length - 1].date + 'T00:00:00');
            const daysCovered = Math.max(1, Math.ceil((lastDate - firstDate) / (1000 * 60 * 60 * 24)) + 1);
            const dailyAverage = totalEvents / daysCovered;
            
            let estCompletion = 'Achieved! 🎉';
            if (remaining > 0 && dailyAverage > 0) {{
                const daysRemaining = Math.ceil(remaining / dailyAverage);
                const completionDate = new Date(lastDate);
                completionDate.setDate(completionDate.getDate() + daysRemaining);
                estCompletion = completionDate.toLocaleDateString('en-US', {{ month: 'short', year: 'numeric' }});
            }}
            
            // Update UI
            document.getElementById('tmxTotalEvents').textContent = formatNum(totalEvents);
            document.getElementById('tmxRemaining').textContent = formatNum(remaining);
            document.getElementById('tmxPercentage').textContent = percentage.toFixed(1) + '%';
            document.getElementById('tmxProgressBar').style.width = percentage + '%';
            document.getElementById('tmxEstCompletion').textContent = estCompletion;
            
            // Change color if achieved
            if (percentage >= 100) {{
                document.getElementById('tmxProgressBar').style.background = 'linear-gradient(90deg, #10b981, #059669)';
            }}
        }}
        
        // URL parameter handling for persistent settings
        function getUrlParams() {{
            const params = new URLSearchParams(window.location.search);
            return {{
                agg: params.get('agg') || 'week',
                events: params.get('events') || 'account_creation,login,payment,other'
            }};
        }}
        
        function buildUrlParams() {{
            const activeEvents = Object.keys(activeEventTypes).filter(k => activeEventTypes[k]).join(',');
            return `?agg=${{currentAggregation}}&events=${{activeEvents}}`;
        }}
        
        function updateYearLinks() {{
            const params = buildUrlParams();
            document.querySelectorAll('.year-link[data-year]').forEach(link => {{
                const year = link.dataset.year;
                link.href = `dashboard_${{year}}.html${{params}}`;
            }});
        }}
        
        function applyUrlParams() {{
            const params = getUrlParams();
            
            // Apply aggregation
            currentAggregation = params.agg;
            document.querySelectorAll('.toggle-btn').forEach(btn => {{
                btn.classList.toggle('active', btn.dataset.agg === currentAggregation);
            }});
            const labels = {{ day: 'Daily', week: 'Weekly', month: 'Monthly' }};
            document.getElementById('chartAggLabel').textContent = labels[currentAggregation] || 'Weekly';
            
            // Apply event type filters
            const activeEvents = params.events.split(',');
            activeEventTypes = {{
                account_creation: activeEvents.includes('account_creation'),
                login: activeEvents.includes('login'),
                payment: activeEvents.includes('payment'),
                other: activeEvents.includes('other')
            }};
            
            // Update checkboxes
            document.querySelectorAll('.checkbox-label input[data-event]').forEach(checkbox => {{
                checkbox.checked = activeEventTypes[checkbox.dataset.event];
            }});
            
            updateYearLinks();
        }}
        
        function toggleEventType(eventType) {{
            activeEventTypes[eventType] = !activeEventTypes[eventType];
            updateYearLinks();
            updateDashboard();
        }}

        function formatNum(n) {{
            if (n >= 1e6) return (n/1e6).toFixed(1) + 'M';
            if (n >= 1e3) return (n/1e3).toFixed(1) + 'K';
            return n.toLocaleString();
        }}

        function formatDate(d) {{
            return new Date(d + 'T00:00:00').toLocaleDateString('en-US', {{ month: 'short', day: 'numeric' }});
        }}

        function getWeekStart(dateStr) {{
            const d = new Date(dateStr + 'T00:00:00');
            const day = d.getDay();
            const diff = d.getDate() - day + (day === 0 ? -6 : 1);
            d.setDate(diff);
            return d.toISOString().split('T')[0];
        }}

        function aggregateData(data, level) {{
            if (level === 'day') return data;
            
            const grouped = {{}};
            data.forEach(row => {{
                let key;
                if (level === 'week') {{
                    key = getWeekStart(row.date);
                }} else {{
                    key = row.date.substring(0, 7) + '-01';
                }}
                if (!grouped[key]) {{
                    grouped[key] = {{ date: key, account_creation: 0, login: 0, payment: 0, other: 0 }};
                }}
                grouped[key].account_creation += row.account_creation;
                grouped[key].login += row.login;
                grouped[key].payment += row.payment;
                grouped[key].other += row.other;
            }});
            return Object.values(grouped).sort((a, b) => a.date.localeCompare(b.date));
        }}

        function setAggregation(level) {{
            currentAggregation = level;
            document.querySelectorAll('.toggle-btn').forEach(btn => {{
                btn.classList.toggle('active', btn.dataset.agg === level);
            }});
            const labels = {{ day: 'Daily', week: 'Weekly', month: 'Monthly' }};
            document.getElementById('chartAggLabel').textContent = labels[level];
            updateYearLinks();
            updateDashboard();
        }}

        function updateDashboard() {{
            const data = rawData;
            
            // Calculate totals
            const totals = data.reduce((a, r) => {{
                a.account_creation += r.account_creation;
                a.login += r.login;
                a.payment += r.payment;
                a.other += r.other;
                return a;
            }}, {{ account_creation: 0, login: 0, payment: 0, other: 0 }});

            document.getElementById('totalAccountCreation').textContent = formatNum(totals.account_creation);
            document.getElementById('totalLogin').textContent = formatNum(totals.login);
            document.getElementById('totalPayment').textContent = formatNum(totals.payment);
            document.getElementById('totalOther').textContent = formatNum(totals.other);

            // Update date range text
            if (data.length > 0) {{
                const start = formatDate(data[0].date);
                const end = formatDate(data[data.length-1].date);
                document.getElementById('dateRangeText').textContent = `Event analytics for {year} (${{start}} - ${{end}})`;
            }}

            const aggData = aggregateData(data, currentAggregation);
            
            // Build datasets based on active event types
            const lineDatasets = [];
            const donutLabels = [];
            const donutData = [];
            const donutColors = [];
            const barDatasets = [];
            
            if (activeEventTypes.account_creation) {{
                lineDatasets.push({{ label: 'Account Creation', data: aggData.map(d => d.account_creation), borderColor: colors.blue, backgroundColor: 'transparent', tension: 0.3, borderWidth: 2, pointRadius: currentAggregation === 'day' ? 0 : 3 }});
                donutLabels.push('Account Creation'); donutData.push(totals.account_creation); donutColors.push(colors.blue);
            }}
            if (activeEventTypes.login) {{
                lineDatasets.push({{ label: 'Login', data: aggData.map(d => d.login), borderColor: colors.green, backgroundColor: 'transparent', tension: 0.3, borderWidth: 2, pointRadius: currentAggregation === 'day' ? 0 : 3 }});
                donutLabels.push('Login'); donutData.push(totals.login); donutColors.push(colors.green);
            }}
            if (activeEventTypes.payment) {{
                lineDatasets.push({{ label: 'Payment', data: aggData.map(d => d.payment), borderColor: colors.purple, backgroundColor: 'transparent', tension: 0.3, borderWidth: 2, pointRadius: currentAggregation === 'day' ? 0 : 3 }});
                donutLabels.push('Payment'); donutData.push(totals.payment); donutColors.push(colors.purple);
            }}
            if (activeEventTypes.other) {{
                lineDatasets.push({{ label: 'Other', data: aggData.map(d => d.other), borderColor: colors.orange, backgroundColor: 'transparent', tension: 0.3, borderWidth: 2, pointRadius: currentAggregation === 'day' ? 0 : 3 }});
                donutLabels.push('Other'); donutData.push(totals.other); donutColors.push(colors.orange);
            }}

            // Line Chart
            if (lineChart) lineChart.destroy();
            lineChart = new Chart(document.getElementById('lineChart'), {{
                type: 'line',
                data: {{ labels: aggData.map(d => formatDate(d.date)), datasets: lineDatasets }},
                options: {{
                    responsive: true, maintainAspectRatio: false,
                    interaction: {{ intersect: false, mode: 'index' }},
                    plugins: {{ legend: {{ position: 'top', labels: {{ usePointStyle: true, padding: 16 }} }} }},
                    scales: {{
                        x: {{ grid: {{ display: false }}, ticks: {{ maxTicksLimit: 12 }} }},
                        y: {{ beginAtZero: true, grid: {{ color: 'rgba(0,0,0,0.05)' }}, ticks: {{ callback: v => formatNum(v) }} }}
                    }}
                }}
            }});

            // Donut Chart
            if (donutChart) donutChart.destroy();
            const donutTotal = donutData.reduce((a, b) => a + b, 0);
            donutChart = new Chart(document.getElementById('donutChart'), {{
                type: 'doughnut',
                data: {{ labels: donutLabels, datasets: [{{ data: donutData, backgroundColor: donutColors, borderWidth: 0 }}] }},
                options: {{
                    responsive: true, maintainAspectRatio: false, cutout: '65%',
                    plugins: {{
                        legend: {{ position: 'right', labels: {{ usePointStyle: true, padding: 12 }} }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const value = context.raw;
                                    const percentage = ((value / donutTotal) * 100).toFixed(1);
                                    return `${{context.label}}: ${{formatNum(value)}} (${{percentage}}%)`;
                                }}
                            }}
                        }}
                    }}
                }}
            }});

            // Bar Chart - Monthly
            const monthly = {{}};
            data.forEach(r => {{
                const m = r.date.substring(0, 7);
                if (!monthly[m]) monthly[m] = {{ account_creation: 0, login: 0, payment: 0, other: 0 }};
                monthly[m].account_creation += r.account_creation;
                monthly[m].login += r.login;
                monthly[m].payment += r.payment;
                monthly[m].other += r.other;
            }});
            const months = Object.keys(monthly).sort();
            
            if (activeEventTypes.account_creation) barDatasets.push({{ label: 'Account Creation', data: months.map(m => monthly[m].account_creation), backgroundColor: colors.blue, borderRadius: 4 }});
            if (activeEventTypes.login) barDatasets.push({{ label: 'Login', data: months.map(m => monthly[m].login), backgroundColor: colors.green, borderRadius: 4 }});
            if (activeEventTypes.payment) barDatasets.push({{ label: 'Payment', data: months.map(m => monthly[m].payment), backgroundColor: colors.purple, borderRadius: 4 }});
            if (activeEventTypes.other) barDatasets.push({{ label: 'Other', data: months.map(m => monthly[m].other), backgroundColor: colors.orange, borderRadius: 4 }});

            if (barChart) barChart.destroy();
            barChart = new Chart(document.getElementById('barChart'), {{
                type: 'bar',
                data: {{ labels: months.map(m => new Date(m + '-01').toLocaleDateString('en-US', {{ month: 'short' }})), datasets: barDatasets }},
                options: {{
                    responsive: true, maintainAspectRatio: false,
                    plugins: {{ legend: {{ position: 'top', labels: {{ usePointStyle: true, padding: 12 }} }} }},
                    scales: {{
                        x: {{ grid: {{ display: false }} }},
                        y: {{ beginAtZero: true, grid: {{ color: 'rgba(0,0,0,0.05)' }}, ticks: {{ callback: v => formatNum(v) }} }}
                    }}
                }}
            }});
        }}

        // Initialize - apply URL params first, then update dashboard
        applyUrlParams();
        updateDashboard();
        updateTmxProgress();
    </script>
</body>
</html>'''
    return html

def generate_index_html(all_years):
    """Generate an index page that redirects to the most recent year."""
    most_recent = max(all_years)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=dashboard_{most_recent}.html">
    <title>TMX Dashboard</title>
</head>
<body>
    <p>Redirecting to <a href="dashboard_{most_recent}.html">{most_recent} Dashboard</a>...</p>
</body>
</html>'''
    return html

def main():
    script_dir = Path(__file__).parent
    csv_path = script_dir / 'data.csv'
    
    print("Loading CSV data...")
    years_data = load_csv_data(csv_path)
    
    all_years = list(years_data.keys())
    print(f"Found data for years: {', '.join(sorted(all_years))}")
    
    # Combine all data for TMX progress calculation
    all_data = []
    for year in sorted(years_data.keys()):
        all_data.extend(years_data[year])
    
    # Generate individual year dashboards
    for year, data in years_data.items():
        output_path = script_dir / f'dashboard_{year}.html'
        html = generate_year_html(year, data, all_years, all_data)
        output_path.write_text(html)
        print(f"Generated {output_path.name} ({len(data)} records, {len(html)//1024}KB)")
    
    # Generate index page
    index_path = script_dir / 'index.html'
    index_html = generate_index_html(all_years)
    index_path.write_text(index_html)
    print(f"Generated {index_path.name}")
    
    print("\nDone! Open index.html to start browsing.")

if __name__ == '__main__':
    main()
