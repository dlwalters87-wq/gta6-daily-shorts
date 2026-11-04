
import os
import re
import json
import html
from datetime import datetime, timezone
from pathlib import Path

import feedparser

# GTA 6 Daily — Free News & Shorts Script Generator
# Drafts only. No automatic publishing.

SEARCH_TERMS = [
    "GTA 6 Rockstar Games",
    "Grand Theft Auto VI gameplay",
    "GTA 6 news updates",
]

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)


def clean_text(text):
    text = re.sub(r"<[^>]+>", "", text or "")
    return html.unescape(text).strip()


def get_news():
    stories = []
    seen = set()

    for term in SEARCH_TERMS:
        query = term.replace(" ", "+")
        url = (
            "https://news.google.com/rss/search"
            f"?q={query}&hl=en-US&gl=US&ceid=US:en"
        )

        feed = feedparser.parse(url)

        for entry in feed.entries[:10]:
            title = clean_text(entry.get("title", ""))
            link = entry.get("link", "")

            key = re.sub(r"\W+", "", title.lower())

            if not title or key in seen:
                continue

            seen.add(key)

            stories.append({
                "headline": title,
                "source_url": link,
                "published": entry.get("published", ""),
            })

    return stories


def make_script(story):
    headline = story["headline"]

    # A headline-based draft, not a verified summary.
    # Do not present the headline as confirmed news.
    narration = (
        f"Here's a GTA 6 story worth checking out! "
        f"The latest headline is: {headline}. "
        "Before jumping to conclusions, let's see "
        "what the original source actually confirms. "
        "We'll keep watching for verified updates. "
        "Follow GTA 6 Daily for more!"
    )

    return {
        "title": headline[:90] + " | GTA 6 Daily",
        "narration": narration,
        "source_url": story["source_url"],
        "published": story["published"],
        "status": "NEEDS FACT CHECK",
        "footage_status": "NOT SELECTED",
        "hashtags": [
            "#GTA6",
            "#GTAVI",
            "#GrandTheftAuto6",
            "#Shorts",
        ],
    }


def main():
    print("GTA 6 Daily: Searching for news...")

    stories = get_news()
    drafts = [make_script(s) for s in stories[:5]]

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = OUTPUT / f"shorts_{today}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(drafts, f, indent=2, ensure_ascii=False)

    print(f"Found {len(stories)} stories.")
    print(f"Created {len(drafts)} draft scripts.")
    print(f"Saved to {filename}")

    if not drafts:
        print("No stories found. Try again later.")


if __name__ == "__main__":
    main()

