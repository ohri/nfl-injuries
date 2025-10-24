import requests
from bs4 import BeautifulSoup
import csv
import re
import os

def scrape_nfl_injuries():
    url = "https://www.nfl.com/injuries/"

    # Download players.csv if it doesn't exist
    if not os.path.exists('players.csv'):
        print("players.csv not found. Downloading from nflverse...")
        players_url = "https://github.com/nflverse/nflverse-data/releases/download/players/players.csv"
        try:
            response = requests.get(players_url)
            response.raise_for_status()
            with open('players.csv', 'wb') as f:
                f.write(response.content)
            print("Successfully downloaded players.csv")
        except Exception as e:
            print(f"Failed to download players.csv: {e}")
            print("Continuing without player data...")

    # Load players.csv and create a mapping from player name to gsis_id
    print("Loading players.csv...")
    player_name_to_gsis = {}
    try:
        with open('players.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                display_name = row['display_name']
                gsis_id = row['gsis_id']
                if display_name and gsis_id:
                    player_name_to_gsis[display_name] = gsis_id
        print(f"Loaded {len(player_name_to_gsis)} players from players.csv")
    except FileNotFoundError:
        print("Warning: players.csv not found. GSIS IDs will be empty.")
    except Exception as e:
        print(f"Warning: Error reading players.csv: {e}. GSIS IDs will be empty.")

    # Set headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Fetching NFL injuries page...")
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    injuries_data = []

    # Find all injury tables
    tables = soup.find_all('table', class_='d3-o-table')

    print(f"Found {len(tables)} tables")

    for table in tables:
        # Find team name - look for preceding team link (has specific class)
        team_name = "Unknown"
        team_link = table.find_previous('a', class_='nfl-c-matchup-strip__team-fullname')
        if team_link:
            team_name = team_link.get_text(strip=True)

        # Find all player rows (skip header row)
        tbody = table.find('tbody')
        if not tbody:
            continue

        rows = tbody.find_all('tr')

        for row in rows:
            cells = row.find_all('td')

            # Expected structure: Player, Position, Injuries, Practice Status, Game Status
            if len(cells) >= 5:
                player_name = cells[0].get_text(strip=True)
                position = cells[1].get_text(strip=True)
                # injuries = cells[2].get_text(strip=True)  # We don't need this per requirements
                # practice_status = cells[3].get_text(strip=True)  # We don't need this either
                game_status = cells[4].get_text(strip=True)

                # Only add if we have a player name and a game status
                if player_name and game_status:
                    # Look up gsis_id from players.csv
                    gsis_id = player_name_to_gsis.get(player_name, '')

                    injuries_data.append({
                        'gsis_id': gsis_id,
                        'team': team_name,
                        'position': position,
                        'player_name': player_name,
                        'game_status': game_status
                    })

    # Write to SQL file
    if injuries_data:
        output_file = 'nfl_injuries.sql'
        with open(output_file, 'w', encoding='utf-8') as sqlfile:
            for record in injuries_data:
                gsis_id = record['gsis_id']
                game_status = record['game_status'][0] if record['game_status'] else ''
                sql = f"update tblplayers set injurystatus='{game_status}' where gsis='{gsis_id}';\n"
                sqlfile.write(sql)

        print(f"Successfully scraped {len(injuries_data)} injury records")
        print(f"Data saved to {output_file}")

        # Report how many players were matched
        matched = sum(1 for d in injuries_data if d['gsis_id'])
        print(f"Matched {matched}/{len(injuries_data)} players to GSIS IDs")
    else:
        print("No injury data found. The page structure may have changed.")
        print("Saving raw HTML for inspection...")
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("HTML saved to page_source.html for manual inspection")

if __name__ == "__main__":
    scrape_nfl_injuries()
