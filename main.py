import discord
from discord.ext import commands
import json
from dotenv import load_dotenv
import os
import requests
import random
from pytube import YouTube
import ffmpeg
import math

load_dotenv()

KEY = os.getenv('API_KEY')
tenorKey = os.getenv("TENOR_KEY")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# some classes

class JSON:
    @staticmethod
    def readJson(file):
        with open(file, 'r') as f:
            return json.load(f)
        
    @staticmethod
    def appendToListJson(file, newData):
        data = JSON.readJson(file)
        data.append(newData)
        with open(file, "w") as f:
            json.dump(data, f, indent=4)
        return data
        
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

# helper functions

def testIfCursed(user):
    data = JSON.readJson('userData.json')
    if data[str(user.id)]['cursed']:
        return True
    return False

def getAudioSourceUrlFromYouTubeLink(url):
    yt = YouTube(url)
    return yt.streams.filter(only_audio=True)[-1]

def youtubeSongEmbed(yt):
    embed = discord.Embed(title=yt.title)
    embed.set_image(url = yt.thumbnail_url)
    embed.add_field(name="Author", value=yt.author)
    embed.add_field(name="Views", value=yt.views)
    
    length = yt.length
    minutes = math.floor(length/60)
    seconds = length%60

    embed.add_field(name="Length", value=f"{minutes}:{seconds}")
    embed.add_field(name="Url", value=yt.watch_url)
    return embed

# events ------------------------

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
    
# commands ----------------------

@bot.command(help='Curses a user, and prevents them from talking. Do !curse <@user>')
async def curse(ctx, *, user: discord.Member):

    if user.id == 1182734770736746656:
        await ctx.send(f"Fuck you {ctx.author.mention}, you can't curse me.")
        await ctx.send(f"!curse {ctx.author.mention}")

        JSON.updateUserData(ctx.author.id, "cursed", True)

        await ctx.send(f"{ctx.author.mention} is cursed. Anything they say will be immediately deleted.")
        return

    data = JSON.readJson('userData.json')
    if str(user.id) not in data:
        JSON.createUserProfileInJson(user)
    JSON.updateUserData(user.id, "cursed", True)

    await ctx.send(f"{user.mention} is cursed. Anything they say will be immediately deleted.")

@bot.command(help='Uncurses a user. See curse.')
async def uncurse(ctx, *, user: discord.Member):
    if user.id == ctx.author.id:
        return

    data = JSON.readJson('userData.json')
    if str(user.id) not in data:
        JSON.createUserProfileInJson(user)
    JSON.updateUserData(user.id, "cursed", False)

    await ctx.send(f"{user.mention} is uncursed. You are free from your shackles.")

@bot.command(help='Generates a random gif and sends it. Mostly kpop or anime unfortunately.')
async def randomGif(ctx):
    string = ""
    length = 8

    for _ in range(length):
        string += chr(random.randint(0, 255))

    request = requests.get(f"https://tenor.googleapis.com/v2/search?q={string}&key={tenorKey}&client_key=my_test_app&limit=1").json()
    url = request["results"][0]["media_formats"]["tinygif"]["url"]

    await ctx.send(url)

@bot.command(help='Bot will join the vc of the user who calls this.')
async def joinvc(ctx):
    if not ctx.message.author.voice:
        await ctx.send(f"{ctx.message.author.mention}, you're not in a vc right now")
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(help="If the bot is in a vc, it'll leave it.")
async def leavevc(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        
"""@bot.command(help='Plays the audio from a YouTube url. !play <url>')
async def playYT(ctx, *, url):
    if ctx.voice_client:
        audio_source = discord.FFmpegPCMAudio('song.webm')

        while True:
            ctx.voice_client.play(audio_source)"""


@bot.command(help="Adds a song url to the queue.")
async def addSong(ctx, *, url):
    if not url:
        await ctx.send("You don't have a url lol")
        return
    queue = JSON.appendToListJson("songQueue.json", url)
    yt = YouTube(url)
    await ctx.send(f"Added {yt.title} to queue at position {queue.index(url) + 1}.", embed=youtubeSongEmbed(YouTube(url)))


@bot.command(help="Lists all the songs that are in the queue.")
async def listQueue(ctx):
    queue = JSON.readJson("songQueue.json")
    embed = discord.Embed(title="Song Queue")
    i = 1
    for song in queue:
        yt = YouTube(song)
        embed.add_field(name=f"Position {i}", value=yt.title, inline=True)
        i += 1

    await ctx.send(embed=embed)

@bot.command(help="Plays the song that is first in line in the queue.")
async def play(ctx):
    song = YouTube(JSON.readJson("songQueue.json")[-1])
    stream = song.streams.filter(only_audio=True)[-1]
    stream.download(filename="song.webm")
    
    # song is downloded; let's play it
    
    audio_source = discord.FFmpegPCMAudio("song.webm")
    ctx.voice_client.play(audio_source)
    await ctx.send(f"Playing {song.title}", embed=youtubeSongEmbed(song))

    

bot.run(KEY)
