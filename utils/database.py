import aiosqlite
import logging

logger = logging.getLogger(__name__)

DB_PATH = 'bot_database.db'

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS credits
                            (user_id TEXT PRIMARY KEY, amount INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS current_song
                            (guild_id TEXT PRIMARY KEY, song_name TEXT)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS language_settings
                            (guild_id TEXT PRIMARY KEY, language TEXT)''')
        await db.commit()

async def add_credits(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''INSERT OR REPLACE INTO credits (user_id, amount)
                            VALUES (?, coalesce((SELECT amount FROM credits WHERE user_id = ?) + ?, ?))''',
                         (str(user_id), str(user_id), amount, amount))
        await db.commit()

async def get_credits(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT amount FROM credits WHERE user_id = ?', (str(user_id),)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def update_song_status(guild_id, song_name):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('INSERT OR REPLACE INTO current_song (guild_id, song_name) VALUES (?, ?)',
                         (str(guild_id), song_name))
        await db.commit()

async def set_language(guild_id, language):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('INSERT OR REPLACE INTO language_settings (guild_id, language) VALUES (?, ?)',
                         (str(guild_id), language))
        await db.commit()

async def get_language(guild_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT language FROM language_settings WHERE guild_id = ?', (str(guild_id),)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 'en'