import discord
from discord.ext import commands
import json
from dotenv import load_dotenv
import os
import requests
import random

load_dotenv()

KEY = os.getenv('API_KEY')
tenorKey = os.getenv("TENOR_KEY")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class JSON:
    @staticmethod
    def readJson(file):
        with open(file, 'r') as f:
            return json.load(f)
        
    @staticmethod
    def createUserProfileInJson(user: discord.Member):
        profile = (user.id, {
            "cursed": False,
            "name": user.name
        })

        data = JSON.readJson('userData.json')
        with open('userData.json', "w") as f:
            data[str(profile[0])] = profile[1]
            json.dump(data, f, indent=4)
    
    
    @staticmethod
    def updateUserData(userId, attribute, newValue):
        data = JSON.readJson('userData.json')

        with open('userData.json', "w") as f:
            data[str(userId)][attribute] = newValue
            json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"Hi Nate"))
    print("Bot is online")

@bot.event
async def on_message(message):
   if message.author.id != bot.user.id:

    if testIfCursed(message.author):
        await message.add_reaction("🤡")
        await message.delete()
        return
    if 'fish' not in message.content.lower() and message.channel.name == 'fish':
        await message.channel.send(f"{message.author.mention} YOU DIDNT HAVE FISH. {message.author.name} IS BANNED.")
        await message.author.ban(reason="FISH.")
    else:   
        await bot.process_commands(message)

@bot.command()
async def curse(ctx, *, user: discord.Member):

    if user.id == 1182734770736746656:
        await ctx.send(f"Fuck you {ctx.author.mention}, you can't curse me.")
        await ctx.send(f"!curse {ctx.author.mention}")
        JSON.updateUserData(user.id, "cursed", True)
        await ctx.send(f"{ctx.author.mention} is cursed. Anything they say will be immediately deleted.")
        return

    data = JSON.readJson('userData.json')
    if str(user.id) not in data:
        JSON.createUserProfileInJson(user)
    JSON.updateUserData(user.id, "cursed", True)

    await ctx.send(f"{user.mention} is cursed. Anything they say will be immediately deleted.")

@bot.command()
async def uncurse(ctx, *, user: discord.Member):
    if user.id == ctx.author.id:
        return

    data = JSON.readJson('userData.json')
    if str(user.id) not in data:
        JSON.createUserProfileInJson(user)
    JSON.updateUserData(user.id, "cursed", False)

    await ctx.send(f"{user.mention} is uncursed. You are free from your shackles.")

@bot.command()
async def randomGif(ctx):
    string = ""
    length = 8

    for _ in range(length):
        string += chr(random.randint(0, 255))

    request = requests.get(f"https://tenor.googleapis.com/v2/search?q={string}&key={tenorKey}&client_key=my_test_app&limit=1").json()
    url = request["results"][0]["media_formats"]["tinygif"]["url"]

    await ctx.send(url)

def testIfCursed(user):
    data = JSON.readJson('userData.json')
    if data[str(user.id)]['cursed']:
        return True
    return False


bot.run(KEY)
