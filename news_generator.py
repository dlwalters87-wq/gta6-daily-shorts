
import re
import json
import html
import calendar
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import feedparser

# GTA 6 Daily — News Generator v1.1
# Finds stories and creates REVIEW-ONLY Shorts drafts.

SEARCH_TERMS = [
    '"Grand Theft Auto VI" Rockstar',
    '"GTA 6" gameplay',
    '"GTA 6" release date',
    '"GTA 6" trailer news',
]

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

BLOCKED = [
    "nike", "sneaker", "air force 1",
    "travis scott", "gta online",
    "gta 5", "gta v", "gta 4",
    "gta iv", "mod download",
    "giveaway", "casino",
]

TOPICS = {
    "preload": ["preload", "pre-load", "pre load"],
    "release": ["release date", "launch date",
                "release time", "launch time"],
    "gameplay": ["gameplay", "game mechanics"],
    "trailer": ["trailer", "footage", "teaser"],
    "map": ["map", "leonida", "vice city"],
    "characters": ["jason", "lucia", "character"],
    "features": ["features", "vehicles",
                 "graphics", "open world"],
    "other": [],
}

TOPIC_PRIORITY = {
    "preload": 90,
    "release": 90,
    "gameplay": 100,
    "trailer": 95,
    "map": 75,
    "characters": 75,
    "features": 70,
    "other": 30,
}


def clean(text):
    text = re.sub(r"<[^>]*>", "", text or "")
    return html.unescape(text).strip()


def get_topic(title):
    lower = title.lower()
    for topic, keywords in TOPICS.items():
        if any(word in lower for word in keywords):
            return topic
    return "other"


def get_stories():
    stories = []
    seen = set()

    for term in SEARCH_TERMS:
        url = (
            "https://news.google.com/rss/search?q="
            + quote(term)
            + "&hl=en-US&gl=US&ceid=US:en"
        )

        feed = feedparser.parse(url)

        for entry in feed.entries[:15]:
            title = clean(entry.get("title", ""))
            link = entry.get("link", "")
            lower = title.lower()

            if not title or not link:
                continue

            if any(word in lower for word in BLOCKED):
                continue

            if not any(word in lower for word in [
                "gta 6", "gta vi",
                "grand theft auto vi",
                "rockstar games",
            ]):
                continue

            key = re.sub(r"\W+", "", lower)
            if key in seen:
                continue

            seen.add(key)

            published = entry.get("published_parsed")
            timestamp = (
                calendar.timegm(published)
                if published else 0
            )

            topic = get_topic(title)

            stories.append({
                "headline": title,
                "url": link,
                "published": entry.get("published", ""),
                "timestamp": timestamp,
                "topic": topic,
                "score": TOPIC_PRIORITY[topic],
            })

    return stories


def select_stories(stories, limit=5):
    now = datetime.now(timezone.utc).timestamp()
    recent = []

    for story in stories:
        age_days = (
            (now - story["timestamp"]) / 86400
            if story["timestamp"] else 999
        )

        if age_days > 7 or age_days < -1:
            continue

        story["score"] += max(
            0, int(20 - age_days * 4)
        )
        recent.append(story)

    recent.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    selected = []
    used_topics = set()

    for story in recent:
        if story["topic"] in used_topics:
            continue

        selected.append(story)
        used_topics.add(story["topic"])

        if len(selected) >= limit:
            break

    return selected


def make_script(story):
    topic = story["topic"]
    headline = story["headline"]

    hooks = {
        "preload": "GTA 6 fans, here's a download update!",
        "release": "GTA 6 fans, there's a launch update!",
        "gameplay": "Here's a GTA 6 gameplay story to watch!",
        "trailer": "There's a new GTA 6 trailer headline!",
        "map": "Vice City fans, check this out!",
        "characters": "Here's a GTA 6 character update!",
        "features": "GTA 6 could have something interesting!",
        "other": "Here's a GTA 6 headline making the rounds!",
    }

    narration = (
        f"{hooks[topic]} "
        f"A recent report is titled: {headline}. "
        "That's the headline, not confirmation "
        "of every detail. We're checking the "
        "original source before calling it official. "
        "Follow GTA 6 Daily for verified updates!"
    )

    return {
        "title": headline[:90],
        "topic": topic,
        "narration": narration,
        "source_url": story["url"],
        "published": story["published"],
        "status": "NEEDS FACT CHECK",
        "footage_status": "NEEDS VERIFIED GTA 6 FOOTAGE",
        "approved": False,
        "hashtags": [
            "#GTA6", "#GTAVI",
            "#GrandTheftAuto6", "#Shorts",
        ],
    }


def main():
    print("GTA 6 Daily v1.1 starting...")

    stories = get_stories()
    selected = select_stories(stories)

    drafts = [make_script(s) for s in selected]

    today = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")

    output_file = OUTPUT / f"shorts_{today}.json"

    with open(
        output_file, "w", encoding="utf-8"
    ) as file:
        json.dump(
            drafts, file,
            indent=2, ensure_ascii=False
        )

    print(f"Headlines found: {len(stories)}")
    print(f"Drafts created: {len(drafts)}")
    print(f"Saved: {output_file}")

    for draft in drafts:
        print("-", draft["title"])

    if not drafts:
        print("No suitable recent stories found.")


if __name__ == "__main__":
    main()
