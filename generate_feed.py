import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

URL = "https://werkwarenhuis.nl/project_category/actueel/"
OUTPUT = "feed.xml"

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; WerkwarenhuisRSS/1.0)"
}

print("Werkwarenhuis Actueel ophalen...")

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

fg = FeedGenerator()

fg.id(URL)
fg.title("Werkwarenhuis - Actueel")
fg.description(
    "Onofficiele RSS-feed van de actuele agenda van Werkwarenhuis Den Bosch"
)
fg.link(href=URL, rel="alternate")
fg.language("nl")
fg.lastBuildDate(datetime.now(timezone.utc))

items = []

# Werkwarenhuis gebruikt project-items voor de actuele agenda.
# We zoeken eerst naar de afzonderlijke projectblokken.
selectors = [
    "article",
    ".et_pb_portfolio_item",
    ".project",
    ".et_pb_post"
]

for selector in selectors:
    found = soup.select(selector)
    if found:
        items = found
        print(f"Items gevonden met selector {selector}: {len(items)}")
        break

# Fallback wanneer de site geen duidelijke article-blokken teruggeeft.
if not items:
    print("Geen afzonderlijke projectblokken gevonden.")
    print("Agenda als één feed-item opslaan.")

    main = (
        soup.find("main")
        or soup.find(id="main-content")
        or soup.body
    )

    if not main:
        raise RuntimeError("Agenda-inhoud kon niet worden gevonden.")

    text = " ".join(main.get_text(" ", strip=True).split())

    entry = fg.add_entry()
    entry.id(URL + "#actueel")
    entry.title("Actuele agenda Werkwarenhuis")
    entry.link(href=URL)
    entry.description(text[:4000])

else:
    added = 0
    seen = set()

    for i, item in enumerate(items, 1):

        title_element = item.find(
            ["h1", "h2", "h3", "h4"]
        )

        if title_element:
            title = " ".join(
                title_element.get_text(" ", strip=True).split()
            )
        else:
            title = ""

        text = " ".join(
            item.get_text(" ", strip=True).split()
        )

        # Sla lege of irrelevante blokken over
        if not text or len(text) < 20:
            continue

        if not title:
            title = text[:100]

        link_element = item.find("a", href=True)

        if link_element:
            link = link_element["href"]
        else:
            link = URL

        unique_id = link if link != URL else f"{URL}#item-{i}"

        if unique_id in seen:
            continue

        seen.add(unique_id)

        entry = fg.add_entry()
        entry.id(unique_id)
        entry.title(title)
        entry.link(href=link)
        entry.description(text[:4000])

        added += 1

    print(f"{added} agenda-items toegevoegd")

fg.rss_file(OUTPUT, pretty=True)

print("feed.xml voor Werkwarenhuis succesvol aangemaakt")
