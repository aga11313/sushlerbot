from pynput.keyboard import Key, Controller
import os  # for importing env vars for the bot to use
from twitchio.ext import commands
from dataclasses import dataclass
from typing import List, Any, Dict
import json
import asyncio
from collections import defaultdict


class ConfigMap:
    def __init__(self, data):
        self.data = data

    def get_combo(self, key):
        return self.data.get(key, None)

    @staticmethod
    def load(path):
        with open(path, "r") as f:
            text = f.read()
            deserailized = json.loads(text)
            return ConfigMap(data=deserailized)

    def print_content(self):
        return list(self.data.keys())


class KeyboardController:
    def __init__(self, config: ConfigMap):
        self.config = config
        self.static = [Key.ctrl, Key.shift]
        self.controller = Controller()

    def execute(self, command_id: str):
        for key in self.static:
            self.controller.press(key)
        try:
            key = self.config.get_combo(command_id)
            self.controller.press(key)
            self.controller.release(key)
        except:
            pass
        for key in self.static:
            self.controller.release(key)

    def print_content(self):
        return self.config.print_content()


class Bot(commands.Bot):
    def __init__(self, irc_token, client_id, nick, prefix,
                 initial_channels, config):
        super().__init__(irc_token=irc_token, client_id=client_id, nick=nick, prefix=prefix,
                         initial_channels=initial_channels)
        self.snap_controller = KeyboardController(config)
        self.count_dict = defaultdict(lambda: 0)
        self.set_of_face_options = set(self.snap_controller.print_content())

    async def event_ready(self):
        print(f"{os.environ['BOT_NICK']} is online!")
        ws = bot._ws
        await ws.send_privmsg(os.environ['CHANNEL'], f"/me has landed!")

    async def event_message(self, ctx):
        # make sure the bot ignores itself and the streamer
        if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
            print("it's me")
        else:
            print("some message", ctx.content)
            if ctx.content.strip() in self.set_of_face_options:
                self.count_dict[ctx.content.strip()] += 1
            await self.handle_commands(ctx)

    @commands.command(name='face')
    async def my_command(self, ctx):
        self.count_dict.clear()
        await ctx.send("Possible options: {}".format(self.snap_controller.config.print_content()))
        await asyncio.sleep(10)
        winner = max(self.count_dict.items(), key=lambda a: a[1])[0]
        await ctx.send("Winner is {}".format(winner))
        await ctx.send("Ha! Your time is up!")
        # print("command was", ctx.content.replace('!' + ctx.command.name, ""))
        # args = ctx.content.replace('!' + ctx.command.name, "").strip()
        try:
            self.snap_controller.execute(winner)
        except:
            print("ERRRROROROROROR")
        await ctx.send(f'Face changed!')


if __name__ == "__main__":
    bot = Bot(
        # set up the bot
        irc_token=os.environ['TMI_TOKEN'],
        client_id=os.environ['CLIENT_ID'],
        nick=os.environ['BOT_NICK'],
        prefix=os.environ['BOT_PREFIX'],
        initial_channels=[os.environ['CHANNEL']],
        config=ConfigMap.load("config.json")
    )
    
    bot.run()
