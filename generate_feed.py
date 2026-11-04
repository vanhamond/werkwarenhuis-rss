import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin

HOME_URL = "https://www.zinindenbosch.nl/nl/page/home"
BASE_URL = "https://www.zinindenbosch.nl"
OUTPUT_FILE = "feed.xml"

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; ZinInDenBoschRSS/1.0)"
}

print("Zin in Den Bosch ophalen...")

response = requests.get(
    HOME_URL,
    headers=headers,
    timeout=30
)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

articles = []
seen = set()

for link in soup.find_all("a", href=True):
    href = link["href"]

    if "/nl/article/" not in href:
        continue

    url = urljoin(BASE_URL, href)
    url = url.split("?")[0].split("#")[0]

    if url in seen:
        continue

    seen.add(url)

    title = " ".join(
        link.get_text(" ", strip=True).split()
    )

    if not title:
        title = (
            url.split("/")[-1]
            .replace("-", " ")
            .title()
        )

    articles.append(
        {
            "title": title,
            "url": url
        }
    )

print(f"{len(articles)} artikelen gevonden")

if not articles:
    raise RuntimeError(
        "Geen artikelen gevonden. "
        "De structuur van de website is mogelijk gewijzigd."
    )

fg = FeedGenerator()

fg.id(HOME_URL)
fg.title("Zin in Den Bosch")
fg.description(
    "Onofficiele RSS-feed met artikelen van Zin in Den Bosch"
)
fg.link(
    href=HOME_URL,
    rel="alternate"
)
fg.language("nl")

for article in articles:
    entry = fg.add_entry()

    entry.id(article["url"])
    entry.title(article["title"])
    entry.link(
        href=article["url"]
    )

    entry.description(
        'Lees het volledige artikel op '
        'Zin in Den Bosch: '
        f'<a href="{article["url"]}">'
        f'{article["title"]}</a>'
    )

fg.rss_file(
    OUTPUT_FILE,
    pretty=True
)

print(f"{OUTPUT_FILE} succesvol aangemaakt")
