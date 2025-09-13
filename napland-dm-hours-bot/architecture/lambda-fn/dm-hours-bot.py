import discord
from discord.ext import commands
import os

TOKEN = os.getenv('DM_HOURS_DISCORD_BOT_TOKEN')

description = '''A bot to help track DM hours for D&D'''

intents = discord.Intents.default()
intents.members = True
intents.messages_content = True
bot = commands.Bot(
    command_prefix='!', 
    description=description,
    intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')


@bot.command()
async def add_session(ctx, dm_name: str, date: str, hours: float, session_name: str):
    # Here you can add code to process the input and store it as needed
    await ctx.send(f'Session added: DM: {dm_name}, Date: {date}, Hours: {hours}, Session: {session_name}')


bot.run(TOKEN)