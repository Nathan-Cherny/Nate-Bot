import discord
from discord.ext import commands
import json
from dotenv import load_dotenv
import os

load_dotenv()

KEY = os.getenv('API_KEY')

print(KEY)

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
    if 'fish' not in message.content.lower() and message.channel.name == 'fish':
        await message.channel.send(f"{message.author.mention} YOU DIDNT HAVE FISH. {message.author.name} IS BANNED.")
        await message.author.ban(reason="FISH.")
    else:   
        await bot.process_commands(message)

@bot.command()
async def curse(ctx, *, user: discord.Member):
    userId = user.id

    data = JSON.readJson('userData.json')
    if str(user.id) not in data:
        JSON.createUserProfileInJson(user)
    JSON.updateUserData(user.id, "cursed", True)

    await ctx.send(f"{user.mention} is cursed. Anything they say will be immediately deleted.")

@bot.command()
async def ban(ctx, *, user: discord.Member):
    await user.ban(reason="FISH.")

def testIfCursed(user):
    data = JSON.readJson('userData.json')
    if data[str(user.id)]['cursed']:
        return True
    return False

bot.run(KEY)