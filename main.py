from pynput.keyboard import Key, Controller
import os  # for importing env vars for the bot to use
from twitchio.ext import commands
from dataclasses import dataclass
from typing import List, Any, Dict
import json
import asyncio
from collections import Counter
import time
import random


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


CLEAR_COMMAND = "clear"


class VoteCounter:
    def __init__(self, options):
        self.votes = {}
        self.options = set([option.lower() for option in options])
        self.options.add(CLEAR_COMMAND.lower())

    def is_option(self, option):
        return option.lower() in self.options

    def vote(self, user, vote):
        self.votes[user.lower()] = vote.lower()

    def clear_votes(self):
        self.votes.clear()

    def select_winner(self):
        if not self.votes:
            return CLEAR_COMMAND
        counter = Counter(self.votes.values())
        highest_count = max([count for key, count in counter.most_common()])
        highest_voted = []
        for key, count in counter.most_common():
            if count == highest_count:
                highest_voted.append(key)
        return random.choice(highest_voted)


class Bot(commands.Bot):
    def __init__(self, irc_token, client_id, nick, prefix,
                 initial_channels, config, timeout):
        super().__init__(irc_token=irc_token, client_id=client_id, nick=nick, prefix=prefix,
                         initial_channels=initial_channels)
        self.snap_controller = KeyboardController(config)
        self.vote_counter = VoteCounter(self.snap_controller.print_content())
        self.vote_timeout = timeout
        self.last_face_vote = time.monotonic() - self.vote_timeout
        self.last_used_face = None

    async def event_ready(self):
        print(f"{os.environ['BOT_NICK']} is online!")
        ws = bot._ws
        await ws.send_privmsg(os.environ['CHANNEL'], f"/me has landed!")

    async def event_message(self, ctx):
        # make sure the bot ignores itself and the streamer
        if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
            pass
        else:
            if self.vote_counter.is_option(ctx.content.strip()):
                self.vote_counter.vote(ctx.author.name, ctx.content.strip())
            await self.handle_commands(ctx)

    @commands.command(name='face')
    async def my_command(self, ctx):
        print("Starting voting")

        now = time.monotonic()
        difference = abs(now - self.last_face_vote)
        if difference <= self.vote_timeout:
            print("Voting is timed out")
            await ctx.send(f"You need to wait {int(self.vote_timeout - difference)} seconds more")
            return

        if self.last_used_face is not None:
            try:
                self.snap_controller.execute(self.last_used_face)
            except:
                pass

        self.last_face_vote = now
        self.vote_counter.clear_votes()

        # construct message
        await ctx.send("You have 30 seconds to vote")
        message = ""
        for option in self.snap_controller.print_content():
            message += option + ", "
        await ctx.send("Possible options: {}".format(message))
        print("Waiting 30 seconds for votes")
        await asyncio.sleep(30)
        winner = self.vote_counter.select_winner()

        self.last_used_face = winner

        await ctx.send("Votes have been counted!")
        await ctx.send("Winner is {}".format(winner))
        try:
            if winner != CLEAR_COMMAND:
                self.snap_controller.execute(winner)
        except:
            print("Failed to execute snap command")
        # await ctx.send(f'Face changed!')


if __name__ == "__main__":
    bot = Bot(
        # set up the bot
        irc_token=os.environ['TMI_TOKEN'],
        client_id=os.environ['CLIENT_ID'],
        nick=os.environ['BOT_NICK'],
        prefix=os.environ['BOT_PREFIX'],
        initial_channels=[os.environ['CHANNEL']],
        config=ConfigMap.load("config.json"),
        timeout=float(os.environ['VOTE_TIMEOUT']),
    )

    bot.run()
