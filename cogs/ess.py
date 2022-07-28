import discord
from discord.ext import commands
import urllib.request 
from math import *
import xml.etree.ElementTree as ET
import zipfile
import os
from datetime import datetime
import requests
import json
from html2image import Html2Image
import folium
#-----------------
def main_(ess,lat,lon,dis):
    distance = int(dis)*1000
    download()
    #Ess dispo: 'SP98' / 'SP95' / 'Gazole' / 'E10' / 'E85' / 'GPLc'
    pompe_dispo = trie_pompe(lecture_file_and_add_pompe('PrixCarburants_instantane.xml',lat,lon,distance),ess)
    return tri_croiss(pompe_dispo)

#-----------------
def download():
    urllib.request.urlretrieve('https://donnees.roulez-eco.fr/opendata/instantane', './file.zip')
    with zipfile.ZipFile('./file.zip', 'r') as zip_ref:
        zip_ref.extractall('./')
    os.remove('./file.zip')

#-----------------
def lecture_file_and_add_pompe(file,lat,lon,dis):
    output=[]
    tree = ET.parse(file)
    root = tree.getroot()
    coo1 = cal_lat_lon(lat,lon,dis)
    coo2 = cal_lat_lon(lat,lon,-dis)
    for child in root:
        lat = child.attrib.get('latitude')
        lon = child.attrib.get('longitude')
        try:
            if float(coo1[0]) >= float(lat) >= float(coo2[0]) and float(coo1[1]) >= float(lon) >= float(coo2[1]):
                output.append(child)
        except:
            pass
    return output

#-----------------
def cal_lat_lon(latitude,longitude,distance_m):
    coef = ((distance_m/2) * sqrt(2) )* 0.0000089
    new_latitude = (float(latitude) + coef )*100000
    new_longitude = (float(longitude) + coef / cos(float(latitude) * 0.018)) *100000
    return new_latitude, new_longitude

#-----------------
#Ess dispo: 'SP98' / 'SP95' / 'Gazole' / 'E10' / 'E85' / 'GPLc'
def trie_pompe(list_pompe,ess):
    list_pp=[]
    for child in list_pompe:
        for element in range(len(child)):
            if child[element].tag == 'prix':
                if child[element].get('nom') == ess:
                    list_pp.append((child[0].text,child[1].text,child[element].attrib,child.attrib.get('latitude'),child.attrib.get('longitude')))
    return list_pp

#-----------------
def tri_croiss(main_tab):
    n=len(main_tab)
    for i in range(1,n):
        element_a_inserer=main_tab[i]
        j=i
        while j>0 and main_tab[j-1][2].get('valeur')>element_a_inserer[2].get('valeur'):
            #trie en fonction du prix au litre
            main_tab[j]=main_tab[j-1]
            j=j-1
        main_tab[j]=element_a_inserer
    return main_tab[:3]
    #return seulement les 3 meilleurs

#-----------------
def check_date(main_tab,now):
    date_in_tab = main_tab[2].get('maj')[:10]
    if date_in_tab == now:
        return ":arrow_forward: **Aujourd'hui**"
    else:     
        now_splt = now.split('-')
        date_in_tab_split = date_in_tab.split('-')
        if int(now_splt[1]) - int(date_in_tab_split[1]) >= 1:
            return ":x: **Plus d'un moins, le carburant n'est sûrement plus en stock**"
        elif int(now_splt[2]) - int(date_in_tab_split[2]) == 1:
            return ":arrow_forward: **Hier**"
        elif int(now_splt[2]) - int(date_in_tab_split[2]) == 2:
            return ":arrow_forward: **Deux jours**"
        elif int(now_splt[2]) - int(date_in_tab_split[2]) == 3:
            return ":arrow_forward: **Trois jours**"
        else:           
            return ":x: **Plus de trois jours, le carburant n'est sûrement plus en stock**"

def adresse_to_locate(adresse):
    city = requests.get('https://api-adresse.data.gouv.fr/search/?q={}&limit=1'.format(adresse))
    recup = json.loads(city.text)
    return recup.get('features')[0].get('geometry').get('coordinates')
    

