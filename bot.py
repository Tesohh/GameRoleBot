from discord_slash import SlashCommand
from typing import Type
import discord
from discord import channel
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from discord.ext.commands import has_role
from discord.utils import get
import json
import asyncio
from discord.ext import tasks
from rich.console import Console
from secretTokens import BOT_TOKEN
from languages_iten import langs

console = Console()

# intents = discord.Intents.all()
client = commands.Bot(command_prefix="+")
slash = SlashCommand(client, sync_commands=True)

@client.event
async def on_ready():
   print(f"{client.user} e' online.")

@client.event
async def on_guild_join(guild):
	with open(f"guildsets/{guild.id}_sets.json", "w") as f:
		print(f"Sono stato aggiunto al server {guild.name} ID: {guild.id}")
		jsonPre = {"games" : {"overwatch" : ":watch:", "minecraft" : ":b:"}, "lang" : "en"}
		json.dump(jsonPre, f)
		#aggiungi delle impostazioni di default per il server quando il bot entra nel server

def getGuildSettings(gid):
	with open("serverSettings.json", "r+") as f:
		jsonPre = json.load(f)
		return jsonPre[gid]


@slash.slash(description="comando di prova")
async def hello(ctx, tag):
	await ctx.send(f"Ciao! {tag}")

# @slash.slash(description="Aggiungi un gioco alla lista")

@slash.slash(description="Visualizza tutti i giochi disponibili")
async def weplay(ctx, asdddd):
	l = getGuildSettings(ctx.guild.id)["lang"]
	embed = discord.Embed(title=l["hereWePlay"])
	await ctx.send(embed=embed)

client.run(BOT_TOKEN)