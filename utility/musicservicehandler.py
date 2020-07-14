import hashlib
import logging
import pathlib

import aiohttp
import youtube_dl

from utility import blib, music

cache_folder = "cache/"


async def handler_dl(query, voice_client, text_channel, member, loop):
    file_url_hash = hashlib.sha3_256(bytes(query, "utf-8")).hexdigest()
    file_name = f"{cache_folder}{file_url_hash}"
    if pathlib.Path(file_name).is_file():
        logging.info(f"{file_name} already exists. Using cached version.")
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(query) as response:
                with open(file_name, "wb") as file:
                    while 1:
                        chunk = await response.content.read(blib.one_megabyte_chunk_size)
                        if not chunk:
                            break
                        file.write(chunk)

    prepared_coroutine = blib.PreparedCoroutine(blib.audio_getter_creator, query)
    return music.Piece(
        query, prepared_coroutine, voice_client, text_channel, member
    )


async def handler_yt(query, voice_client, text_channel, member, loop):
    video_info = await loop.run_in_executor(None, helper_ytdl, query)
    link = f"https://youtube.com/watch?v={video_info['entries'][0]['id']}"

    # This will not download anything, as it will have already be downloaded
    prepared_coroutine = blib.PreparedCoroutine(blib.audio_getter_creator, query)
    return music.Piece(
        link, prepared_coroutine, voice_client, text_channel, member
    )


def helper_ytdl(query):
    ytdl_format_options = {
        'format': 'bestaudio/best',
        'outtmpl': f"{cache_folder}{hashlib.sha3_256(bytes(query, 'utf-8')).hexdigest()}",
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        'usenetrc': True
    }
    ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
    # ytdl.download([query])
    output = ytdl.extract_info(query, download=True)
    return output
