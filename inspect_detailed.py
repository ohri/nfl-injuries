import requests
from bs4 import BeautifulSoup

url = "https://www.nfl.com/injuries/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

tables = soup.find_all('table')
print(f"Found {len(tables)} tables\n")

# Look at first table in detail
first_table = tables[0]
print("Full structure around first table:")
print("=" * 80)

# Get the container div
container = first_table.find_parent('div', class_=True)
if container:
    print(f"Container classes: {container.get('class')}")
    print(f"Container text (first 200 chars): {container.get_text(strip=True)[:200]}\n")

    # Look for all text content in container before the table
    for child in container.children:
        if child == first_table:
            break
        if hasattr(child, 'get_text'):
            text = child.get_text(strip=True)
            if text:
                print(f"Before table - {child.name}: {text}")

print("\n" + "=" * 80)

# Check for team logo or team link
team_link = first_table.find_previous(['a', 'img', 'span'], class_=lambda x: x and ('team' in ' '.join(x).lower() if isinstance(x, list) else 'team' in x.lower()))
if team_link:
    print(f"\nFound team element: {team_link.name} - {team_link.get('alt') or team_link.get('title') or team_link.get_text(strip=True)}")

# Check caption
caption = first_table.find('caption')
if caption:
    print(f"\nTable caption: {caption.get_text(strip=True)}")

# Look at tbody structure
tbody = first_table.find('tbody')
if tbody:
    # Check if first row might be team name
    first_row = tbody.find('tr')
    if first_row:
        cells = first_row.find_all(['td', 'th'])
        print(f"\nFirst row cells ({len(cells)}): {[c.get_text(strip=True) for c in cells]}")
        print(f"First row classes: {first_row.get('class')}")

        # Check if row has colspan (might be team header)
        for cell in cells:
            if cell.get('colspan'):
                print(f"Found cell with colspan: {cell.get_text(strip=True)}")
