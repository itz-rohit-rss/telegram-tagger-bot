import os
import random
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantsRecent

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))  # Aapka numeric Telegram User ID

client = TelegramClient('tagger_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Active processes track karne ke liye
active_tagging = {}
active_games = {}
registered_groups = set()

# --- GAMES DATA ---
TYPING_WORDS = [
    "TELEGRAM", "DEVELOPER", "PYTHON", "INTERNET", "SECURITY", 
    "ALGORITHM", "DATABASE", "APPLICATION", "COMPUTER", "PROGRAMMING"
]

GUESS_WORDS = {
    "APPLE": "🍎 Ek laal rang ka phal",
    "PYTHON": "🐍 Ek programming language aur ek saap ka naam",
    "EARTH": "🌍 Hum jis grah par rehte hain",
    "CRICKET": "🏏 Bharat ka sabse pasandeeda khel",
    "CHANDRAYAAN": "🚀 Bharat ka Moon mission"
}

RIDDLES = [
    {"q": "Aisi kaunsi cheez hai jo sookhne par 1kg, geeli par 2kg aur jal jaye toh 3kg hoti hai?", "a": "sulfur"},
    {"q": "Aisa kaunsa room hai jisme na koi darwaza hota hai na khidki?", "a": "mushroom"},
    {"q": "Aisi kaunsi cheez hai jo subah 4 tango par, dopahar ko 2 par aur shaam ko 3 par chalti hai?", "a": "insan"}
]

# --- 1. SINGLE SINGLE TAGGER (/tag & /single) ---
@client.on(events.NewMessage(pattern=r"^/(tag|single)(?:\s+(.*))?"))
async def single_tagger(event):
    if event.is_private:
        await event.reply("Ye command sirf groups me kaam karti hai!")
        return

    chat_id = event.chat_id
    registered_groups.add(chat_id)
    if active_tagging.get(chat_id):
        await event.reply("⚠️ Tagging process pehle se chal rahi hai! Rokne ke liye `/cancel` use karein.")
        return

    custom_text = event.pattern_match.group(2)
    active_tagging[chat_id] = True

    async for user in client.iter_participants(chat_id):
        if not active_tagging.get(chat_id):
            break
        if user.bot:
            continue
        
        name = user.first_name or "Member"
        mention = f"[{name}](tg://user?id={user.id})"
        msg = f"{custom_text} {mention}" if custom_text else mention
        
        await event.respond(msg)
        await asyncio.sleep(2)

    active_tagging[chat_id] = False

# --- 2. 5-5 BATCH TAGGER (/tagall & /all) ---
@client.on(events.NewMessage(pattern=r"^/(tagall|all)(?:\s+(.*))?"))
async def batch_tagger(event):
    if event.is_private:
        await event.reply("Ye command sirf groups me kaam karti hai!")
        return

    chat_id = event.chat_id
    registered_groups.add(chat_id)
    if active_tagging.get(chat_id):
        await event.reply("⚠️ Tagging process pehle se chal rahi hai! Rokne ke liye `/cancel` use karein.")
        return

    custom_text = event.pattern_match.group(2)
    active_tagging[chat_id] = True

    mentions = []
    async for user in client.iter_participants(chat_id):
        if user.bot:
            continue
        name = user.first_name or "Member"
        mentions.append(f"[{name}](tg://user?id={user.id})")

    # 5-5 members ka batch
    for i in range(0, len(mentions), 5):
        if not active_tagging.get(chat_id):
            break
        chunk = mentions[i:i + 5]
        chunk_str = " ".join(chunk)
        
        msg = f"{custom_text}\n\n{chunk_str}" if custom_text else chunk_str
        await event.respond(msg)
        await asyncio.sleep(3)

    active_tagging[chat_id] = False

# Tagging stop karne ke liye
@client.on(events.NewMessage(pattern=r"^/cancel$"))
async def cancel_tagging(event):
    chat_id = event.chat_id
    if active_tagging.get(chat_id):
        active_tagging[chat_id] = False
        await event.reply("🛑 Tagging process rok di gayi hai.")
    else:
        await event.reply("Koi active tagging nahi chal rahi hai.")

# --- 3. FIVE DIFFERENT GAMES ---

# Game 1: Fast Typing
@client.on(events.NewMessage(pattern=r"^/typegame$"))
async def typing_game(event):
    target = random.choice(TYPING_WORDS)
    active_games[event.chat_id] = {"type": "type", "ans": target.lower()}
    await event.respond(f"⚡ **Fast Typing Challenge!**\n\nSabse pehle ye word type karke bhejo:\n👉 `{target}`")

# Game 2: Guess The Word (Clue ke sath)
@client.on(events.NewMessage(pattern=r"^/guesstheword$"))
async def guess_word_game(event):
    word, hint = random.choice(list(GUESS_WORDS.items()))
    active_games[event.chat_id] = {"type": "guess", "ans": word.lower()}
    await event.respond(f"🧩 **Guess The Word!**\n\nHint: **{hint}**\nWord ki length: **{len(word)} letters**\nJaldi sahi word guess karein!")

# Game 3: Word Scramble
@client.on(events.NewMessage(pattern=r"^/scramble$"))
async def scramble_game(event):
    word = random.choice(TYPING_WORDS)
    scrambled = "".join(random.sample(word, len(word)))
    active_games[event.chat_id] = {"type": "scramble", "ans": word.lower()}
    await event.respond(f"🔀 **Word Scramble!**\n\nIs ulti-pulti spelling ko theek karein:\n👉 `{scrambled}`")

# Game 4: Math Quiz
@client.on(events.NewMessage(pattern=r"^/mathquiz$"))
async def math_game(event):
    n1 = random.randint(10, 99)
    n2 = random.randint(5, 50)
    ans = n1 + n2
    active_games[event.chat_id] = {"type": "math", "ans": str(ans)}
    await event.respond(f"🔢 **Quick Math Quiz!**\n\nBatao: **{n1} + {n2} = ?**")

# Game 5: Paheli (Riddle)
@client.on(events.NewMessage(pattern=r"^/riddle$"))
async def riddle_game(event):
    riddle = random.choice(RIDDLES)
    active_games[event.chat_id] = {"type": "riddle", "ans": riddle["a"].lower()}
    await event.respond(f"🤔 **Dimagi Paheli!**\n\n{riddle['q']}\n\nJawab likh kar bhejo!")

# Common Answer Checker for Games
@client.on(events.NewMessage)
async def check_game_answer(event):
    chat_id = event.chat_id
    if chat_id not in active_games or not event.text:
        return
    
    expected = active_games[chat_id]["ans"]
    if event.text.strip().lower() == expected:
        user = await event.get_sender()
        name = user.first_name or "Member"
        del active_games[chat_id]
        await event.reply(f"🎉 **Shaandaar [{name}](tg://user?id={user.id})!** Aapka jawab bilkul sahi tha!")

# --- 4. SUDOLIST (OWNER PROFILE) ---
@client.on(events.NewMessage(pattern=r"^/sudolist$"))
async def sudo_list(event):
    if OWNER_ID == 0:
        await event.reply("⚠️ OWNER_ID set nahi hai. Kripya Koyeb me OWNER_ID variable daalein.")
        return
    
    try:
        owner = await client.get_entity(OWNER_ID)
        username = f"@{owner.username}" if owner.username else "No Username"
        text = (
            f"👑 **BOT SUDO / OWNER PROFILE** 👑\n\n"
            f"👤 **Name:** [{owner.first_name}](tg://user?id={owner.id})\n"
            f"🆔 **User ID:** `{owner.id}`\n"
            f"🔗 **Username:** {username}\n"
            f"⚡ **Role:** Permanent Super Admin / Sudo"
        )
    except Exception:
        text = f"👑 **BOT SUDO / OWNER** 👑\n\n🆔 **Owner ID:** `{OWNER_ID}`\n⚡ **Access:** Full Controller"

    await event.reply(text)

# --- 5. BROADCAST (ONLY OWNER ACCESS) ---
@client.on(events.NewMessage(pattern=r"^/broadcast(?:\s+(.*))?"))
async def broadcast(event):
    # Sirf Owner allow hoga
    if event.sender_id != OWNER_ID:
        await event.reply("❌ **Access Denied:** Ye command sirf bot ka Owner chala sakta hai!")
        return

    msg = event.pattern_match.group(1)
    if not msg:
        await event.reply("Kripya message bhi likhein!\nExample: `/broadcast Sabhi dhyan dein`")
        return

    status = await event.reply("📢 Broadcast shuru kiya ja raha hai...")
    count = 0
    for chat_id in list(registered_groups):
        try:
            await client.send_message(chat_id, f"📢 **Broadcast from Owner:**\n\n{msg}")
            count += 1
            await asyncio.sleep(1)
        except Exception:
            pass

    await status.edit(f"✅ Broadcast complete! Total **{count}** groups me message deliver hua.")

print("Upgraded Tagger + Games + Sudo Bot Started!")
client.run_until_disconnected()
    
