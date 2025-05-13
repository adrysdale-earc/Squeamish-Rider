#!/usr/bin/env python3
"""
scraper.py

Scrapes the Insurtech Insights USA agenda page and exports:
  Session Title, Date/Time, Speakers/Presenters, Location
to a CSV.
"""

import argparse
import pandas as pd
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_agenda(url: str):
    with sync_playwright() as p:
        # Launch headless browser
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, 'html.parser')
    sessions = []

    # ——— UPDATE THESE SELECTORS TO MATCH THE LIVE DOM ———
    # Here we look for each “session block” container.
    for entry in soup.select('div.agenda-item, article.session, li.session-item'):
        # 1. Date/Time
        dt = entry.select_one('.session-time, .time, .agenda-time')
        when = dt.get_text(separator=" ", strip=True) if dt else ''

        # 2. Title
        title = entry.select_one('.session-title, h3, .agenda-title')
        title_text = title.get_text(strip=True) if title else ''

        # 3. Speakers / Presenters
        speakers = entry.select('.speaker-name, .presenter')
        speaker_list = [s.get_text(strip=True) for s in speakers]
        speakers_text = "; ".join(speaker_list)

        # 4. Location
        loc = entry.select_one('.session-location, .location')
        loc_text = loc.get_text(strip=True) if loc else ''

        sessions.append({
            'Date/Time': when,
            'Session Title': title_text,
            'Speakers/Presenters': speakers_text,
            'Location': loc_text
        })

    return sessions

def main():
    parser = argparse.ArgumentParser(description="Scrape Insurtech Insights USA agenda → CSV")
    parser.add_argument('--url',
                        default='https://www.insurtechinsights.com/america/agenda/',
                        help='Agenda page URL')
    parser.add_argument('--output',
                        default='agenda.csv',
                        help='Output CSV path')
    args = parser.parse_args()

    data = scrape_agenda(args.url)
    df = pd.DataFrame(data)
    df.to_csv(args.output, index=False)
    print(f"✅  Scraped {len(df)} sessions → {args.output}")

if __name__ == '__main__':
    main()
