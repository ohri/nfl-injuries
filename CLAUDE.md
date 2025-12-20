# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an NFL injury data scraper that fetches current injury reports from nfl.com/injuries and generates SQL UPDATE statements to sync injury statuses with a database table named `tblplayers`.

## Core Architecture

### Main Scraper (`scrape_nfl_injuries.py`)

The primary script that:
1. Auto-downloads `players.csv` from nflverse if not present locally
2. Loads player data to map display names to GSIS IDs
3. Scrapes injury tables from nfl.com/injuries using BeautifulSoup
4. Extracts team name, player name, position, and game status for each injured player
5. Generates SQL UPDATE statements that set `injurystatus` field to first character of game status ('Q', 'O', 'D', etc.)
6. Writes output to `nfl_injuries.sql`

**Key data flow:**
- Players.csv provides the GSIS ID lookup (player display_name → gsis_id)
- **Only current players are matched** - filters for GSIS IDs starting with "00-" (old players have IDs like "WIL384489")
- HTML parsing finds tables with class `d3-o-table`
- Team names are extracted from preceding `<a>` tags with class `nfl-c-matchup-strip__team-fullname`
- Each table row contains: Player | Position | Injuries | Practice Status | Game Status
- Only gsis_id and game_status[0] are used in final SQL output

**Output format:**
```sql
update tblplayers set injurystatus='Q' where gsis='00-0036616';
```

### Inspection Scripts

Helper scripts for debugging HTML structure when the scraper breaks due to NFL.com page changes:
- `inspect_page.py` - Examines table structure and headers
- `inspect_teams.py` - Checks parent elements and siblings for team identification
- `inspect_detailed.py` - Analyzes container structure and team elements
- `inspect_links.py` - Inspects links preceding tables to find team names

## Running the Scraper

```bash
python scrape_nfl_injuries.py
```

**Expected output:**
- Downloads players.csv if missing (from nflverse GitHub releases)
- Prints progress: tables found, players loaded, matches made
- Writes SQL statements to `nfl_injuries.sql`
- Reports match rate (e.g., "Matched 120/123 players to GSIS IDs")

## Database Schema

The scraper expects a database table with this structure:
- Table: `tblplayers`
- Key field: `gsis` (GSIS player ID, format: '00-0036616')
- Updated field: `injurystatus` (single character: 'Q', 'O', 'D', etc.)

## Dependencies

- `requests` - HTTP requests to NFL.com and nflverse
- `beautifulsoup4` - HTML parsing
- `csv` (stdlib) - Reading players.csv

Install with: `pip install requests beautifulsoup4`

## Key HTML Selectors

When NFL.com changes their page structure, update these selectors in `scrape_nfl_injuries.py`:
- Injury tables: `table.d3-o-table`
- Team name: `a.nfl-c-matchup-strip__team-fullname` (preceding sibling)
- Table structure: `tbody > tr > td` (5 cells per row)

## Player Data Source

Players.csv is auto-downloaded from:
https://github.com/nflverse/nflverse-data/releases/download/players/players.csv

This file is gitignored but will be fetched on first run. It contains the authoritative mapping of player names to GSIS IDs.

**GSIS ID Format:**
- Current players: `00-0040735` (starts with "00-")
- Old players: `WIL384489` (legacy format)
- The scraper only matches current players to avoid updating retired player records
