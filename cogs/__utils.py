from discord.ext import commands

channel_list = [
    867298168492261376,
    686598604340592640,
    798224036977967126
]

def is_approved_channel():
    def predicate(ctx):
        return ctx.channel.id in channel_list

    return commands.check(predicate) 