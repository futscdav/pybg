import requests
import json
import os
from datatypes import *

def make_url(path_list, opts_list=None):
    url = "/".join(path_list)
    if opts_list:
        url = url + "?" + ",".join(opts_list)
    #print(url)
    return url

def code_to_error(code):
    if code == 200:
        return None
    elif code == 401:
        return "Invalid api key"
    elif code == 404:
        return "Not found"
    elif code == 415:
        return "Bad request"
    elif code == 429:
        return "Too many requests"
    else:
        return ("Unknown status code: %s" % code)

def save_to_file(filename, text):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    with open(filename, "w+") as savefile:
        savefile.write(text)

def read_file(filename):
    with open(filename, "r") as file:
        return file.read()

def fullfile(path_list):
    return "/".join(path_list)

def json_parse(text):
    return json.loads(text)

def json_dump_to_file(json_object, filename):
    with open(filename, "w+") as f:
        json.dump(json_object, f, indent=4, separators=(',', ': '))

def get_telemetry_path(telemetry):
    # assume the path format doesnt change
    assert(len(telemetry) == 11)
    telemetry = telemetry[4:]
    path = ['telemetry', telemetry[0], telemetry[1] + '-' + telemetry[2] + '-' + telemetry[3],
            telemetry[4]+telemetry[5], telemetry[6]]
    return path

class PubgApi:
    def __init__(self):
        try:
            with open("apikey.env") as apikeyfile:
                self.key = apikeyfile.read()
        except:
            raise Exception("Api key must be placed in the apikey.env file.")
        self.stored_header = {"Authorization": self.key, "Accept": "application/vnd.api+json"}
        self.default_shard = "pc-eu"
        self.shards = ["xbox-as","xbox-eu","xbox-na","xbox-oc","pc-krjp","pc-na","pc-eu","pc-oc","pc-kakao","pc-sea","pc-as"]
        self.base_url = "https://api.playbattlegrounds.com/shards"
        self.data_store = "."
        self.player_data_store = fullfile([self.data_store, "players"])
        self.match_data_store = fullfile([self.data_store, "matches"])
        self.telemetry_data_store = fullfile([self.data_store, "telemetry"])

    def get_player(self, player, shard=None, search_ds=True):
        if shard is None:
            shard = self.default_shard
        json, error = self.get_player_json_checked(player, shard, search_ds)
        if not error:
            if len(json['data']) > 1:
                print('Warning: multiple players with name %(player)s found, returning first occurrence.')
            return Player(json['data'][0]), None
        else:
            return None, error

    def get_player_json_checked(self, player, shard, search_ds):
        result = None
        if search_ds:
            result = self.search_player_ds(player, shard)
        return (result, None) if result else (self.make_player_request(player, shard))

    def make_player_request(self, player, shard):
        url = make_url([self.base_url, shard, 'players'], ['filter[playerNames]=' + player])
        r = requests.get(url, headers=self.stored_header)
        if (r.status_code == 200):
            save_to_file(fullfile([self.player_data_store, shard, player + '.json']), r.text)
        response = r.text
        return json_parse(response), code_to_error(r.status_code)

    def search_player_ds(self, player, shard):
        expect = fullfile([self.player_data_store, shard, player + '.json'])
        return json_parse(read_file(expect)) if os.path.exists(expect) else None

    def get_match(self, matchid, shard=None, search_ds=True):
        if shard is None:
            shard = self.default_shard
        json, error = self.get_match_json_checked(matchid, shard, search_ds)
        if not error:
            return Match(json), None
        else:
            return None, error

    def get_match_json_checked(self, matchid, shard, search_ds):
        result = None
        if search_ds:
            result = self.search_match_ds(matchid, shard)
        return (result, None) if result else (self.make_match_request(matchid, shard))

    def search_match_ds(self, matchid, shard):
        expect = fullfile([self.match_data_store, shard, matchid + '.json'])
        return json_parse(read_file(expect)) if os.path.exists(expect) else None

    def make_match_request(self, matchid, shard):
        url = make_url([self.base_url, shard, 'matches', matchid])
        r = requests.get(url, headers=self.stored_header)
        if (r.status_code == 200):
            save_to_file(fullfile([self.match_data_store, shard, matchid + '.json']), r.text)
        response = r.text
        return json_parse(response), code_to_error(r.status_code)

    def get_match_telemetry(self, match, search_ds=True):
        json, error = self.get_match_telemetry_checked(match, search_ds)
        return (MatchTelemetry(json), None) if not error else (None, error)

    def get_match_telemetry_checked(self, match, search_ds):
        assert(type(match) == Match)
        result = None
        if search_ds:
            result = self.search_telemetry_ds(match.get_telemetry_link())
        return (result, None) if result else (self.make_telemetry_request(match.get_telemetry_link()))

    def search_telemetry_ds(self, telemetry):
        telemetry = telemetry.split("/")
        path = fullfile(get_telemetry_path(telemetry))
        return json_parse(read_file(path)) if os.path.exists(path) else None

    def make_telemetry_request(self, link):
        # we can save api requests :)
        r = requests.get(link, headers={})
        if r.status_code == 200:
            save_to_file(fullfile(get_telemetry_path(link.split('/'))), r.text)
        response = r.text
        return json_parse(response), code_to_error(r.status_code)
