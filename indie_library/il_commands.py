import random
from indie_library.il import Node
import pickle

from indie_utils import logger

nodes = {}
indie_library: Node = Node("il").load("il.node")
il_loaded = False
focii = {}
cmd_line: str = "IL:"


greetings = {
    1: "Hi there, {0}! Glad to see you.",
    2: "Hello, {0}! Nice weather we're having on Indie Academy, hey?",
    3: "Um. No, {0}. I don't know you. Sorry. Bye."
}


def initialize_il_commands(bot):

    @bot.command(name="write")
    @logger("il")
    async def write(ctx, *args):
        author = ctx.message.author.id
        author_name = str(ctx.message.author)
        global indie_library, focii
        if indie_library.get_node(focii[author_name][:1]).get_name() != author_name:
            await ctx.message.channel.send("<@" + str(author) + ">, you can only write under your own name, try .login to go there.")

        try:
            at_node: Node = indie_library.get_node(focii[author_name])
        except:
            await ctx.message.channel.send(author + ", you must .login first. Obviously.")
        string_to_write = ""
        for arg in args:
            string_to_write += " " + arg
        at_node.write("    " + string_to_write)
        indie_library.save()
        await ctx.message.channel.send(indie_library.get_node_address(focii[author_name]).replace("il.node", "IL:\\") + ">")

    @bot.command(name="read", aliases=["print", "show", "display", "see"])
    @logger("il")
    async def read(ctx, *args):
        author = ctx.message.author.id
        author_name = str(ctx.message.author)
        global indie_library, focii
        try:
            at_node: Node = indie_library.get_node(focii[author_name])
        except:
            await ctx.message.channel.send("<@" + str(author) + ">, you must .login first.")
        string_to_return = at_node.read()
        string_to_return += "\n<@" + str(author) + ">\n" + indie_library.get_node_address(focii[author_name]).replace("il.node",
                                                                                                              "IL:\\") + ">"
        await ctx.message.channel.send(string_to_return)

    @bot.command(name="add", aliases=["addnode", "add_node"])
    @logger("il")
    async def add_node(ctx, *args):
        string_to_return = ""
        author = ctx.message.author.id
        author_name = str(ctx.message.author)
        global indie_library, focii
        if indie_library.get_node(focii[author_name][:1]).get_name() != author_name:
            await ctx.message.channel.send(author + ", you can only change things under your own name, try .login to go there.")
        try:
            at_node: Node = indie_library.get_node(focii[author_name])
        except:
            await ctx.message.channel.send("<@" + str(author) + ">, you must .login first. Obviously.")
        for arg in args:
            at_node.add_node(Node(arg))
            string_to_return += "Added node '" + arg + "'...\n"
        string_to_return += indie_library.get_node_address(focii[author_name]).replace("il.node", "IL:\\") + ">"
        indie_library.save()
        await ctx.message.channel.send(string_to_return)

    @bot.command(name="delete", aliases=["remove", "rmv", "kill"])
    @logger("il")
    async def rem_nodes(ctx, *args):
        author = ctx.message.author.id
        author_name = str(ctx.message.author)
        global indie_library, focii
        if indie_library.get_node(focii[author_name][:1]).get_name() != author_name:
            await ctx.message.channel.send("<@" + str(author) + ">, you can only change things under your own name, try .login to go there.")
        string_to_return = ""
        try:
            at_node: Node = indie_library.get_node(focii[author_name])
        except:
            await ctx.message.channel.send("<@" + str(author) + ">, you must .login first. Obviously.")
        for arg in args:
            string_to_return += rem_node(author, author_name, arg)
        string_to_return += "IL:\\" + indie_library.get_node_address(focii[author_name])[7:] + ">"
        await ctx.message.channel.send(string_to_return)

    def rem_node(author, author_name, name: str):
        global indie_library, focii
        try:
            at_node: Node = indie_library.get_node(focii[author_name])
        except:
            return "<@" + str(author) + ">, you must .login first. Obviously."
        if at_node.has_node(name):
            at_node.kill_node(name)
        indie_library.save()
        string_to_return = "Removing node '" + name + "'\n"
        return string_to_return

    @bot.command(name="back", aliases=["goback", "go_back"])
    @logger("il")
    async def go_back(ctx, *args):
        author = ctx.message.author.id
        author_name = str(ctx.message.author)
        global indie_library, focii
        try:
            at_node: Node = indie_library.get_node(focii[author_name])
        except:
            await ctx.message.channel.send("<@" + str(author) + ">, you must .login first. Obviously.")
        focii[author_name] = focii[author_name][:-1]
        await ctx.message.channel.send(indie_library.get_node_address(focii[author_name]).replace("il.node", "IL:\\") + ">")

    @bot.command(name="node", aliases=["cd", "into", "gointo", "go_into"])
    @logger("il")
    async def go_into(ctx, *args):
        author = ctx.message.author.id
        author_name = str(ctx.message.author)
        global indie_library, focii
        try:
            at_node: Node = indie_library.get_node(focii[author_name])
        except:
            await ctx.message.channel.send("<@" + str(author) + ">, you must .login first. Obviously.")
        if at_node.has_node(args[0]):
            focii[author_name] = at_node.get_node_in_node(args[0]).get_address()
        await ctx.message.channel.send(indie_library.get_node_address(focii[author_name]).replace("il.node", "IL:\\") + ">")

    @bot.command(name="dir", aliases=["nodes", "look", "whatsinhere", "inhere", "here"])
    @logger("il")
    async def nodes(ctx, *args):
        author = ctx.message.author.id
        author_name = str(ctx.message.author)
        global indie_library, focii
        at_node: Node = Node("")
        try:
            at_node = indie_library.get_node(focii[author_name])
        except:
            await ctx.message.channel.send("<@" + str(author) + ">, you must .login first. Obviously.")
        string_to_return = "Nodes here are:\n"
        for node in at_node.get_nodes():
            string_to_return += "    " + node.get_name() + "\n"
        string_to_return += indie_library.get_node_address(focii[author_name]).replace("il.node", "IL:\\") + ">"
        await ctx.message.channel.send(string_to_return)

    @bot.command(name="login", aliases=["load"])
    @logger("il")
    async def login(ctx, *args):
        author = ctx.message.author.id
        author_name = str(ctx.message.author)
        global indie_library, focii
        try:
            with open("il.node", 'rb') as load_file:
                indie_library = pickle.load(load_file)
        except:
            indie_library = Node("il.node")
        if not indie_library.has_node(author_name):
            indie_library.add_node(Node(author_name))
        focii[author_name] = indie_library.get_node_in_node(author_name).get_address()
        indie_library.save()
        await ctx.message.channel.send(indie_library.get_node_address(focii[author_name]).replace("il.node", "IL:\\") + ">")

    @bot.command(name="hi", aliases=["hello", "howareyou", "hiya", "hey", "yo"])
    @logger("il")
    async def hi(ctx, *args):
        author = ctx.message.author.id
        print("saying hi")
        global greetings
        await ctx.message.channel.send(greetings[random.randint(1, 3)].format(str(author)))

