import requests
from bs4 import BeautifulSoup

url = "https://www.nfl.com/injuries/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

tables = soup.find_all('table', class_='d3-o-table')
first_table = tables[0]

print("Looking for links before first table:")
print("=" * 80)

# Find all <a> tags before the first table
all_links = []
for element in first_table.find_all_previous(['a']):
    href = element.get('href', '')
    text = element.get_text(strip=True)
    classes = element.get('class', [])
    all_links.append((text, href, classes))
    if len(all_links) >= 20:  # Just get first 20
        break

for i, (text, href, classes) in enumerate(reversed(all_links[-10:]), 1):
    print(f"{i}. Text: {text[:50]:<50} | Href: {href[:60]:<60} | Classes: {classes}")
