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

for i, table in enumerate(tables[:3], 1):  # Check first 3 tables
    print(f"Table {i}:")
    print("-" * 80)

    # Check parent elements for team name
    parent = table.parent
    for _ in range(5):  # Go up 5 levels
        if parent:
            # Look for headings
            heading = parent.find(['h1', 'h2', 'h3', 'h4', 'h5'])
            if heading:
                print(f"  Found heading in parent: {heading.get_text(strip=True)}")
                break
            parent = parent.parent

    # Check preceding siblings
    prev_sibling = table.find_previous_sibling(['h1', 'h2', 'h3', 'h4', 'h5', 'div'])
    if prev_sibling:
        print(f"  Previous sibling: {prev_sibling.name} - {prev_sibling.get_text(strip=True)[:80]}")

    # Check for any data attributes
    attrs = table.attrs
    if attrs:
        print(f"  Table attributes: {attrs}")

    print()
