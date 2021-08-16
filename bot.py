from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType
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
	try:
		l = langs["it"] #! DA CAMBIARE IN EN

		managerRole = await guild.create_role(name="LFG Manager Manager")
		welcomeChat = await guild.create_text_channel('lfg-manager')

		embed = discord.Embed(title=l["welcome1"])
		embed.add_field(name=l["section2"], value=l["welcome2"], inline=False)
		embed.add_field(name=l["section3"], value=l["welcome3"], inline=False)
		embed.add_field(name=l["section4"], value=l["welcome4"], inline=False)
		embed.add_field(name=l["section5"], value=l["welcome5"], inline=False)
		await welcomeChat.send(embed=embed)

		lfgChat = await guild.create_text_channel('lfg')
		await lfgChat.send(l["lfg1"])

		with open(f"guildsets/{guild.id}_sets.json", "w") as f:
			print(f"Sono stato aggiunto al server {guild.name} ID: {guild.id}")
			jsonPre = {"games" : {"overwatch" : ":watch:", "minecraft" : ":b:"}, "lang" : "it", "role" : managerRole.id, "welcomeChat" : welcomeChat.id, "lfgChat":lfgChat.id}
			json.dump(jsonPre, f)
			#aggiungi delle impostazioni di default per il server quando il bot entra nel server
	except:
		console.print_exception()

def getGuildSettings(gid):
	with open(f"guildsets/{gid}_sets.json", "r") as f:
		jsonPre = json.load(f)
		return jsonPre

def saveGuildSettings(gid, dictionariation):
	with open(f"guildsets/{gid}_sets.json", "w") as f:
		json.dump(dictionariation, f)


@slash.slash(description="comando di prova")
async def hello(ctx, tag):
	await ctx.send(f"Ciao! {tag}")

@slash.slash(description="🇮🇹 Aggiungi un gioco alla lista\n🇬🇧 Add a game to list (ADMIN ONLY)")
# TODO permissionsssssssssssss
async def addgame(ctx, name, emoji):
	try:
		gsts = getGuildSettings(ctx.guild.id)
		l = langs[gsts["lang"]]
		if name in gsts["games"]:
			await ctx.send(l["addGameError_AlreadyExists"])
			return
		gsts["games"][name] = emoji
		saveGuildSettings(ctx.guild.id, gsts)
		allGamesPretty = "```diff\n"
		for i in gsts["games"]:
			if i == name:
				allGamesPretty += f"+ {gsts['games'][i]} {i}\n"
			else:
				allGamesPretty += f"= {gsts['games'][i]} {i}\n"
		allGamesPretty += "```"
		embed = discord.Embed(title=l["addGameConfirm"], description=allGamesPretty)
		await ctx.send(embed=embed)
	except:
		console.print_exception()

@slash.slash(description="🇮🇹 Rimuovi un gioco dalla lista\n🇬🇧 Remove a game from list (ADMIN ONLY)")
# TODO permissionsssssssssssss
async def removegame(ctx, name):
	try:
		gsts = getGuildSettings(ctx.guild.id)
		l = langs[gsts["lang"]]
		if name not in gsts["games"]:
			await ctx.send(l["removeGameError_NotFound"])
			return
		for i in gsts["games"]:
			if i == name:
				allGamesPretty += f"- {gsts['games'][i]} {i}\n"
			else:
				allGamesPretty += f"= {gsts['games'][i]} {i}\n"
		allGamesPretty += "```"

		gsts["games"].remove(name)
		saveGuildSettings(ctx.guild.id, gsts)
		allGamesPretty = "```diff\n"

		embed = discord.Embed(title=l["addGameConfirm"], description=allGamesPretty)
		await ctx.send(embed=embed)
	except:
		console.print_exception()

@slash.slash(description="🇮🇹 Visualizza tutti i giochi a cui giochiamo\n🇬🇧 View all games we play")
async def weplay(ctx):
	gsts = getGuildSettings(ctx.guild.id)
	l = langs[gsts["lang"]]
	hereWePretty = ""
	for i in gsts["games"]:
		hereWePretty += f'{gsts["games"][i]} {i}\n'
	embed = discord.Embed(title=l["hereWePlay"], description=hereWePretty)
	await ctx.send(embed=embed)

@slash.slash(description="Esce dal server con stile.")
async def lessgo(ctx):
	gsts = getGuildSettings(ctx.guild.id)
	welcomeChannel = discord.utils.get(ctx.guild.channels, name="lfg-manager")
	lfgChannel = discord.utils.get(ctx.guild.channels, name="lfg")
	managerRole = discord.utils.get(ctx.guild.roles, name="LFG Manager Manager")
	await welcomeChannel.delete()
	await lfgChannel.delete()
	await managerRole.delete()
	await ctx.send("Addio!", file=discord.File("byebye.gif"))
	toleave = client.get_guild(ctx.guild.id)
	await toleave.leave()	

client.run(BOT_TOKEN)