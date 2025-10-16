import requests
from bs4 import BeautifulSoup

url = "https://www.nfl.com/injuries/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the first table and print its structure
tables = soup.find_all('table')
print(f"Found {len(tables)} tables\n")

if tables:
    first_table = tables[0]
    print("First table structure:")
    print("=" * 80)

    # Check for headers
    headers_row = first_table.find('thead') or first_table.find('tr')
    if headers_row:
        headers = [th.get_text(strip=True) for th in headers_row.find_all(['th', 'td'])]
        print(f"Headers: {headers}\n")

    # Print first 5 data rows
    rows = first_table.find_all('tr')[1:6]  # Skip header row
    for i, row in enumerate(rows, 1):
        cells = row.find_all(['td', 'th'])
        cell_texts = [cell.get_text(strip=True) for cell in cells]
        print(f"Row {i}: {cell_texts}")

    print("\n" + "=" * 80)

    # Check for any team identifiers
    team_elements = first_table.find_all(['div', 'span', 'h2', 'h3'], class_=True)
    print(f"\nFound {len(team_elements)} potential team elements")
    if team_elements:
        print("First few team-related elements:")
        for elem in team_elements[:5]:
            print(f"  {elem.name} class={elem.get('class')}: {elem.get_text(strip=True)[:50]}")
