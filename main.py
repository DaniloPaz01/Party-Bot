import os
import discord
from database import get_games,get_game_to,get_ranks_to,create_connection,insert_into_plays,insert_into_player
from discord.ext import commands
from games_config import games_with_icons,games_with_mmr

intents = discord.Intents.all()

token = "Here goes the token,for security reasons right now is not available"

bot = commands.Bot(command_prefix='$',intents=intents)
connector = create_connection('localhost','root','root','bot')

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
    print(context.guild)
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
async def add(context):
    print(context.guild)
    games_from_db = get_games(connector)
    embed = create_embed_with_title_from('Select your games',games_from_db)
    embed.set_author(name=context.author.name,icon_url=context.author.avatar_url)
    game_selection = await context.author.send(embed=embed,delete_after=60)
    for icon in games_from_db.values():
        await game_selection.add_reaction(icon)

    def check(reaction, user):
        return not(user.bot) and user == context.author and reaction.message == game_selection and str(reaction.emoji) in games_from_db.values()

    game_icon,player = await bot.wait_for('reaction_add',check=check)
    
    print(game_icon)
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
    print(type(player.id))
    #insert_into_player(connector,player.id,player.name,context.guild.name)
    insert_into_plays(connector,player.id,player.name,context.guild,game_title,str(game_icon.emoji),'hola',str(game_mmr_icon.emoji))
    await context.send(player)
    await context.send(game_icon)
    await context.send(game_mmr_icon)

@bot.command()
async def insert(context):
    print(context.author.id,context.author.name,context.guild.name)
    print(type(context.author.id),type(context.author.name),type(context.guild.name))
    insert_into_player(connector,context.author.id,context.author.name,context.guild.name)  

bot.run(token)