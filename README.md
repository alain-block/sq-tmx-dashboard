# Square TMX Dashboard

A static web dashboard for visualizing ThreatMetrix (TMX) event analytics for Square. The dashboard displays event data across four categories: Account Creation, Login, Payment, and Other transactions.

## 🌐 Live Dashboard

**https://blockcell.sqprod.co/sites/square-tmx-dashboard/**

## 🎯 Purpose

This dashboard was created to track and analyze TMX event data for Square's integration with ThreatMetrix. Key features include:

- **Multi-year data visualization** - View event trends across 2024, 2025, and 2026
- **Interactive charts** - Line chart (trends), donut chart (distribution), and bar chart (monthly totals)
- **Event type filtering** - Toggle visibility of Account Creation, Login, Payment, and Other events
- **Flexible aggregation** - View data by Day, Week, or Month
- **TMX Agreement Progress Tracker** - Tracks cumulative events since April 1, 2025 toward the 100M event target (excluding "Other" events), with estimated completion date

## 📁 Project Structure

```
├── index.html              # Redirects to the most recent year dashboard
├── dashboard_2024.html     # Dashboard for 2024 data
├── dashboard_2025.html     # Dashboard for 2025 data
├── dashboard_2026.html     # Dashboard for 2026 data
├── generate_dashboard.py   # Python script to regenerate dashboards from CSV
├── data.csv                # Raw event data from Google Sheet
├── data_2024.json          # Year-specific JSON data
├── data_2025.json
├── data_2026.json
└── README.md
```

## 🚀 Running the Application

### Prerequisites

- Python 3.x
- A modern web browser (Chrome, Firefox, Safari, Edge)

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/alain-block/sq-tmx-dashboard.git
   cd sq-tmx-dashboard
   ```

2. **Open the dashboard locally:**
   
   Simply open `index.html` in your browser, or open a specific year:
   ```bash
   open dashboard_2026.html
   ```

3. **Regenerate dashboards from CSV:**
   
   If you've updated `data.csv`, regenerate all HTML dashboards:
   ```bash
   python3 generate_dashboard.py
   ```

### Dashboard Controls

- **Year Navigation** - Click year links (2024, 2025, 2026) to switch between years
- **Aggregation Toggle** - Select Day, Week, or Month to change data grouping
- **Event Type Filters** - Check/uncheck event types to show/hide them in charts
- **Settings Persistence** - Your aggregation and filter settings are preserved when navigating between years

## 🔄 Weekly Update Process

The dashboard is updated weekly with new data from the Google Sheet. Follow these steps:

### Step 1: Export Data from Google Sheet

1. Open the [TMX Events Google Sheet](https://docs.google.com/spreadsheets/d/1mS0s-MNKjPjLmGj3BVlT5NQXP8AqxMEHZrZVk9Dn3Hs)
2. Export as CSV: **File → Download → Comma Separated Values (.csv)**
3. Save/replace as `data.csv` in the project folder

### Step 2: Regenerate Dashboards

```bash
cd "/Users/alain/Desktop/Vibe/POC Hack Week/TMX dashboard"
python3 generate_dashboard.py
```

This will:
- Parse the CSV data
- Split data by year
- Generate updated JSON files (`data_2024.json`, `data_2025.json`, `data_2026.json`)
- Create new HTML dashboards with embedded data
- Update `index.html` to redirect to the most recent year

### Step 3: Commit to GitHub

```bash
git add .
git commit -m "Weekly update: Added data through [DATE]"
git push
```

### Step 4: Deploy to Blockcell

Use Goose or the Blockcell CLI to upload the updated files:
```
Upload directory to Blockcell site: square-tmx-dashboard
```

The updated dashboard will be live at:
https://blockcell.sqprod.co/sites/square-tmx-dashboard/

## 📊 Data Format

The `data.csv` file should have the following format:

```csv
Date,Events,Event Type
2024-06-15,12345,account_creation
2024-06-15,67890,login
2024-06-15,11111,payment
2024-06-15,2222,transaction_other
```

- **Date** - Supports formats: `YYYY-MM-DD`, `M/D/YY`, `M/D/YYYY`
- **Events** - Number of events (integer)
- **Event Type** - One of: `account_creation`, `login`, `payment`, `transaction_other`

## 🛠 Technologies Used

- **HTML/CSS/JavaScript** - Frontend
- **Chart.js** - Interactive charts
- **Python** - Dashboard generation script
- **Blockcell** - Static site hosting

## 📝 License

Internal use only - Square, Inc.
