#!/usr/bin/env python3
"""
Update TMX Dashboard from Google Sheet.

This script is meant to be run via Goose to pull data from the Google Sheet
and regenerate the dashboard HTML files.

Usage (in Goose):
    "Update the TMX dashboard from the Google Sheet"
    
Goose will:
1. Read data from the Google Sheet using googledrive__read
2. Save it to data.csv
3. Run generate_dashboard.py to create the HTML files
4. Optionally redeploy to Blockcell
"""

SHEET_URL = "https://docs.google.com/spreadsheets/d/1zOQV8sxFnFQRtp5kvZJJv76DQ_3aqxW1-D-bsEfZK8g/edit?gid=637452331#gid=637452331"
BLOCKCELL_SITE = "square-tmx-dashboard"

print(f"""
=== TMX Dashboard Update Instructions ===

To update the dashboard, ask Goose to:

1. Read the Google Sheet:
   googledrive__read(id_or_url="{SHEET_URL}")

2. Save the CSV content to: /Users/alain/Desktop/Vibe/POC Hack Week/TMX dashboard/data.csv

3. Run the generator:
   python3 generate_dashboard.py

4. Deploy to Blockcell:
   blockcell__manage_site(site_name="{BLOCKCELL_SITE}", action="upload", directory_path="/Users/alain/Desktop/Vibe/POC Hack Week/TMX dashboard")

Or simply say: "Update the TMX dashboard from the Google Sheet and deploy to Blockcell"
""")
