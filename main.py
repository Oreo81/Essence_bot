from discord import *
from discord.ext import commands


bot = commands.Bot(command_prefix="e!",intents=Intents.default())
key_file  = open("./key.txt", "r")

#================================================================================

bot.load_extension("cogs.ess")
bot.load_extension("cogs.help")

#================================================================================

@bot.event
async def on_ready():
	print("Près à être utilisé !")

bot.run(key_file.readline())
key_file.close()

#FIN ============================================================================