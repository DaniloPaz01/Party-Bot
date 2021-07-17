import mysql.connector

def create_connection(host_name,user_name,user_password,db_name):
    connection = None
    try:
        connection = mysql.connector.connect(host=host_name,
                                             user=user_name,
                                             password=user_password,
                                             database=db_name,
                                             port='3306')
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("Your connected to database: ", record)
    except Exception as error:
        print('the error {}'.format(error))
    return connection

def get_games(connection):

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM game"
            cursor.execute(query)
            games = cursor.fetchall()
            games_dic = dict()
            for game in games:
                games_dic[game.get('title')] = game.get('icon')
    
        return games_dic

def get_game_to(connection,game_icon):

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT game.title FROM game WHERE game.icon = '{}' ".format(game_icon)
            cursor.execute(query)
            game_name = cursor.fetchall()
        return(game_name[0].get('title'))


def get_ranks_to(connection,game_title):
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT mmr.mmr_name , mmr.mmr_icon FROM mmr WHERE mmr.title = '{}' ".format(game_title)
            cursor.execute(query)
            games_rank = cursor.fetchall()
            print(games_rank)
            games_dic = dict()
            for game in games_rank:
                games_dic[game.get('mmr_name')] = game.get('mmr_icon')
            return(games_dic)
    
def insert_into_player(connection,player_id,player_name,player_guild):
    if connection.is_connected():
            cursor = connection.cursor()
            #"INSERT INTO player(id,player_name,guild) VALUES('{}','{}','{}')".format(5433,'WHISPER','paFIN')
            query = "INSERT INTO player(id,player_name,guild) VALUES('{}','{}','{}')".format(player_id,player_name,player_guild)
            cursor.execute(query)
            connection.commit()

def insert_into_plays(connection,
                       player_id,
                       player_name,
                       player_guild,
                       game_title,
                       game_icon,
                       rank_name,
                       rank_icon):
    if connection.is_connected():
            cursor = connection.cursor()
            query = "INSERT INTO plays VALUES ({},'{}','{}','{}','{}','{}','{}')".format(player_id,
                                                                                        player_name,
                                                                                        player_guild,
                                                                                        game_title,
                                                                                        game_icon,
                                                                                        rank_name,
                                                                                        rank_icon)
            cursor.execute(query)
            connection.commit()