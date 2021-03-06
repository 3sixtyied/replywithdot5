"""BrianLib"""
import datetime
import hashlib
import re

import aiohttp
import discord

from classes import botexception


# from objects import errors


def dict_from_object(object_) -> dict:
    """Returns a dictionary with the public non-function attributes and values of an object"""
    dict_to_return = dict()
    for attribute in dir(object_):
        if attribute.startswith("_"):
            continue
        # Check if attribute is a function
        try:
            if hasattr(getattr(object_, attribute), "__call__"):
                continue
        except AttributeError:
            # raise errors.NothingChangedException("what the fuck")
            pass
        try:
            dict_to_return[attribute] = getattr(object_, attribute)
        except AttributeError:
            pass
    return dict_to_return


# Currently Non-Functional
async def upload_sharex(url, file) -> str:
    print(file)
    print("im here")
    data = aiohttp.FormData()
    # reverse engineering sharex :sunglasses:
    data.add_field("files[]", file, filename="text.txt", content_type="text/plain")
    print(str(data))
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            print("now im here")
            print(await response.text())
            return (await response.json())["files"][0]["url"]


# Currently Non-Functional
async def upload_discordjsmoe(file) -> str:
    print("im here")
    data = aiohttp.FormData()
    # reverse engineering sharex :sunglasses:
    data.add_field("files[]", file, filename="text.txt", content_type="text/plain")
    async with aiohttp.ClientSession() as session:
        async with session.post("https://discordjs.moe/api/upload", data=data,
                                headers={"token": os.environ.get("discordjsmoe_token")}) as response:
            print("now im here")
            print(await response.text())
            return (await response.json())["files"][0]["url"]


async def upload_discord(channel, file, filename) -> str:
    """Uploads a file to a Discord channel and returns the URL"""
    return (await channel.send(file=discord.File(file, filename=filename))).attachments[0].url


def diff_obj(first, second) -> str:
    """Returns a string with the differences between the public non-function attributes of two objects pretty-printed
    """
    diff_str = ""
    first_dict = dict_from_object(first)
    second_dict = dict_from_object(second)
    for key1, value1 in first_dict.items():
        if value1 == second_dict[key1]:
            continue
        else:
            diff_str += f"{key1}: {value1} -> {second_dict[key1]}\n"
    return diff_str.strip()


def parse_command_arguments(string: str) -> dict:
    """Returns a dictionary with the command arguments from a string"""
    return {key: value for key, value in [x.split("=") for x in string.split(" ")[1:]]}


def map_aliases(dictionary: dict, aliases: dict) -> dict:
    """Combines key variations in dictionary to keys from aliases"""
    return {aliases[k]: v for k, v in dictionary.items()}


def str_from_object(object_: object) -> str:
    """Returns a pretty-printed string"""
    return "\n".join([f"{k}: {v}" for k, v in dict_from_object(object_).items()])


def do_nothing(**kwargs) -> None:
    pass


def return_true(**kwargs) -> bool:
    return True


def return_false(**kwargs) -> bool:
    """Equivalent to do_nothing"""
    return False


def is_user_bot(user=None) -> bool:
    """For discord.py's user class"""
    return user.bot


def is_client_user_bot(client=None) -> bool:
    """For discord.py's client class"""
    return client.user.bot


def get_snowflake_timestamp(snowflake: int) -> str:
    """Returns UTC time from a Discord snowflake"""
    # milliseconds from discord epoch
    time_flake = ((snowflake >> 22) + 1420070400000) // 1000
    return datetime.datetime.utcfromtimestamp(time_flake).strftime('%Y-%m-%d %H:%M:%S')


def is_member_in_guilds(member_id: int, guilds: set) -> bool:
    return member_id in (iii.id for ii in (i.members for i in guilds) for iii in ii)


def get_pretty_printed_sorted_dict(dictionary: dict) -> str:
    return ", ".join([f"{key}: {value}" for key, value in
                      list({k: v for k, v in sorted(dictionary.items(), key=lambda item: item[1])}
                           .items())[::-1]])


