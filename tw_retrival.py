# -*- coding: utf-8 -*-

import math 
import numpy as np
import random
import argparse
import json
import csv

import tweepy
import pandas as pd

__CONSUMER_KEY__        = 'tgs8wgT43E431LTDKMNaX2si1'
__CONSUMER_SECRET__     = 'sxa6lxqN2qjdqZ9EUShNRhgaE0Rk9IpCCaUY6n55TaTSF4lubA'
__ACCESS_TOKEN__        = '895734806163607552-gWPIn4EIPmONp7dsPzB6mxcYIgkkSHh'
__ACCESS_TOKEN_SECRET__ = '9TukCQG99DVKwCTCkxfyxkv78nXqQ4XsRInqQDlYROq4F'

# Etiquetar una persona en un comentario con api.search.

class RegistroTwiter(object):
    def __init__(self,
                 id = None,
                 text = None,
                 likes = None,
                 cant_tweets = None,
                 lang = None,
                 replies = None):
        self.id = id
        self.text = text
        self.likes = likes
        self.cant_tweets = cant_tweets
        self.lang = lang     
        self.replies = replies

    @classmethod
    def init_by_status(cls, status):
        return cls(status.id_str,
                   status.text,
                   status.favorite_count,
                   status.retweet_count,
                   status.lang,
                   status.in_reply_to_status_id_str,)

    def to_dict(self):
        return self.__dict__

class ModeloConectorTwiter(object):
    def __init__(self,
                 consumer_key = __CONSUMER_KEY__,
                 consumer_secret = __CONSUMER_SECRET__,
                 access_token = __ACCESS_TOKEN__,
                 access_token_secret = __ACCESS_TOKEN_SECRET__):
        self.__consumer_key        = consumer_key       
        self.__consumer_secret     = consumer_secret    
        self.__access_token        = access_token       
        self.__access_token_secret = access_token_secret
        self.__api = self.__conectar_api()

    def __conectar_api(self):
        auth = tweepy.OAuthHandler(self.__consumer_key, self.__consumer_secret)
        auth.set_access_token(self.__access_token, self.__access_token_secret)
        api = tweepy.API(auth)
        if not api:
            raise ErrorConexion('Problema de conexión a la API')
        else:
            return api # api.me().name

    def obtener_estadisticas_usuario(self, user_name):
        # user_name de la forma @<nombre de usuario>
        data = self.__api.get_user(user_name[1:])
        res = {
            'followers'		: data.followers_count,
            'tweets'    	: data.statuses_count,
            'favourites'	: data.favourites_count,
            'friends'		: data.friends_count,
            'list_appears'	: data.listed_count,
        }
        return pd.DataFrame.from_dict(res, orient='index')


    # def recuperar_tweets_usuario(self, user_name, cant_tweets=15):
    #     res = { status.id_str : { 'text':status.text, 'likes' : status.favorite_count, 'cant_tweets' : status.retweet_count, 'lang' : status.lang }
    #     for status in tweepy.Cursor(self.__api.user_timeline, screen_name = user_name[1:], count = cant_tweets, include_rts = True).items(cant_tweets) }
    #     return pd.DataFrame.from_dict(res, orient='index')

    def recuperar_tweets_usuario(self, user_name, cant_tweets=15):
        res = { status.id_str : RegistroTwiter.init_by_status(status).to_dict() for status in
                tweepy.Cursor(self.__api.user_timeline, screen_name = user_name[1:], count = cant_tweets, include_rts = True).items(cant_tweets) }
        return pd.DataFrame.from_dict(res, orient='index')


    def recuperar_interaccion_usuario(self, user_name, cant_tweets=15, cant_replies=1000):
        res = dict()
        respuestas = dict()
        for status in tweepy.Cursor(self.__api.user_timeline, screen_name = user_name[1:], count = cant_tweets, include_rts = True).items(cant_tweets):
            res[status.id_str] = RegistroTwiter.init_by_status(status).to_dict()
            search_dict = {
                'since_id' : status.id_str,
                'count' : cant_replies,
            }
            for s in tweepy.Cursor(self.__api.search, q = "to:"+user_name[1:], **search_dict).items(cant_replies):
                if s.in_reply_to_status_id_str == status.id_str or s.in_reply_to_status_id == status.id:
                    respuestas[s.id_str] = RegistroTwiter.init_by_status(s).to_dict()
        return pd.DataFrame.from_dict(res, orient='index'), pd.DataFrame.from_dict(respuestas, orient='index')

    def obtener_tweets_tag(self, tag_name, cant_tweets=15):
        res = dict()
        search_dict = {
            'count' : cant_tweets,
        }
        for s in tweepy.Cursor(self.__api.search, q = tag_name, **search_dict).items(cant_tweets):
            res[s.id_str] = RegistroTwiter.init_by_status(s).to_dict()
        return pd.DataFrame.from_dict(res, orient='index')


