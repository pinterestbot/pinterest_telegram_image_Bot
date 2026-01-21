import asyncio
import feedparser
import requests
from io import BytesIO
from telegram import Bot

BOT_TOKEN = "7989471579:AAE6DIBDHwlbtNKYxWVJZ6D_52Cq6sSNZkw"
CHANNEL_USERNAME = "@AnimeLifeHackProducts"
PINTEREST_RSS = "https://www.pinterest.com/allwetmovie0031/anime-best-figures-india-2026.rss"
CHECK_INTERVAL = 300  # 5 min
DATA_FILE = "pins.json"

bot = Bot(token=BOT_TOKEN)

# Load old pins
def load_old_pins():
    try:
        import json
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_pins(pins):
    import json
    with open(DATA_FILE, "w") as f:
        json.dump(pins, f)

# Fetch new pins from RSS
def fetch_pins():
    feed = feedparser.parse(PINTEREST_RSS)
    pins = []
    for entry in feed.entries[:5]:
        # RSS me sometimes thumbnail or media_content available hota hai
        # Use first image or None
        img_url = None
        if 'media_content' in entry:
            img_url = entry.media_content[0]['url']
        elif 'media_thumbnail' in entry:
            img_url = entry.media_thumbnail[0]['url']

        pins.append({
            "title": entry.title,
            "link": entry.link,
            "image": img_url
        })
    return pins

# Post pin to Telegram
async def post_to_telegram(pin):
    caption = f"🔥 NEW PIN ALERT 🔥\n\n📌 {pin['title']}\n👉 View on Pinterest: {pin['link']}"
    try:
        if pin["image"]:
            # Download image and send
            response = requests.get(pin["image"])
            response.raise_for_status()
            image_bytes = BytesIO(response.content)
            await bot.send_photo(chat_id=CHANNEL_USERNAME, photo=image_bytes, caption=caption)
        else:
            # Only caption if image not available
            await bot.send_message(chat_id=CHANNEL_USERNAME, text=caption)
        print(f"✅ Posted: {pin['title']}")
    except Exception as e:
        print(f"⚠️ Error posting: {e}")

# Main loop
async def main():
    print("🤖 Pinterest → Telegram bot started...")
    old_pins = load_old_pins()

    while True:
        pins = fetch_pins()
        for pin in pins:
            if pin["link"] not in old_pins:
                await post_to_telegram(pin)
                old_pins.append(pin["link"])
                save_pins(old_pins)
                await asyncio.sleep(5)
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())