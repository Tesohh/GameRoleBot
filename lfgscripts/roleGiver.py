from typing import Type
import discord
from discord import channel
from discord.utils import get
import json
import asyncio
from rich.console import Console
from languages_iten import langs
import random
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption
from lfgscripts.settingManagers import saveGuildSettings

console = Console()

async def theRoleFather(gsts, g):
	try:
		l = langs[gsts["lang"]]
		c = discord.utils.get(g.channels, name="lfg")
		# m = await c.fetch_message(gsts["roleFatherMsg"])
		roleOptions = []
		for i in gsts["games"]:
			roleOptions.append(SelectOption(label=i, value=i, emoji=gsts["games"][i]))
		
		embed = discord.Embed(title="The Father Of Roles", description=l["roleDesc"])

		# await m.delete()
		m = await c.send(embed=embed, components=Select(placeholder=l["rolePlaceholder"], options=roleOptions))
		gsts["roleFatherMsg"] = m.id
		saveGuildSettings(g.id, gsts)
		# NON FUNGE. DA ERRORE PECULIARE TypeError: object of type 'Select' has no len()
		# Manca anche il wait_for nel bot.py

	except:
		console.print_exception()
		
