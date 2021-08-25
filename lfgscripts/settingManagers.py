import json
def getGuildSettings(gid):
	with open(f"guildsets/{gid}_sets.json", "r") as f:
		jsonPre = json.load(f)
		return jsonPre

def saveGuildSettings(gid, dictionariation):
	with open(f"guildsets/{gid}_sets.json", "w") as f:
		json.dump(dictionariation, f)