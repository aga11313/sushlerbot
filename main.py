from pynput.keyboard import Key, Controller
import os  # for importing env vars for the bot to use
from twitchio.ext import commands
from dataclasses import dataclass
from typing import List, Any, Dict


@dataclass
class KeyCombo:
    commands: List[Any]


class KeyboardController:
    def __init__(self, commands: Dict[str, KeyCombo]):
        self.commands = commands
        self.controller = Controller()

    def execute(self, command_id: str):
        combo = self.commands[command_id]
        for key in combo.commands:
            self.controller.press(key)


class Bot(commands.Bot):
    def __init__(self, irc_token, client_id, nick, prefix,
                 initial_channels):
        super().__init__(irc_token=irc_token, client_id=client_id, nick=nick, prefix=prefix,
                         initial_channels=initial_channels)
        self.snap_controller = KeyboardController({
                "zebra": KeyCombo([Key.ctrl, Key.shift, '1']),
                "bunny": KeyCombo([Key.ctrl, Key.shift, '2']),
                "deer": KeyCombo([Key.ctrl, Key.shift, '3'])
            })

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
            await self.handle_commands(ctx)

    @commands.command(name='face')
    async def my_command(self, ctx):
        print("command was", ctx.content.replace('!' + ctx.command.name, ""))
        args = ctx.content.replace('!' + ctx.command.name, "").strip()
        try:
            self.snap_controller.execute(args)
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
        initial_channels=[os.environ['CHANNEL']]
    )
    bot.run()

# keyboard = Controller()
# keyboard.press(Key.ctrl)
# keyboard.press(Key.shift)
# keyboard.press('1')

# keyboard.release(Key.ctrl)
# keyboard.release(Key.shift)
# keyboard.release('1')