def handle_argument_list(string: str, get_one_function, get_all_function, separator: str = ",") -> list:
    """Returns an Iterable"""
    if string == "all":
        if hasattr(get_all_function, "__call__"):
            return get_all_function()
        else:
            return get_all_function
    else:
        # for i in get_one_function(string.split(separator)):
        #      yield i
        return [get_one_function(int(i)) for i in string.split(separator)]


def wrap_object(obj: object) -> object:
    """Objectively the most useless function ever. Haha, get it?"""
    return obj


def flatten_generator(generator) -> list:
    """Turns a generator into a list"""
    flattened = []
    for i in generator:
        flattened.append(i)
    return flattened


def multireplace(string, replacements, ignore_case=False):
    """
    Given a string and a replacement map, it returns the replaced string.
    :param str string: string to execute replacements on
    :param dict replacements: replacement dictionary {value to find: value to replace}
    :param bool ignore_case: whether the match should be case insensitive
    :rtype: str
    """
    # If case insensitive, we need to normalize the old string so that later a replacement
    # can be found. For instance with {"HEY": "lol"} we should match and find a replacement for "hey",
    # "HEY", "hEy", etc.
    if ignore_case:
        def normalize_old(s):
            return s.lower()

        re_mode = re.IGNORECASE

    else:
        def normalize_old(s):
            return s

        re_mode = 0

    replacements = {normalize_old(key): val for key, val in replacements.items()}

    # Place longer ones first to keep shorter substrings from matching where the longer ones should take place
    # For instance given the replacements {'ab': 'AB', 'abc': 'ABC'} against the string 'hey abc', it should produce
    # 'hey ABC' and not 'hey ABc'
    rep_sorted = sorted(replacements, key=len, reverse=True)
    rep_escaped = map(re.escape, rep_sorted)

    # Create a big OR regex that matches any of the substrings to replace
    pattern = re.compile("|".join(rep_escaped), re_mode)

    # For each match, look up the new string in the replacements, being the key the normalized old string
    return pattern.sub(lambda match: replacements[normalize_old(match.group(0))], string)


def command_argument_parser(
        argument_string: str,
        expected_positional_arguments: list,
        string_separator: str = " ",
        keyword_argument_prefix: str = "--"
):
    """
    :param str argument_string: A string of the arguments, minus the command itself
    :param list expected_positional_arguments: A list of positional arguments to expect
    :param str string_separator: The string which is placed between the arguments
    :param str keyword_argument_prefix: The string which signifies the start of a keyword parameter
    :return: A dictionary of the parsed arguments The dictionary contains strings
    Parses Bash-like commands
    """
    separated_string = argument_string.split(string_separator)
    # Avoid IndexError when zero arguments are present
    if separated_string == [""]:
        return dict()
    return_arguments = dict()
    # Keep track of current position
    current_position = 0
    while len(separated_string) > 0:
        # Set current item
        # Remove current item from processing queue
        current_item = separated_string.pop(0)
        # Parse --arg arguments
        if current_item.startswith(keyword_argument_prefix):
            current_argument_value = list()
            # Do not take the next keyword argument as part of the current value
            # Iterate through the processing queue
            # Note: For presence arguments, check for presence in the dictionary, not for its boolean value
            while len(separated_string) > 0 and not separated_string[0].startswith(keyword_argument_prefix):
                # Append value and Remove processed value from the processing queue
                current_argument_value.append(separated_string.pop(0))
                current_position += 1
            # Set the current value
            return_arguments[current_item[len(keyword_argument_prefix):]] = string_separator.join(
                current_argument_value)
        else:
            # Set by positional argument
            # Allow the last positional argument to have the separator in between
            if current_position >= len(expected_positional_arguments):
                if expected_positional_arguments[-1] in return_arguments:
                    return_arguments[expected_positional_arguments[-1]] += string_separator + current_item
                else:
                    return_arguments[expected_positional_arguments[-1]] = current_item
            else:
                return_arguments[expected_positional_arguments[current_position]] = current_item

        current_position += 1

    return return_arguments