class ErrorConexion(Exception):
    def __init__(self, message, errors = 500):
        super(ErrorConexion, self).__init__(message)
        self.errors = errors


if __name__ == '__main__':
    connector = ModeloConectorTwiter()
    commands = {
        'estadisticas' : connector.obtener_estadisticas_usuario,
        'tweets' : connector.recuperar_tweets_usuario,
        'interacion' : connector.recuperar_interaccion_usuario,
        'etiqueta' : connector.obtener_tweets_tag,
    }
    # crear el parser del mas alto nivel.
    parser = argparse.ArgumentParser(prog='Interfaz de programación para Twitter')

    subparsers = parser.add_subparsers(dest='command', help='Tipos de comandos.')
    # crear el parser para el comando "estadisticas"
    parser_estadisticas = subparsers.add_parser('estadisticas', help='Obtiene una serie de estadísticas dado el usuario.')
    parser_estadisticas.add_argument('user_name', type=str, help='Nombre de usuario dado por la forma @<nombre usuario>.')
    
    # crear el parser para el comando "tweets"
    parser_tweets = subparsers.add_parser('tweets', help='Obtener los tweets de un usuario y sus estadisticas.')
    parser_tweets.add_argument('user_name', type=str, help='Nombre de usuario dado por la forma @<nombre usuario>.')
    parser_tweets.add_argument('cant_tweets', type=int, nargs='?', default=15, help='Cantidad de tweets de usuario recuperados.')

    # crear el parser para el comando "interacion"
    parser_interacion = subparsers.add_parser('interacion', help='Obtener los tweets de un usuario, sus estadisticas y las replicas de los mismos.')
    parser_interacion.add_argument('user_name', type=str, help='Nombre de usuario dado por la forma @<nombre usuario>.')
    parser_interacion.add_argument('cant_tweets', type=int, nargs='?', default=15, help='Cantidad de tweets de usuario recuperados.')
    parser_interacion.add_argument('cant_replies', type=int, nargs='?', default=15, help='Cantidad de replies sobre los tweets de usuario recuperados.')
    
    # crear el parser para el comando "etiqueta"
    parser_etiqueta = subparsers.add_parser('etiqueta', help='Obtener los tweets de un usuario y sus estadisticas.')
    parser_etiqueta.add_argument('tag_name', type=str, help='Etiqueta de un tópico ,tema o persona dado por la forma #<nombre> o @<nombre>.')
    parser_etiqueta.add_argument('cant_tweets', type=int, nargs='?', default=15, help='Cantidad de tweets de usuario recuperados.')

    # parse some argument lists
    args = vars(parser.parse_args())
    cmd = args.pop('command')
    print "%s" % [commands[cmd](**args)]


# http://tweepy.readthedocs.io/en/v3.5.0/auth_tutorial.html#auth-tutorial
# https://github.com/bear/python-twitter
# https://stackoverflow.com/questions/35921662/twitter-api-how-to-get-real-time-tweets-by-user
# http://pythoncentral.io/introduction-to-tweepy-twitter-for-python/
# https://www.slickremix.com/docs/how-to-get-api-keys-and-tokens-for-twitter/
# http://codygo.es/redes-sociales/conseguir-las-consumer-key-y-access-token-de-twitter/
# https://www.digitalocean.com/community/tutorials/how-to-authenticate-a-python-application-with-twitter-using-tweepy-on-ubuntu-14-04

# http://www.dealingdata.net/2016/07/23/PoGo-Series-Tweepy/
# https://cmry.github.io/notes/twitter-python
# https://www.dataquest.io/blog/streaming-data-python/
# http://www.programcreek.com/python/example/76301/tweepy.Cursor
# https://stackoverflow.com/questions/38923298/does-tweepy-handle-rate-limit-code-429
# https://rstudio-pubs-static.s3.amazonaws.com/129875_b0ce4a962a0c4fa8af53c62d239f30df.html