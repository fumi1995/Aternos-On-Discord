print('execute discordbot.py')

import discord
import os
import sys
import asyncio
from dotenv import load_dotenv
from discord.ext import tasks
#from Configure import launch_config
from connect_and_launch import get_status, get_number_of_players
from connect_and_launch import connect_account, quitBrowser, get_server_info
from connect_and_launch import start_server, stop_server

# 
#if not os.path.exists(os.path.relpath(".env")):
#    launch_config()
#    sys.exit()

load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

client = discord.Client()


@client.event
async def on_ready():
    text = "Logging into Aternos... | --help"
    await client.change_presence(activity=discord.Game(name=text))

    connect_account()  # logs into aternos
    print('The bot is logged in as {0.user}'.format(client))
    await asyncio.sleep(2)
    serverStatus.start()  # starts the presence update loop


@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.startswith('--'):

        if message.content.lower() == '--launch server':

            await message.channel.send("Launching Server...")
            status = get_status()

            if status == "Offline":
                await start_server()
                author = message.author
                # loops until server has started and pings person who launched
                while True:
                    await asyncio.sleep(5)
                    if get_status() == "Online":
                        await message.channel.send(f"{author.mention}, the "
                                                   f"server has started!")
                        break

            elif status == "Online":
                await message.channel.send("The server is already Online.")

            elif status == 'Starting ...' or status == 'Loading ...':
                text = "The server is already starting..."
                await message.channel.send(text)

            elif status == 'Stopping ...' or status == 'Saving ...':
                text = "The server is stopping. Please wait."
                await message.channel.send(text)

            else:
                text = "An error occurred. Either the status server is not " \
                       "responding or you didn't set the server name " \
                       "correctly.\n\nTrying to launch the server anyways."
                await message.channel.send(text)
                await start_server()

        elif message.content.lower() == '--server status':
            await message.channel.send(f"The server is {get_status()}.")

        elif message.content.lower() == '--players':
            text = f"There are {get_number_of_players()} players online."
            await message.channel.send(text)
        
        elif message.content.lower() == '--server info':
            ip, status, players, software, version = get_server_info()
            text = f"**IP:** {ip} \n**Status:** {status} \n**Players: " \
                   f"**{players} \n**Version:** {software} {version}"
            embed = discord.Embed()
            embed.add_field(name="Server Info", value=text, inline=False)
            await message.channel.send(embed=embed)

        elif message.content.lower() == '--stop server':
            await message.channel.send("Stopping the server.")
            status = get_status()

            if status != 'Stopping ...' or status != 'Saving ...':
                await stop_server()

            else:
                await message.channel.send("The server is already Offline.")

        elif message.content.lower() == '--help':
            embed = discord.Embed(title="Help")
            embed.add_field(name="--launch server",
                            value="Launches the server",
                            inline=False)
            embed.add_field(name="--server status",
                            value="Gets the server status",
                            inline=False)
            embed.add_field(name="--server info",
                            value="Gets the server info",
                            inline=False)
            embed.add_field(name="--players",
                            value="Gets the number of players",
                            inline=False)
            embed.add_field(name="--stop server",
                            value="Stops the server",
                            inline=False)
            embed.add_field(name="--crash",
                            value="Shuts down the bot",
                            inline=False)
            embed.add_field(name="--help",
                            value="Displays this message",
                            inline=False)
            await message.channel.send(embed=embed)

        elif message.content == '--crash':
            quitBrowser()
            text = "Bot Shutting Down..."
            await client.change_presence(activity=discord.Game(name=text))
            sys.exit()

        else:
            await message.channel.send("Unknown command, use --help to see a "
                                       "list of all avaliable commands.")


@tasks.loop(seconds=5.0)
async def serverStatus():
    text = f"Server: {get_status()} | Players: {get_number_of_players()} | " \
           f"--help"
    activity = discord.Activity(type=discord.ActivityType.watching, name=text)
    await client.change_presence(activity=activity)


client.run(BOT_TOKEN)