# https://github.com/django/django/blob/stable/1.3.x/django/core/validators.py#L45
valid_url_regex = regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def is_string_valid_url(string: str) -> bool:
    return re.match(valid_url_regex, string) is not None


async def connect_with_member(member, timeout=60, reconnect=True):
    """
    :param discord.Member member: Member whom to join
    :param int timeout: Timeout for joining the voice channel
    :param bool reconnect: Whether to reconnect if part of the handshake fails or the gateway goes down
    :return: The Voice Client
    :rtype: discord.VoiceClient
    :raises botexception.MemberNotInAnyVoiceChannelException: If member.voice is None
    :raises asyncio.TimeoutError: Could not connect to the voice channel in time.
    :raises discord.ClientException: You are already connected to a voice channel.
    :raises discord.opus.OpusNotLoaded: The opus library has not been loaded.
    """
    if member.voice is None:
        raise botexception.MemberNotInAnyVoiceChannelException
    else:
        return await get_voice_client(member.voice.channel, timeout=timeout, reconnect=reconnect)


async def get_voice_client(voice_channel, timeout=60, reconnect=True):
    """
    :param discord.VoiceChannel voice_channel: Voice Channel to join
    :param int timeout: Timeout for joining the voice channel
    :param bool reconnect: Whether to reconnect if part of the handshake fails or the gateway goes down
    :return: Voice Client
    :rtype: discord.VoiceClient
    :raises asyncio.TimeoutError: Could not connect to the voice channel in time.
    :raises discord.ClientException: You are already connected to a voice channel.
    :raises discord.opus.OpusNotLoaded: The opus library has not been loaded.
    """
    return await voice_channel.connect(timeout=timeout, reconnect=reconnect)


alphanumerical = "abcdefghijklmnopqrstuvwxyz1234567890"

one_megabyte_chunk_size = 1048576  # 1024^2


async def audio_getter_creator(url):
    """
    :param url: URL
    :return: FFmpegPCMAudio
    :rtype: discord.FFmpegPCMAudio
    Reads cached files from disk
    """
    file_url_hash = hashlib.sha3_256(bytes(url, "utf-8")).hexdigest()
    file_name = f"cache/{file_url_hash}"

    return discord.FFmpegPCMAudio(file_name)


def remove_chars_from_string(string, chars):
    """Remove Chars from string"""
    return "".join([x for x in string if x not in chars])


def keep_only_chars_in_string(string, chars):
    """Filter String to only contain chars"""
    return "".join([x for x in string if x in chars])


class PreparedCoroutine:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        return self.func(*self.args, **self.kwargs)


def format_time(**kwargs):
    """Format time string"""
    return str(datetime.timedelta(**kwargs))


class WrappedTuple(tuple):
    """Tuple with indexes that wrap around"""

    def __getitem__(self, item):
        item = item % len(self)
        return super().__getitem__(item)


async def fetch_latest_message(text_channel: discord.TextChannel) -> discord.Message:
    """Gets the latest message in a text channel"""
    return (await text_channel.history(limit=1).flatten())[0]


def get_snowflake_epoch(snowflake: int) -> int:
    """Returns UTC time from a Discord snowflake"""
    return ((snowflake >> 22) + 1420070400000) // 1000


async def search_google_images(
        image_url,
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0"
):
    """
    :param image_url: a str or URL object
    :param str user_agent: the user agent to use
    :return: The response in bytes
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"http://www.google.com/searchbyimage?image_url={image_url}",
                headers={
                    "User-Agent": user_agent
                },
                allow_redirects=True
        ) as response:
            return await response.read()


def counter_confidence_with_word_list(counter, word_list):
    """
    :param collections.Counter counter:
    :param word_list: Any Iterable
    :return: A list containing the percentage of how common the word is compared to the total of all the words
    """
    total_count = 0
    for element, count in counter.most_common():
        if element in word_list:
            total_count += count

    return [[element, count, 100 * (count / total_count)]
            for element, count in counter.most_common()
            if element in word_list]


primitives = int, float, str, bool


def is_primitive(obj):
    for type_ in primitives:
        if isinstance(obj, type_):
            return True
    return False
