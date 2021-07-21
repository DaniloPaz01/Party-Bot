
import os
import discord
from database import get_games,get_game_to,get_ranks_to,create_connection,get_mmr_title,insert_new_player,get_games_from_user_and_guild,get_ranks_from_user_and_guild
from discord.ext import commands
from games_config import games_with_icons,games_with_mmr

intents = discord.Intents.all()

token = "ODYyOTU2MjgzMzg0OTU0OTAw.YOf4qg.gkWU6mKd6v2CNZFIkyj7wH1hVeM"

bot = commands.Bot(command_prefix='$',intents=intents)
connector = None
try:
    connector = create_connection('localhost','root','root','bot')
except Exception as error:
    print('db not available {}'.format(error))

@bot.command
async def load(context,extension):
    bot.load_extension('cogs.{}'.format(extension))
    pass

@bot.command
async def unload(context,extension):
    bot.unload_extension('cogs.{}'.format(extension))
    pass

def create_embed_with_title_from(a_title,a_dict_with_icons):
    embed = discord.Embed(title=a_title,color=0xe67e22)
    for game,emoji in a_dict_with_icons.items():
        embed.add_field(name = game, value= emoji, inline = True)
    return embed

def show_players_activity(a_guild):
    activity = ''
    for member in (a_guild.members):
        if (member.status != discord.Status.offline) and not(member.bot) and (member.activity):
            activity += '**{}** is playing: **{}** \n'.format(member.name,member.activity.name)
    return activity


@bot.event
async def on_ready():
    print("i'm ready")

@bot.command()
async def who(context):
    try:
        embed = discord.Embed(title="Server activity", description=show_players_activity(context.author.guild),color=0xe67e22)
    except AttributeError as error:
        print(error)
        await context.author.send('This command is only usable on any of your guilds')
    else:
        await context.channel.send(embed=embed)
    

@bot.command()
async def games(context):
    embed = create_embed_with_title_from('Our games',games_with_icons)
    await context.channel.send(embed=embed)

@bot.command()
async def ping(context):
    embed = discord.Embed(title="PING", description=f":ping_pong: Pingpingpingpingping! The ping is **{round(bot.latency *1000)}** milliseconds!", color=0xe67e22)
    await context.channel.send(embed=embed)

@bot.command()
async def my(context):
    my_games = get_games_from_user_and_guild(connector,context.author.id,context.guild)
    embed = create_embed_with_title_from('This are your games',my_games)
    embed.set_author(name=context.author.name,icon_url=context.author.avatar_url)
    await context.channel.send(embed=embed)

@bot.command()
async def rank(context):
    my_ranks = get_ranks_from_user_and_guild(connector,context.author.id,context.guild)
    embed = create_embed_with_title_from('This are your ranks',my_ranks)
    embed.set_author(name=context.author.name,icon_url=context.author.avatar_url)
    await context.channel.send(embed=embed)

@bot.command()
async def clear(context):
    limit = 20
    await context.channel.purge(limit=limit)

@bot.command()
async def add(context):

    games_from_db = get_games(connector)
    embed = create_embed_with_title_from('Select your games',games_from_db)
    embed.set_author(name=context.author.name,icon_url=context.author.avatar_url)
    game_selection = await context.author.send(embed=embed,delete_after=60)
    for icon in games_from_db.values():
        await game_selection.add_reaction(icon)

    def check(reaction, user):
        return not(user.bot) and user == context.author and reaction.message == game_selection and str(reaction.emoji) in games_from_db.values()

    game_icon,player = await bot.wait_for('reaction_add',check=check)
    game_title = get_game_to(connector,game_icon)
    game_mmr = get_ranks_to(connector,game_title)
    
    embed_mmr = create_embed_with_title_from(game_title,game_mmr)
    embed_mmr.set_author(name="Now select your MMR",icon_url=context.author.avatar_url)
    mmr_selection = await context.author.send(embed=embed_mmr,delete_after=60)
    await mmr_selection.add_reaction('<:X_:864075974110216193>')
    for icon_mmmr in game_mmr.values():
             await mmr_selection.add_reaction(icon_mmmr)

    def check_mmr_selected(reaction, user):

        if context.author == user and reaction.message == mmr_selection and not(user.bot):
            if (str(reaction.emoji) in game_mmr.values()):
                return (reaction.emoji,user)
            elif str(reaction.emoji) == '<:X_:864075974110216193>':
                return ('<:X_:864075974110216193>',user)
                  
    game_mmr_icon, _ = await bot.wait_for('reaction_add',check=check_mmr_selected)
    mmr_title = get_mmr_title(connector,game_mmr_icon)
    print(player.id)
    insert_new_player(connector,player.id,player.name,context.guild,game_title,game_icon,mmr_title,game_mmr_icon)
    
bot.run(token)