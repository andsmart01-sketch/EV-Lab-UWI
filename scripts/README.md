# Weekly Data Update

Run every Wednesday after Petrojam publishes new prices (usually by midday):

    cd ev-lab-repo
    python scripts/update_weekly.py

First-time setup:

    pip install playwright requests
    playwright install chromium

What it does:
- Fetches the live USD/JMD exchange rate from open.er-api.com
- Scrapes the latest Petrojam pump prices using a headless Chromium browser
- Appends new prices to the data/Fuel_Prices CSV (skips if already present)
- Writes data/live_config.json with the exchange rate and last update timestamp

After running, restart the dashboard with `python dashboard/app.py` to load the new data.

If the scrape fails (Petrojam may change their page layout):
- Visit https://petrojam.com/price-schedule
- Note the prices for 87-octane, 90-octane, and Auto Diesel
- Add a row manually to the CSV in data/