#-------------------------------------------
class Com(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog Command Ready!')
     
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            try:
                embed=discord.Embed(title=':x: Erreur',color=discord.Color.red())
                embed.set_author(name="{} - Help --> e!?".format(ctx.author.name),icon_url=ctx.author.avatar_url)
                embed.add_field(name="Comamnde:", value='e!prix (essence) (distance en KM) (adresse)')
                embed.add_field(name="Essence disponible:", value='SP95 / Gazole / E10 / E85 / GPLc')
                await ctx.send(embed=embed)
            except discord.HTTPException:
                pass
#================================================================================
    @commands.command('prix',aliases=['p'])
    async def prix(self,ctx,ess,dis,*,adresse):
        dispo = ['SP98','SP95','Gazole','E10','E85','GPLc']

        coo = adresse_to_locate(adresse)

        hti = Html2Image(custom_flags=['--no-sandbox','--gpu off'])
        hti.browser_executable = "/usr/bin/google-chrome"

        m = folium.Map(location=[coo[1],coo[0]], zoom_start=12, disable_3d=True)
        folium.Marker(
            location=[coo[1],coo[0]],
            popup='Kumpula Campus',
            icon=folium.Icon(color='gray', icon='ok-sign'),
        ).add_to(m)
        m.save('index.html')
        with open('./index.html') as f:
            hti.screenshot(f.read(), save_as='out.png', size=(250, 250))

        embed=discord.Embed(title=':wheelchair: Recherche en cours de traitement',color=0xFFFFFF,url=f'https://www.google.com/maps/search/?api=1&query={coo[1]}%2C{coo[0]}')
        file = discord.File('./out.png', filename="out.png")
        embed.set_thumbnail(url="attachment://out.png")
        embed.set_author(name="{} - Info".format(ctx.author.name),icon_url=ctx.author.avatar_url)
        embed.add_field(name=":pushpin: Lieu de départ: {}".format(adresse),value="Essence: {}, Distance: {}km".format(ess,dis), inline=False)
        await ctx.send(file=file,embed=embed)

        if ess not in dispo:
            embed=discord.Embed(title=':x: Erreur',color=discord.Color.red())
            embed.set_author(name="{} - Help --> e!?".format(ctx.author.name),icon_url=ctx.author.avatar_url)
            embed.add_field(name="Essence disponible:", value='SP95 / Gazole / E10 / E85 / GPLc', inline=False)
            await ctx.send(embed=embed)
        else:    
            now = datetime.now().strftime("%Y-%m-%d")
            try:
                tab = main_(ess,coo[1],coo[0],dis)
                if 1<= int(dis) <= 30:
                    if len(tab) == 0:
                        embed=discord.Embed(title=':warning: Rien trouvé',color=0xFFFFFF)
                        embed.set_author(name="{} - Info".format(ctx.author.name),icon_url=ctx.author.avatar_url)
                        embed.add_field(name="Essayé avec une distance plus grande", value="Entre 1 & 30km", inline=False)
                        embed.add_field(name="Comamnde:", value='e!prix (essence) (distance en KM) (adresse)')
                        embed.add_field(name="Essence disponible:", value='SP95 / Gazole / E10 / E85 / GPLc')
                        await ctx.send(embed=embed)
                    else:
                        color = [discord.Color.green(),discord.Color.orange(),discord.Color.red()]
                        color_map = ['green','orange','red']
                        for el in tab:
                            m = folium.Map(location=[float(el[3])/100000,float(el[4])/100000], zoom_start=16, disable_3d=True)
                            folium.Marker(
                                location=[float(el[3])/100000,float(el[4])/100000],
                                popup='Kumpula Campus',
                                icon=folium.Icon(color=color_map[tab.index(el)], icon='ok-sign'),
                            ).add_to(m)
                            m.save('index.html')
                            with open('./index.html') as f:
                                hti.screenshot(f.read(), save_as='out.png', size=(500, 500))

                            output = (("Pompe {}: Essence {}= {}€/L".format(tab.index(el)+1,el[2].get('nom'),el[2].get('valeur'))),("{} {}".format(el[0],el[1])),(check_date(el,now)))
                            embed=discord.Embed(title=output[0],color=color[tab.index(el)],url='https://www.google.com/maps/search/?api=1&query={}%2C{}'.format(float(el[3])/100000,float(el[4])/100000))
                            file = discord.File('./out.png', filename="out.png")
                            embed.set_thumbnail(url="attachment://out.png")
                            embed.add_field(name="Adresse:", value=output[1], inline=False)
                            embed.add_field(name="Date d'actualisation:", value=output[2], inline=False)


                            await ctx.send(file=file,embed=embed)
                        
                else:
                    embed=discord.Embed(title=':x: Erreur',color=discord.Color.red())
                    embed.set_author(name="{} - Help --> e!?".format(ctx.author.name),icon_url=ctx.author.avatar_url)
                    embed.add_field(name="Essayé avec une autre distance", value="Entre 1 & 30km", inline=False)
                    embed.add_field(name="Comamnde:", value='e!prix (essence) (distance en KM) (adresse)')
                    embed.add_field(name="Essence disponible:", value='SP95 / Gazole / E10 / E85 / GPLc')
                    await ctx.send(embed=embed)
            except Exception as e:
                print(e)
                embed=discord.Embed(title=':x: Erreur',color=discord.Color.red())
                embed.set_author(name="{} - Help --> e!?".format(ctx.author.name),icon_url=ctx.author.avatar_url)
                embed.add_field(name="Comamnde:", value='e!prix (essence) (distance en KM) (adresse)')
                embed.add_field(name="Essence disponible:", value='SP95 / Gazole / E10 / E85 / GPLc')
                await ctx.send(embed=embed)
    

#================================================================================
def setup(bot):
    bot.add_cog(Com(bot))

#FIN ============================================================================