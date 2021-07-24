
from os import name
import discord
from discord.member import Member
from discord.mentions import AllowedMentions
from database import get_games,get_game_to,get_ranks_to,create_connection,get_mmr_title,insert_new_player,get_games_from_user_and_guild,get_ranks_from_user_and_guild,find_players,update_mmr
from discord.ext import commands

mentions = discord.AllowedMentions(everyone=True, users=True, roles=True, replied_user=True)

#this enables sthe bot to track de members activity and current status
intents = discord.Intents.all()

token = ""

bot = commands.Bot(command_prefix='$',intents=intents,AllowedMentions=mentions)
connector = None
try:
    connector = create_connection('localhost','root','root','bot')
except Exception as error:
    print('db not available {}'.format(error))

def create_embed_with_title_from(a_title,a_dict_with_icons):
    """it creates an embeded message with a title and a dict which items are the name of  the game and it's icon"""
    embed = discord.Embed(title=a_title.capitalize(),color=0xe67e22)
    for game,emoji in a_dict_with_icons.items():
        embed.add_field(name = game.capitalize(), value= emoji, inline = True)
    return embed

def show_players_activity(a_guild):
    """sends a message to the context channel with the activity of the server members"""
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
    

@bot.event
async def on_voice_state_update(member, before, after):

    #these are the channels that needs to be targeted
    channel_names = ['csgo','overwatch','dota','lol','valorant']

    #we check that before is not none,otherwise it means that we have entered a channel
    if before.channel:

        #if there are no members and the channel is one of the targeted then we can delete it
        if before.channel.name.lower() in channel_names and len(before.channel.members) == 0:
            await before.channel.delete()

@bot.command()
async def party(context):

    #we display all games 
    games_from_db = get_games(connector)
    embed = create_embed_with_title_from('Select a game for your party',games_from_db)
    embed.set_author(name=context.author.name,icon_url=context.author.avatar_url)
    game_selection = await context.channel.send(embed=embed,delete_after=60)
    for icon in games_from_db.values():
        await game_selection.add_reaction(icon)

    def check(reaction, user):
        return not(user.bot) and user == context.author and reaction.message == game_selection and str(reaction.emoji) in games_from_db.values()

    game_icon,player = await bot.wait_for('reaction_add',check=check)
    game_title = get_game_to(connector,game_icon)

    #we make the message to the members of the guild
    #allowed_mentions = discord.AllowedMentions(everyone = True)
    party_embed = discord.Embed(title='is creating a party for: ' + game_title.capitalize(), color=0xe67e22)
    party_embed.set_author(name=context.author.name, icon_url=context.author.avatar_url)
    party_message = await context.channel.send(content="@everyone", embed=party_embed)
    await party_message.add_reaction(game_icon)
    
    #we make an empty list in which the players will be added if they react to the message
    player_waitlist = []

    def check_users(reaction, user):
        return not(user.bot) and reaction.message == party_message and str(reaction.emoji) in games_from_db.values()

    while True:
        reaction, player = await bot.wait_for('reaction_add', check=check_users)
        player_waitlist.append(player)

        new_embed = party_message.embeds.pop()
        new_embed.add_field(name=player.name, value='has joined the party')
        await party_message.edit(embed=new_embed)

        if len(player_waitlist) == 2:
            break
    
    #we create a voice channel for that game and an invitation 
    voice = await context.guild.create_voice_channel(name=game_title, user_limit=5)
    invite = await voice.create_invite()

    for p in player_waitlist:
        await p.send(invite)
    
