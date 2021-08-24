# A script for deleting channels when nobody is inside
import discord
import asyncio
from discord.utils import get

async def tickBomb(lfgId, guild):
	"""Every 1m check if someone is in the channel, if not delete it"""
	while True:
		await asyncio.sleep(60)
		voiceChannel = discord.utils.get(guild.channels, name="LFG-voice-"+str(lfgId))
		textChannel = discord.utils.get(guild.channels, name="lfg-text-"+str(lfgId))
		if list(voiceChannel.voice_states.keys()) == []:
			await voiceChannel.delete()
			await textChannel.delete()
			break