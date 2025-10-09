from discord import Bot, Intents
import random
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Date
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select, insert, update, delete

# Fix for audioop
import sys
import types

sys.modules['audioop'] = types.ModuleType('audioop')



import bot_creds

# --- DATABASE CONFIG ---
# Example: replace with your own credentials
DATABASE_URL = bot_creds.db_url

# create engine and metadata
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# define users table
users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('uid', Integer, unique=True, nullable=False),
    Column('birthdate', Date, nullable=False)
)

# create table if it doesn't exist
metadata.create_all(engine)

# --- DISCORD BOT SETUP ---
intents = Intents.default()
intents.message_content = True
bot = Bot(intents=intents)

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f"Successfully logged in as '{bot.user}' (ID: {bot.user.id}), in {len(bot.guilds)} guilds:") # type: ignore
    for guild in bot.guilds:
        print(f"- {guild.id}: {guild.name}")

# --- COMMANDS ---
@bot.slash_command(description="View your age in days.")
async def dayssincebirth(ctx):
    user_id = ctx.author.id
    with engine.connect() as conn:
        query = select(users.c.birthdate).where(users.c.uid == user_id)
        result = conn.execute(query).fetchone()
        if result:
            birthdate = result[0]
            age = (datetime.now().date() - birthdate.date()).days
            if age > 0:
                await ctx.respond(f"You have been alive for {age} days.")
            else:
                await ctx.respond("You haven't been born yet.")
        else:
            await ctx.respond("Your birthday hasn't been set yet.")
    print(f"User {user_id} viewed their age in days.")

@bot.slash_command(description="Set your birthday for the 'dayssincebirth' command.")
async def setbirthday(ctx, day: int, month: int, year: int):
    user_id = ctx.author.id
    try:
        birthdate = datetime(year, month, day).date()
    except ValueError:
        await ctx.respond("Invalid date. Please enter a valid date in the format 'DD MM YYYY'.")
        return

    with engine.connect() as conn:
        try:
            # insert or update (upsert)
            stmt = insert(users).values(uid=user_id, birthdate=birthdate).on_conflict_do_update( # type: ignore
                index_elements=[users.c.uid],
                set_={"birthdate": birthdate}
            )
            conn.execute(stmt)
            conn.commit()
            await ctx.respond("Your birthday has been set.")
            print(f"User {user_id} set their birthday.")
        except IntegrityError:
            await ctx.respond("Failed to set your birthday. Something went wrong.")

@bot.slash_command(description="Delete all your data from this bot's database.")
async def wipe(ctx):
    user_id = ctx.author.id
    with engine.connect() as conn:
        stmt = delete(users).where(users.c.uid == user_id)
        conn.execute(stmt)
        conn.commit()
    await ctx.respond("Your data has been deleted from the database.")
    print(f"User {user_id} wiped their data.")

# RANDOM COMMANDS (hot take, fact, corporate buzz)
async def send_random_from_file(ctx, filename):
    with open(filename, 'r') as f:
        items = f.readlines()
    item = items[random.randint(0, len(items)-1)].strip()
    await ctx.respond(item)

@bot.slash_command(description="Get a random hot take.")
async def hottake(ctx):
    await send_random_from_file(ctx, 'hottakes.txt')
    print("Random hottake command used.")

@bot.slash_command(description="Get a random fact.")
async def fact(ctx):
    await send_random_from_file(ctx, 'facts.txt')
    print("Random fact command used.")

@bot.slash_command(description="Get a random corporate buzz.")
async def corporatebuzz(ctx):
    await send_random_from_file(ctx, 'corporatebsbuzz.txt')
    print("Random corporate buzz command used.")

# --- RUN BOT ---
try:
    bot.run(bot_creds.token)
except Exception as ex:
    print("Some error occurred:")
    print(ex)
