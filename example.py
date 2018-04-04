import requests
import json
import os
from datatypes import *
from api import *

api = PubgApi()
# currently supported: find a single player by name
# shard is 2nd parameter, default is pc-eu, you can change
# defaults in the api.py file
# By default, local "storage" will also be searched for cached
# files, to disable, pass search_ds=False
player, error = api.get_player("Arican")
if error:
    raise Exception(error)

# xbox is not yet supported because of differences in the api
# player2, error = api.get_player("Back To Boots", 'xbox-na')

match, error = api.get_match(player.matches[0])
if error:
    raise Exception(error)

# print the id of the match
print(match.id)
# print number of teams
print(len(match.rosters))

# print the names of the players of the 2nd team
for x in (match.get_roster_participants(match.rosters[1])):
    print(x.name)

# download the full telemetry for match
telemetry, error = api.get_match_telemetry(match)
if error:
    raise Exception(error)

# example :: print killfeed
for event in telemetry.events:
    if event.event_type == "LogPlayerKill":
        killer = event.killer.name if event.killer.name else event.damage_type_category
        print(killer + " killed " + event.victim.name)
    if event.event_type == "LogMatchEnd":
        print("Match ended, winners are: " + ','.join(map(lambda x: x.name, list(filter(lambda x: x.ranking == 1, event.characters)))))

        
