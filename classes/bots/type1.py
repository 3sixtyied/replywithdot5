from os import environ

import discord

from classes.bot import Bot
from tasks.on_connect import status, persistentstorageautoupdate
# from actions.on_message import
from utility import blib
from utility.persistentstoragev2 import PersistentStorage


class Type1(Bot):

    def __init__(self, token: str, group):
        super().__init__(token, group)

        class Client(discord.Client):

            async def on_connect(self):
                self.persistent_storage = PersistentStorage(self.get_guild(int(environ.get("host_guild_id"))))
                self.command_dict = command_dict
                for i in task_dict["on_connect"]:
                    self.loop.create_task(i)

            async def get_prefix_of_guild(self, guild):
                try:
                    return (await self.persistent_storage.get_config(guild.id))["prefix"]
                except KeyError:
                    return default_prefix

            async def on_message(self, message):
                for i in actions_dict["on_message"]:
                    self.loop.create_task(i.run(self, message))
                # if message.content.startswith(prefix):
                prefix = await self.get_prefix_of_guild(message.guild)
                # Due to the presence of return statements, this should always be last.
                if message.content.startswith(prefix):
                    prefix_and_command = message.content.split(string_separator)[0]
                    try:
                        # Dictionaries are O(1), while iterating through a list is O(n/2)
                        # Identify Command
                        command = command_dict[prefix_and_command[len(prefix):]]
                    except KeyError:
                        # Command not found
                        return
                    else:
                        # Command found
                        # Check for permissions
                        for i in command.required_permissions:
                            if not getattr(message.author.guild_permissions, i) is True:
                                await message.channel.send(f"Lacking Required Permissions!\n"
                                                           f"You are missing the permission {i}")
                                return

                        argument_string = message.content[len(prefix_and_command) + 1:]

                        command_arguments = blib.command_argument_parser(
                            argument_string, command.expected_positional_parameters
                        )
                        # Check if all the required parameters are present
                        if not len(set(command_arguments.keys()) & command.required_parameters) == len(
                                command.required_parameters):
                            await message.channel.send(f"Lacking Required Parameters!\n"
                                                       f"You are missing the parameters:\n"
                                                       f"{', '.join(command.required_parameters)}")
                            return

                        async with message.channel.typing():
                            try:
                                await command.run(
                                    self,
                                    group,
                                    message,
                                    blib.map_aliases(
                                        command_arguments,
                                        command.aliases
                                    ))
                            except Exception as e:
                                await message.channel.send(f"{type(e).__name__}: {str(e)}")

        self.client = Client()

        task_dict = {
            "on_connect": [
                status.run(self.client, "In Testing"),
                persistentstorageautoupdate.run(self.client)
            ]
        }

        default_prefix = ","

        # Commands are imported here to create separate instances for each bot
        from commands import ping, setprefix, helpcommand

        command_dict = {
            "ping": ping,
            "prefix": setprefix,
            "setprefix": setprefix,
            "changeprefix": setprefix,
            "help": helpcommand
        }

        actions_dict = {
            "on_message": {
            }
        }

        string_separator = " "
