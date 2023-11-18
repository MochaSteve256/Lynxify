import discord
from discord.ext import commands
from discord.ui import Button, View
import sqlite3
import time
from datetime import datetime

import bot_token

# set up bot intents
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

# connect to database
conn = sqlite3.connect('database.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, uid INTEGER UNIQUE NOT NULL, birthdate DATE NOT NULL)''')

@bot.event
async def on_ready():
    print(f'Successfully logged in as {bot.user}')
    #await bot.change_presence(activity=discord.Game("Territorial.io"))

@bot.slash_command(description="View your age in days.")
async def dayssincebirth(ctx):
    #await ctx.respond(f"Time: <t:{int(time.time())}:R>")
    user_id = ctx.author.id
    cur.execute("SELECT birthdate FROM users WHERE uid = ?", (user_id,))
    birthdate = cur.fetchone()
    if birthdate is not None:
        birthdate = datetime.strptime(birthdate[0], "%Y-%m-%d %H:%M:%S").date()
        age = (datetime.now().date() - birthdate).days
        if age > 0:
            await ctx.respond(f"You have been alive for {age} days.")
        else:
            await ctx.respond("You haven't been born yet.")
    else:
        await ctx.respond("Your birthday hasn't been set yet.")

@bot.slash_command(description="Set your birthday for the ```dayssincebirth``` command.")
async def setbirthday(ctx, day: int, month: int, year: int):
    user_id = ctx.author.id
    birthdate = datetime(year, month, day)
    cur.execute("INSERT OR REPLACE INTO users (uid, birthdate) VALUES (?, ?)", (user_id, birthdate))
    conn.commit()
    await ctx.respond("Your birthday has been set.")

# run bot
try:
    bot.run(bot_token.token)
except Exception as ex:
    print("Some error occurred:")
    print(ex)