@bot.command()
async def games(context):
    embed = create_embed_with_title_from('Our games',get_games(connector))
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
async def find(context):

    games_from_db = get_games(connector)
    embed = create_embed_with_title_from('Select a game',games_from_db)
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
    embed_mmr.set_author(name="Now select a rank",icon_url=context.author.avatar_url)
    mmr_selection = await context.author.send(embed=embed_mmr,delete_after=60)
    for icon_mmmr in game_mmr.values():
             await mmr_selection.add_reaction(icon_mmmr)

    def check_mmr_selected(reaction, user):

        if context.author == user and reaction.message == mmr_selection and not(user.bot):
            if (str(reaction.emoji) in game_mmr.values()):
                return (reaction.emoji,user)
                  
    game_mmr_icon, _ = await bot.wait_for('reaction_add',check=check_mmr_selected)
    mmr_title = get_mmr_title(connector,game_mmr_icon)
    players = find_players(connector,context.guild,game_title,mmr_title)
    if players:
        player_embed = discord.Embed(title='Found them',color=0xe67e22)
        player_embed.add_field(name='Total gamers found',value= len(players))
        mention_string = ''
        for player_id in players:
            mention_string += '<@!{}> \n'.format(player_id)
        await context.channel.send(embed=player_embed)
        await context.channel.send(mention_string)
    else:
        await context.channel.send('Nothing found')

@bot.command()
async def add(context):

    #we get all the games available
    games_from_db = get_games(connector)

    #now we create an embeded message with the titles and icons
    embed = create_embed_with_title_from('Select your games', games_from_db)
    embed.set_author(name=context.author.name, icon_url=context.author.avatar_url)
    game_selection = await context.author.send(embed=embed, delete_after=60)
    for icon in games_from_db.values():
        await game_selection.add_reaction(icon)

    def check_game(reaction, user):
        return not(user.bot) and user == context.author and reaction.message == game_selection and str(reaction.emoji) in games_from_db.values()

    #we get the icon and the player who reacted to the message
    game_icon, player = await bot.wait_for('reaction_add', check=check_game)

    #we get the  name of the game which icon belongs to
    game_title = get_game_to(connector, game_icon)

    #then we get the ranks of that game
    game_mmr = get_ranks_to(connector, game_title)
    
    #finally we create a new embed message which the names and icons of the game ranks
    embed_mmr = create_embed_with_title_from(game_title, game_mmr)
    embed_mmr.set_author(name="Now select your MMR", icon_url=context.author.avatar_url)
    mmr_selection = await context.author.send(embed=embed_mmr, delete_after=60)
    for icon in game_mmr.values():
             await mmr_selection.add_reaction(icon)

    def check_mmr(reaction, user):
        return context.author == user and reaction.message == mmr_selection and not(user.bot) and (str(reaction.emoji) in game_mmr.values())
                  
    icon_mmr, _ = await bot.wait_for('reaction_add', check=check_mmr)
    mmr_title = get_mmr_title(connector, icon_mmr)
    insert_new_player(connector, player.id, player.name, context.guild, game_title, game_icon, mmr_title, icon_mmr)
    
@bot.command()
async def update(context):

    #first we get the games of the caller of this command
    my_games = get_games_from_user_and_guild(connector,context.author.id,context.guild)

    #as we did before we create a new embed message
    embed = create_embed_with_title_from('Select a game to update',my_games)
    embed.set_author(name=context.author.name,icon_url=context.author.avatar_url)
    game_selection = await context.author.send(embed=embed)
    for game_icon in my_games.values():
        await game_selection.add_reaction(game_icon)
    
    def check_update(reaction, user):
        return not(user.bot) and user == context.author and reaction.message == game_selection and str(reaction.emoji) in my_games.values()

    game_icon,player = await bot.wait_for('reaction_add', check=check_update)
    game_title = get_game_to(connector, game_icon)
    game_mmr = get_ranks_to(connector, game_title)

    #now we display the available ranks
    embed_mmr = create_embed_with_title_from(game_title, game_mmr)
    embed_mmr.set_author(name="Now select your new MMR", icon_url=context.author.avatar_url)
    mmr_selection = await context.author.send(embed=embed_mmr, delete_after=60)
    for icon_mmmr in game_mmr.values():
             await mmr_selection.add_reaction(icon_mmmr)

    def check_mmr_selected(reaction, user):
        return context.author == user and reaction.message == mmr_selection and not(user.bot) and (str(reaction.emoji) in game_mmr.values())
                  
    game_mmr_icon, _ = await bot.wait_for('reaction_add',check=check_mmr_selected)
    mmr_title = get_mmr_title(connector,game_mmr_icon)
    update_mmr(connector,context.guild,player.name,game_title,mmr_title,game_mmr_icon)

bot.run(token)