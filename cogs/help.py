import discord
from datetime import *
from time import *
from discord.ext import commands

class help(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command(name="help",aliases=['h', '?'])
    async def help(self,ctx,*input):
        embed = discord.Embed(
            title = "\U0001F4CD Help [e!help / e!h / e!?]",
            color = discord.Colour.purple() 
        )
        embed.set_author(name="{} - Help menu".format(ctx.author.name),icon_url=ctx.author.avatar_url)
        if not input:
            embed.add_field(name=":bar_chart: 〉 e!prix / e!p", value="e!p {Essence} {Distance (km)} {Adresse}", inline= False)
            embed.add_field(name=":purple_circle: 〉 Essence", value="Type d'essence: SP95 / Gazole / E10 / E85 / GPLc", inline= False)
            embed.add_field(name=":purple_circle: 〉 Distancee", value="Distance en km entre 1 et 30", inline= False)
            embed.add_field(name=":purple_circle: 〉 Adresse", value="Lieux pour centre de recherche. Ville / adresse complète (espace autorité)", inline= False)
            await ctx.send(embed=embed)
        else:
            error = discord.Embed(
                title = "{}  La commande '{}' n'existe pas".format("\U000026D4",input[0]),
                color = discord.Colour.dark_red()
            )
            await ctx.send(embed=error)

def setup(bot):
    bot.remove_command("help")
    bot.add_cog(help(bot))        

#FIN ============================================================================