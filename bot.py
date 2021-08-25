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
import random
from lfgscripts.tickingBomb import tickBomb
from lfgscripts.roleGiver import theRoleFather
from secrets import token_hex
from lfgscripts.settingManagers import getGuildSettings, saveGuildSettings
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption

lfgRequests = {}

console = Console()

# intents = discord.Intents.all()
client = commands.Bot(command_prefix="+")
slash = SlashCommand(client, sync_commands=True)

@client.event
async def on_ready():
   print(f"{client.user} e' online.")
   DiscordComponents(client)

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
		lfgMsg = await lfgChat.send(l["lfg1"])

		with open(f"guildsets/{guild.id}_sets.json", "w") as f:
			print(f"Sono stato aggiunto al server {guild.name} ID: {guild.id}")
			jsonPre = {"games" : {}, "lang" : "it", "role" : managerRole.id, "welcomeChat" : welcomeChat.id, "lfgChat":lfgChat.id, "roleFatherMsg" : lfgMsg.id}
			json.dump(jsonPre, f)
			#aggiungi delle impostazioni di default per il server quando il bot entra nel server
	except:
		console.print_exception()



@slash.slash(description="Update/Aggiorna The Father Of Roles")
async def fatherrole(ctx):
	await theRoleFather(getGuildSettings(ctx.guild.id), ctx.guild)
	await ctx.send("a")

@slash.slash(description="🇮🇹 Crea un annuncio LFG 🇬🇧 Make a LFG Post")
async def postlfg(ctx, game, desc, size):
	global lfgRequests
	gsts = getGuildSettings(ctx.guild.id)
	l = langs[gsts["lang"]]
	embed = discord.Embed(title=l["lfgTitle"], description=desc)
	if not game in [i.lower() for i in gsts["games"]]:
		await ctx.send(l["lfgNotFound"])
		return
	try:
		size = int(size)
		if size == 1:
			raise Exception
	except:
		await ctx.send(l["lfgNotNumber"])
		return
	gameRole = discord.utils.get(ctx.guild.roles, name=game)

	embed.add_field(name=l["lfgGame"], value=f"{gsts['games'][game]} {gameRole.mention}")
	embed.add_field(name=l["lfgSize"], value=f"1/{size}")
	embed.set_footer(text=f"{l['lfgPostBy']}{ctx.author}", icon_url=ctx.author.avatar_url)

	lfgChannel = discord.utils.get(ctx.guild.channels, name="lfg")
	await ctx.send(l["lfgTitlePre"], embed=embed)

	lfgId = token_hex(4)
	lfgRequests[lfgId] = {
		"embed" : embed,
		"size" : size,
		"currentSize" : 1,
		"game" : gameRole.mention,
		"message" : await lfgChannel.send(content=gameRole.mention, embed=embed, components=[Button(style=ButtonStyle.green, label=f"{l['lfgEnter']} - {lfgId}", custom_id="lfgAccept")])
	}

	createdVoiceChannel = False

	while lfgRequests[lfgId]["currentSize"] != lfgRequests[lfgId]["size"]:
		interaction = await client.wait_for("button_click", check=lambda i: i.component.label.startswith(f"{l['lfgEnter']} - {lfgId}"))

		if not createdVoiceChannel:
			createdVoiceChannel = True
			lfgRequests[lfgId]["voicechannel"] = await ctx.guild.create_voice_channel(f'LFG-voice-{lfgId}')
			lfgRequests[lfgId]["textchannel"] = await ctx.guild.create_text_channel(f'lfg-text-{lfgId}')

		print(repr(interaction))
		await interaction.respond(content=f'Voice: {lfgRequests[lfgId]["voicechannel"].mention}\nText: {lfgRequests[lfgId]["textchannel"].mention}')
		await ctx.send(f"{ctx.author.mention} {l['lfgSomeoneEntered']}{lfgRequests[lfgId]['voicechannel'].mention} {lfgRequests[lfgId]['textchannel'].mention}\n{l['lfgWarning']}")
		await tickBomb(lfgId, ctx.guild)
		lfgRequests[lfgId]["currentSize"] += 1
		# TODO canali autocancellanti e messaggio che si modifica a seconda di quanti sono dentor

	await lfgRequests[lfgId]["message"].delete()
	lfgRequests.pop(lfgId)

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
		selectedColor = random.choice([0xf94144, 0xf3722c, 0xf8961e, 0xf9844a, 0xf9c74f, 0x90be6d, 0x43aa8b, 0x4d908e, 0x577590, 0x277da1, 0x240046, 0x9d4edd, 0x582f0e])
		gameRole = await ctx.guild.create_role(name=name, colour=discord.Colour(selectedColor))
		await ctx.send(embed=embed)
	except:
		console.print_exception()

@slash.slash(description="🇮🇹 Rimuovi un gioco dalla lista\n🇬🇧 Remove a game from list (ADMIN ONLY)")
# TODO permissionsssssssssssss
async def removegame(ctx, name):
	try:
		gsts = getGuildSettings(ctx.guild.id)
		l = langs[gsts["lang"]]
		allGamesPretty = "```diff\n"
		if name not in gsts["games"]:
			await ctx.send(l["removeGameError_NotFound"])
			return
		for i in gsts["games"]:
			if i == name:
				allGamesPretty += f"- {gsts['games'][i]} {i}\n"
			else:
				allGamesPretty += f"= {gsts['games'][i]} {i}\n"
		allGamesPretty += "```"

		gsts["games"].pop(name)
		saveGuildSettings(ctx.guild.id, gsts)

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
		print(i)
		gameRole = discord.utils.get(ctx.guild.roles, name=i)
		hereWePretty += f'{gsts["games"][i]} {gameRole.mention}\n'
	embed = discord.Embed(title=l["hereWePlay"], description=hereWePretty)
	await ctx.send(embed=embed)

@slash.slash(description="Uninstalls the bot with style.")
async def uninstall(ctx, confirm):
	if confirm == "confirm":
		gsts = getGuildSettings(ctx.guild.id)
		welcomeChannel = discord.utils.get(ctx.guild.channels, name="lfg-manager")
		lfgChannel = discord.utils.get(ctx.guild.channels, name="lfg")
		managerRole = discord.utils.get(ctx.guild.roles, name="LFG Manager Manager")

		allRoles = f" - {managerRole.mention}\n"

		for i in gsts["games"]:
			gameRole = discord.utils.get(ctx.guild.roles, name=i)
			allRoles += f" - {gameRole.mention}\n"
			await gameRole.delete()

		allRoles += " - #lfg-manager\n - #lfg"
		embed = discord.Embed(title="Deleted", description=allRoles)
		
		await welcomeChannel.delete()
		await lfgChannel.delete()
		await managerRole.delete()
		await ctx.send(embed = embed, file=discord.File("byebye.gif"))
		toleave = client.get_guild(ctx.guild.id)
		await toleave.leave()	

client.run(BOT_TOKEN)