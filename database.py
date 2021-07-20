import mysql.connector
import sys

#sys.path.append('./')
#print(sys.path)

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
                games_dic[game.get('game_title')] = game.get('game_icon')
    
        return games_dic

def get_game_to(connection,game_icon):

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT game_title FROM game WHERE game_icon = '{}' ".format(game_icon)
            cursor.execute(query)
            game_name = cursor.fetchall()
        return game_name[0].get('game_title')


def get_ranks_to(connection,game_title):
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT mmr_name , mmr_icon FROM mmr WHERE mmr.game_title = '{}' ".format(game_title)
            cursor.execute(query)
            games_rank = cursor.fetchall()
            print(games_rank)
            games_dic = dict()
            for game in games_rank:
                games_dic[game.get('mmr_name')] = game.get('mmr_icon')
            return(games_dic)
    
def get_mmr_title(connection,a_mmr_icon):
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        query = "SELECT mmr_name FROM mmr WHERE mmr.mmr_icon = '{}'".format(a_mmr_icon)
        cursor.execute(query)
        mmr_name = cursor.fetchall()
        return mmr_name[0].get('mmr_name')