#!/usr/bin/env python

# note: we are using pipenv and python 3.6.1
from sys import stdout
import json
from bottle import request, route, run, get, post
from logging import basicConfig, debug, info, warning, DEBUG
from collections import namedtuple

basicConfig(filename='matchmakingserver.log', level=DEBUG)

class Match:    
    """ match data container """

    matches = []

    def __init__(self, gamename, password, max_players, server_address, server_port):
        """ initialise a new match """
        self.gamename = gamename        
        self.max_players = max_players
        self.player_count = 0
        self.server_address = server_address
        self.server_port = server_port
        self.server_password = password
        debug("create new match: " + str(self))
        Match.matches.append(self)
    
    def request_join(self, _password, _ip):
        """ request join to the server """
        debug("join requested from: " + _ip)
        if(self.server_password == _password):
            debug("join successful for " + _ip)
            return "" + str(self.server_address) + ":" + str(self.server_port)
        else:
            debug("join failed for " + _ip)
            return "incorrect server password"

    @staticmethod
    def join_match(name, password, _ip):
        """ join a match by name, returns server info if the password is correct """
        debug("finding match for " + _ip)

        for match in Match.matches:
            if match.gamename == name:
                return match.request_join(password, _ip)

        return "match not found"

    def server_info(self):        
        match_info = {}
        match_info['name'] = self.gamename
        match_info['max_players'] = self.max_players
        match_info['players'] = self.player_count
        
        return match_info

    def __str__(self):
        output_str = []
        output_str.append("Game: " + self.gamename)
        output_str.append(", max players: " + self.max_players)
        output_str.append(", player count: " + str(self.player_count))
        output_str.append(", address: " + self.server_address)
        output_str.append(", port: " + str(self.server_port))
        output_str.append(", password: " + self.server_password)
        return "".join(output_str)


@route('/')
def index():
    return "server is up"

#
# Debug forms for testing purposes
# remove them in production use
DEBUG = False
if DEBUG:
    @get('/matchmaking/create')
    def create_match_debug():
        """ this is for debugging purposes, returns manual forms for testing the server out """
        return '''
            <h3>Game info</h3>
            <form action="/matchmaking/create" method="post">
                Name: <input name="name" type="text" />
                Password: <input name="password" type="password" />
                Players: <input name ="maxplayers" type="number" value=10/>
                Port: <input name ="port" type="number" value="27015"/>
                Address: <input name ="address" type="text" value="192.168.0.1"/>
                <input value="Create Game" type="submit" />
            </form>
        '''

    @get('/matchmaking/join')
    def join_match_debug():
        return '''
            <h3>Game info</h3>
            <form action="/matchmaking/join" method="post">
                Name: <input name="name" type="text" />
                Password: <input name="password" type="password" />
                <input value="Join Game" type="submit" />
            </form>
        '''

#
# Matchmaking functions
#

@get('/matchmaking/list') 
def list_matches():
    return "{\"servers\":" + json.dumps([match.server_info() for match in Match.matches]) + "}"


@post('/matchmaking/create')
def create_match():
    debug("match requested")
    gamename = request.forms.get('name')
    password = request.forms.get('password')
    count = request.forms.get('maxplayers')
    address = retrieve_ip()
    port = request.forms.get('port')

    # create the match - will be stored internally automatically
    game = Match(gamename, password, count, address, port)
    debug("match created, returning info!")
    return "" + str(game)


def retrieve_ip():
    return request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')


@post('/matchmaking/join')
def join_game():
    gamename = request.forms.get('name')
    password = request.forms.get('password')
    # HTTP_X_FORWARDED_FOR is a proxy check, if it returns null the REMOTE_ADDR is used.
    ip = retrieve_ip()
    
    return Match.join_match(gamename, password, ip)




run(host='localhost', port=27015, debug=False)
