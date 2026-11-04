
import asyncio
import json
from pathlib import Path

import edge_tts

# GTA 6 Daily — AI Voice Generator v1.0

VOICE = "en-US-GuyNeural"
RATE = "+8%"
PITCH = "+0Hz"

OUTPUT = Path("output")
AUDIO = Path("audio")
AUDIO.mkdir(exist_ok=True)


async def generate_voice(text, filename):
    speech = edge_tts.Communicate(
        text,
        VOICE,
        rate=RATE,
        pitch=PITCH,
    )
    await speech.save(str(filename))


async def main():
    files = sorted(OUTPUT.glob("shorts_*.json"))

    if not files:
        print("No script drafts found.")
        return

    latest = files[-1]

    with open(latest, encoding="utf-8") as f:
        scripts = json.load(f)

    print(f"Loaded {len(scripts)} drafts.")

    for index, script in enumerate(scripts, start=1):
        text = script.get("narration", "").strip()

        if not text:
            continue

        filename = AUDIO / f"gta6_short_{index}.mp3"

        print(f"Generating voice {index}...")

        try:
            await generate_voice(text, filename)
            print(f"Saved: {filename}")
        except Exception as error:
            print(f"Voice {index} failed: {error}")


if __name__ == "__main__":
    asyncio.run(main())
