import os
import asyncio
from telethon import TelegramClient, events

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

client = TelegramClient('tagger_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(pattern=r"^/(tagall|all)(?:\s+(.*))?"))
async def tag_all(event):
    if event.is_private:
        await event.reply("Ye command sirf groups me kaam karti hai!")
        return

    msg_extra = event.pattern_match.group(2) or "Dhyan dein sabhi!"
    status_msg = await event.reply("Tag karna shuru kiya ja raha hai...")

    mentions = []
    async for user in client.iter_participants(event.chat_id):
        if user.bot:
            continue
        first_name = user.first_name or "Member"
        mentions.append(f"[{first_name}](tg://user?id={user.id})")

    chunk_size = 5
    for i in range(0, len(mentions), chunk_size):
        chunk = mentions[i:i + chunk_size]
        text = f"📢 **{msg_extra}**\n\n" + " ".join(chunk)
        await event.respond(text)
        await asyncio.sleep(2)

    await status_msg.delete()

print("Tagger Bot live ho chuka hai!")
client.run_until_disconnected()
