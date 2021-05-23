import traceback
import random
import discord
from discord.ext import commands

# Math functions, the core of IndieBot
from indie_math import indie_seq, indie_oeis, indie_collatz, indie_pig

mods = []
oeis_in_progress = False


def create_bot_instance(prefix, bot_id):
    global mods
    inst = commands.Bot(command_prefix=prefix)
    with open("dat/mods.csv", "r+") as f:
        for each in f.readlines():
            mods.append(each.replace("\n", ""))
    initialize_events(inst)
    initialize_commands(inst)
    return inst


def initialize_events(bot):

    @bot.event
    async def on_ready():
        await bot.change_presence(activity=discord.Game("around"))
        print("IndieBot is live.")

    @bot.event
    async def on_message(message):
        await bot.process_commands(message)


def initialize_commands(bot):

    def logger(command_type):

        # Encapsulates bot commands for added functionality
        def command_wrapper(command):

            # Where the magic happens. This gives commands more versatility
            async def function_wrapper(ctx):

                def has_permission():
                    global mods
                    if command_type == "modonly" and str(ctx.message.author.id) in mods:
                        return True
                    elif command_type == "all":
                        return True
                    elif command_type == "pig-math":
                        return ctx.message.channel.name == "pig-math" or ctx.message.channel.name == "bot-testing"
                    else:
                        return False

                args = ctx.message.content.split(" ")[1:]
                print("Command used:", command.__name__)
                try:
                    if has_permission():
                        await command(ctx, *args)
                        # Log successful command usage
                        with open("dat/command_log.csv", "a+") as f:
                            f.write(f"{command.__name__},{ctx.message.author.id}\n")
                    else:
                        await ctx.message.add_reaction("❌")
                        print(
                            f"User {ctx.message.author.name} does not have permission to use command {command.__name__}")
                except Exception:
                    await ctx.message.add_reaction("❌")
                    print(traceback.format_exc())

            return function_wrapper

        return command_wrapper

    @bot.command(name="snr")
    @logger("all")
    async def snr(ctx, *args):
        await ctx.message.channel.send(str(indie_seq.Seq([int(k) for k in args]).f()))

    @bot.command(name="oeis")
    @logger("all")
    async def oeis(ctx, *args):
        global oeis_in_progress
        if not oeis_in_progress:
            oeis_in_progress = True
            if len(args) > 0:
                await ctx.message.channel.send(indie_oeis.get_sequence_from_b_file(args[0]))
            else:
                await ctx.message.channel.send(indie_oeis.get_sequence_from_b_file(str(random.randint(1, 341962))))
            oeis_in_progress = False
        else:
            await ctx.message.add_reaction("❌")

    @bot.command(name="collatz")
    @logger("all")
    async def collatz(ctx, *args):
        num = int(args[0])
        inity = "" if len(args) < 2 else args[1]

        collatz_results = indie_collatz.collatz_info(num)
        if len(inity) == 1:
            if inity == "e":
                await ctx.message.channel.send(f"Evenity trajectory of {num}: {collatz_results.evenity_trajectory}")
            elif inity == "o":
                await ctx.message.channel.send(f"Oddinity trajectory of {num}: {collatz_results.oddinity_trajectory}")
        else:
            await ctx.message.channel.send(f"Collatz trajectory of {num}: {collatz_results.collatz_trajectory}")

    @bot.group(name="pig")
    async def pig(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.message.add_reaction("❌")

    def get_user_id_from_mention(user_id):
        user_id = user_id.replace("<", "")
        user_id = user_id.replace(">", "")
        user_id = user_id.replace("@", "")
        user_id = user_id.replace("!", "")
        return user_id

    # Pig Math commands

    @pig.command(name="challenge")
    @logger("pig-math")
    async def challenge(ctx, *args):
        challengee = get_user_id_from_mention(args[1])
        challengee = (await bot.fetch_user(challengee)).name
        if len(args) > 2:
            point_target = int(args[2])
        else:
            point_target = 100
        pig_challenge = indie_pig.PigChallenge.create_challenge(ctx.message.author.name, challengee, point_target)
        await ctx.message.channel.send(pig_challenge.status)

    @pig.command(name="accept")
    @logger("pig-math")
    async def accept(ctx, *args):
        await ctx.message.channel.send(indie_pig.PigChallenge.accept_challenge(ctx.message.author.name))

    @pig.command(name="reject")
    @logger("pig-math")
    async def reject(ctx, *args):
        await ctx.message.channel.send(indie_pig.PigChallenge.reject_challenge(ctx.message.author.name))

    @pig.command(name="roll")
    @logger("pig-math")
    async def roll(ctx, *args):
        await ctx.message.channel.send(indie_pig.PigGame.play(ctx.message.author.name, "roll"))

    @pig.command(name="bank")
    @logger("pig-math")
    async def bank(ctx, *args):
        await ctx.message.channel.send(indie_pig.PigGame.play(ctx.message.author.name, "bank"))
