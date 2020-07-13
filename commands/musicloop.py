"""Toggle Looping Current Piece"""
import discord

from utility import music

description = __doc__

usage = "{prefix}loop\n"

aliases = dict()

required_parameters = set()

required_permissions = set()

expected_positional_parameters = list()


async def run(client: discord.Client, group, message: discord.Message, args: dict):
    # noinspection PyUnresolvedReferences
    music_manager: music.MusicManager = client.music_manager
    # Check if requester is in a voice channel
    if message.author.voice is None:
        await message.channel.send("You are not in a voice channel!")
        return "Requester is not in a voice channel"

    queue = music_manager.get_queue(message.guild)

    queue.looping_current_piece = not queue.looping_current_piece
    if queue.looping_current_piece:
        await message.channel.send("Now looping current piece")
    else:
        await message.channel.send("No longer looping current piece")
