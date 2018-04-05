
class Player:
    def __init__(self):
        self.id = None
        self.created_at = None
        self.name = None
        self.shard = None
        self.patch_version = None
        self.updated_at = None
        self.title_id = None

        self.matches = None
        self.link = None

    def __init__(self, json_object):
        assert(json_object['type'] == "player")
        self.id = json_object['id']

        attrs = json_object['attributes']
        self.created_at = attrs['createdAt']
        self.name = attrs['name']
        self.shard = attrs['shardId']
        self.patch_version = attrs['patchVersion']
        self.updated_at = attrs['updatedAt']
        self.title_id = attrs['titleId']

        self.matches = []
        relationships = json_object['relationships']
        if 'matches' in relationships:
            matchlist = relationships['matches']['data']
            for match in matchlist:
                assert(match['type']=="match")
                self.matches.append(match['id'])
        self.link = json_object['links']['self']


class Match:
    def __init__(self):
        self.id = None
        # completion time
        self.created_at = None
        self.duration = None
        # [ duo, duo-fpp, solo, solo-fpp, squad, squad-fpp ]
        self.game_mode = None
        self.patch_version = None
        self.shard = None
        self.tags = None
        self.title_id = None

        self.assets = None
        self.rosters = None
        self.rounds = None
        self.spectators = None

        self.link = None
    
    def __init__(self, json_object):

        data = json_object['data']
        assert(data['type'] == "match")
        self.id = data['id']

        attrs = data['attributes']
        self.created_at = attrs['createdAt']
        self.duration = attrs['duration'] # in seconds
        self.game_mode = attrs['gameMode']
        self.patch_version = attrs['patchVersion']
        self.shard = attrs['shardId']
        self.tags = attrs['tags']
        self.title_id = attrs['titleId']

        rs = data['relationships']

        self.assets = []
        self.participants = []
        self.rosters = []
        # untested, will come with custom game support
        self.spectators = []

        self.read_included(json_object['included'])

        # currently unused?
        self.rounds = rs['rounds']

        self.link = json_object['links']['self']
    
    def read_included(self, json_object):

        for include in json_object:
            typ = include['type']
            if typ == "participant":
                self.participants.append(MatchParticipant(include))
            elif typ == "roster":
                self.rosters.append(MatchRoster(include))
            elif typ == "asset":
                self.assets.append(MatchAsset(include))
            else:
                print("Unknown included type: %(typ)s")    

    def get_roster_participants(self, roster):
        # allow id later
        assert(type(roster) == MatchRoster)
        return list(filter(lambda x: x.participant_id in roster.participants, self.participants))

    def get_telemetry_link(self):
        return self.assets[0].link


class MatchRoster:
    def __init__(self):
        self.roster_id = None
        self.shard = None
        self.rank = None
        self.team_id = None
        self.won = None
        self.team = None

        self.participants = None
    
    def __init__(self, json_object):
        self.roster_id = json_object['id']
        attrs = json_object['attributes']
        self.shard = attrs['shardId']
        stats = attrs['stats']
        self.rank = stats['rank']
        self.team_id = stats['teamId']
        self.won = attrs['won']
        
        rs = json_object['relationships']
        self.team = rs['team']
        self.participants = []
        for participant in rs['participants']['data']:
            self.participants.append(participant['id'])


class MatchAsset:
    def __init__(self):
        self.id = None
        self.link = None
        self.created_at
        self.description = None
        self.name = None

    def __init__(self, json_object):
        assert(json_object['type'] == "asset")
        self.id = json_object['id']
        attrs = json_object['attributes']
        self.link = attrs['URL']
        self.created_at = attrs['createdAt']
        self.description = attrs['description']
        self.name = attrs['name']


class MatchParticipant:
    def __init__(self):
        self.participant_id = None
        
        self.player_id = None
        self.shard = None
        self.name = None

        self.dbnos = None
        self.assists = None
        self.boosts = None
        self.damage_dealt = None
        #[ alive, byplayer, suicide ]
        self.death_type = None
        self.headshot_kills = None
        self.heals = None
        self.kill_place = None
        self.kill_points_delta = None
        self.kill_streaks = None
        self.kills = None
        self.last_kill_points = None
        self.last_win_points = None
        self.longest_kill = None
        self.most_damage = None
        self.revives = None
        self.ride_distance = None
        self.road_kills = None
        self.team_kills = None
        self.time_survived = None
        self.vehicles_destroyed = None
        self.walk_distance = None
        self.weapons_acquired = None
        self.win_place = None
        self.win_points = None

    def __init__(self, json_object):
        assert(json_object['type'] == "participant")
        self.participant_id = json_object['id']
        
        stats = json_object['attributes']['stats']

        self.player_id = stats['playerId']
        self.shard = json_object['attributes']['shardId']
        self.name = stats['name']

        self.dbnos = stats['DBNOs']
        self.assists = stats['assists']
        self.boosts = stats['boosts']
        self.damage_dealt = stats['damageDealt']
        #[ alive, byplayer, suicide ]
        self.death_type = stats['deathType']
        self.headshot_kills = stats['headshotKills']
        self.heals = stats['heals']
        self.kill_place = stats['killPlace']
        self.kill_points_delta = stats['killPointsDelta']
        self.kill_streaks = stats['killStreaks']
        self.kills = stats['kills']
        self.last_kill_points = stats['lastKillPoints']
        self.last_win_points = stats['lastWinPoints']
        self.longest_kill = stats['longestKill']
        self.most_damage = stats['mostDamage']
        self.revives = stats['revives']
        self.ride_distance = stats['rideDistance']
        self.road_kills = stats['roadKills']
        self.team_kills = stats['teamKills']
        self.time_survived = stats['timeSurvived']
        self.vehicles_destroyed = stats['vehicleDestroys']
        self.walk_distance = stats['walkDistance']
        self.weapons_acquired = stats['weaponsAcquired']
        self.win_place = stats['winPlace']
        self.win_points = stats['winPointsDelta']


class MatchTelemetry:
    def __init__(self):
        self.events = None

    def __init__(self, json_object):
        self.events = []
        self.process_events(json_object)

    def process_events(self, json):
        for event in json:
            typ = event["_T"]
            if typ == "LogItemPickup":
                self.events.append(EventItemPickup(event))
            elif typ == "LogPlayerLogin":
                self.events.append(EventPlayerLogin(event))
            elif typ == "LogPlayerCreate":
                self.events.append(EventPlayerCreate(event))
            elif typ == "LogPlayerPosition":
                self.events.append(EventPlayerPosition(event))
            elif typ == "LogPlayerAttack":
                self.events.append(EventPlayerAttack(event))
            elif typ == "LogItemEquip":
                self.events.append(EventItemEquip(event))
            elif typ == "LogItemUnequip":
                self.events.append(EventItemUnequip(event))
            elif typ == "LogVehicleRide":
                self.events.append(EventVehicleRide(event))
            elif typ == "LogMatchDefinition":
                self.events.append(EventMatchDefinition(event))
            elif typ == "LogMatchStart":
                self.events.append(EventMatchStart(event))
            elif typ == "LogGameStatePeriodic":
                self.events.append(EventGamestatePeriodic(event))
            elif typ == "LogVehicleLeave":
                self.events.append(EventVehicleLeave(event))
            elif typ == "LogPlayerTakeDamage":
                self.events.append(EventPlayerTakeDamage(event))
            elif typ == "LogPlayerLogout":
                self.events.append(EventPlayerLogout(event))
            elif typ == "LogItemAttach":
                self.events.append(EventItemAttach(event))
            elif typ == "LogItemDrop":
                self.events.append(EventItemDrop(event))
            elif typ == "LogPlayerKill":
                self.events.append(EventPlayerKill(event))
            elif typ == "LogItemDetach":
                self.events.append(EventItemDetach(event))
            elif typ == "LogItemUse":
                self.events.append(EventItemUse(event))
            elif typ == "LogCarePackageSpawn":
                self.events.append(EventCarePackageSpawn(event))
            elif typ == "LogVehicleDestroy":
                self.events.append(EventVehicleDestroy(event))
            elif typ == "LogCarePackageLand":
                self.events.append(EventCarePackageLand(event))
            elif typ == "LogMatchEnd":
                self.events.append(EventMatchEnd(event))
            else:
                self.events.append(TelemetryEvent(event))
                raise Exception(event["_T"] + " not implemented!")


class TelemetryEvent:
    def __init__(self):
        self.version = None
        self.event_timestamp = None
        self.event_type = None

    def __init__(self, json_object):
        self.version = json_object["_V"]
        self.event_timestamp = json_object["_D"]
        self.event_type = json_object["_T"]
        #print(self.event_type)


class Location:
    #max = 0
    def __init__(self):
        self.x = None
        self.y = None
        self.z = None
    def __init__(self, json_object):
        self.x = json_object['x']
        self.y = json_object['y']
        self.z = json_object['z']
        #print(" %.2f %.2f %.2f" % (self.x, self.y, self.z))
        #if(self.x < Location.max):
        #    Location.max = self.x
        #if(self.y < Location.max):
        #    Location.max = self.y
        #if(self.z < Location.max):
        #    Location.max = self.z
        #print(Location.max)


class Character(Location):
    def __init__(self):
        self.name = None
        self.team_id = None
        self.health = None
        self.ranking = None
        self.account_id = None

    def __init__(self, json_object):
        super().__init__(json_object['location'])
        self.name = json_object['name']
        self.team_id = json_object['teamId']
        self.health = json_object['health']
        self.ranking = json_object['ranking']
        self.account_id = json_object['accountId']

class Item:
    def __init__(self):
        self.item_id = None
        self.stack_count = None
        self.category = None
        self.subcategory = None
        self.attached_items = None

    def __init__(self, json_object):
        self.item_id = json_object['itemId']
        self.stack_count = json_object['stackCount']
        self.category = json_object['category']
        self.subcategory = json_object['subCategory']
        self.attached_items = []
        self.read_attached_items(json_object['attachedItems'])

    def read_attached_items(self, json_object):
        for item in json_object:
            self.attached_items.append(item)


class ItemPackage(Location):
    def __init__(self):
        self.item_package_id = None
        self.items = None

    def __init__(self, json_object):
        super().__init__(json_object['location'])
        self.item_package_id = json_object['itemPackageId']
        self.items = []
        self.read_items(json_object['items'])

    def read_items(self, json_object):
        for item in json_object:
            self.items.append(Item(item))


class Vehicle:
    def __init__(self):
        self.vehicle_type = None
        self.vehicle_id = None
        self.health_percent = None
        self.fuel_percent = None

    def __init__(self, json_object):
        self.vehicle_type = json_object['vehicleType']
        self.vehicle_id = json_object['vehicleId']
        self.health_percent = json_object['healthPercent']
        # FIXME INTENTIONAL TYPO INCLUDED IN API
        self.fuel_percent = json_object['feulPercent']


class Gamestate:
    def __init__(self):
        self.elapsed_time = None
        self.num_alive_teams = None
        self.num_join_players = None
        self.num_start_players = None
        self.num_alive_players = None
        self.safety_zone_position = None
        self.safety_zone_radius = None
        self.poison_gas_warning_position = None
        self.poison_gas_warning_radius = None
        self.redzone_position = None
        self.redzone_radius = None

    def __init__(self, json_object):
        self.elapsed_time = json_object['elapsedTime']
        self.num_alive_teams = json_object['numAliveTeams']
        self.num_join_players = json_object['numJoinPlayers']
        self.num_start_players = json_object['numStartPlayers']
        self.num_alive_players = json_object['numAlivePlayers']
        self.safety_zone_position = self.read_location(json_object['safetyZonePosition'])
        self.safety_zone_radius = json_object['safetyZoneRadius']
        self.poison_gas_warning_position = self.read_location(json_object['poisonGasWarningPosition'])
        self.poison_gas_warning_radius = json_object['poisonGasWarningRadius']
        self.redzone_position = self.read_location(json_object['redZonePosition'])
        self.redzone_radius = json_object['redZoneRadius']

    def read_location(self, json_object):
        return Location(json_object)


class EventItemPickup(TelemetryEvent):
    def __init__(self):
        self.character = None
        self.item = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.character = Character(json_object['character'])
        self.item = Item(json_object['item'])


class EventPlayerLogin(TelemetryEvent):
    def __init__(self):
        self.result = None
        self.error_message = None
        self.account_id = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.result = json_object['result']
        self.error_message = json_object['errorMessage']
        self.account_id = json_object['accountId']

    
class EventPlayerCreate(TelemetryEvent):
    def __init__(self):
        self.character = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.character = Character(json_object['character'])


class EventPlayerPosition(TelemetryEvent):
    def __init__(self):
        self.character = None
        self.elapsed_time = None
        self.num_alive_players = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.character = Character(json_object['character'])
        self.elapsed_time = json_object['elapsedTime']
        self.num_alive_players = json_object['numAlivePlayers']


class EventPlayerAttack(TelemetryEvent):
    def __init__(self):
        self.attack_id = None
        self.attacker = None
        self.attack_type = None
        self.weapon = None
        self.vehicle = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.attack_id = json_object['attackId']
        self.attacker = Character(json_object['attacker'])
        self.attack_type = json_object['attackType']
        self.weapon = Item(json_object['weapon'])
        self.vehicle = Vehicle(json_object['vehicle'])


class EventItemEquip(TelemetryEvent):
    def __init__(self):
        self.character = None
        self.item = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.character = Character(json_object['character'])
        self.item = Item(json_object['item'])


class EventItemUnequip(TelemetryEvent):
    def __init__(self):
        self.character = None
        self.item = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.character = Character(json_object['character'])
        self.item = Item(json_object['item'])


class EventVehicleRide(TelemetryEvent):
    def __init__(self):
        self.character = None
        self.vehicle = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.character = Character(json_object['character'])
        self.vehicle = Vehicle(json_object['vehicle'])


class EventMatchDefinition(TelemetryEvent):
    def __init__(self):
        self.match_id = None
        self.ping_quality = None

    def __init__(self, json_object):
        super().__init__(json_object)
        # FIXME RANDOMLY FIRST WORD CAPITALIZED??
        self.match_id = json_object['MatchId']
        self.ping_quality = json_object['PingQuality']


class EventMatchStart(TelemetryEvent):
    def __init__(self):
        self.characters = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.characters = []
        for character in json_object['characters']:
            self.characters.append(Character(character))


class EventGamestatePeriodic(TelemetryEvent):
    def __init__(self):
        self.gamestate = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.gamestate = Gamestate(json_object['gameState'])

    
class EventVehicleLeave(TelemetryEvent):
    def __init__(self):
        self.character = None
        self.vehicle = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.character = Character(json_object['character'])
        self.vehicle = Vehicle(json_object['vehicle'])


class EventPlayerTakeDamage(TelemetryEvent):
    def __init__(self):
        self.attack_id = None
        self.attacker = None
        self.victim = None
        self.damage_type_category = None
        self.damage_reason = None
        self.damage = None
        self.damage_causer_name = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.attack_id = json_object['attackId']
        self.attacker = Character(json_object['attacker'])
        self.victim = Character(json_object['victim'])
        self.damage_type_category = json_object['damageTypeCategory']
        self.damage_reason = json_object['damageReason']
        self.damage = json_object['damage']
        self.damage_causer_name = json_object['damageCauserName']


class EventPlayerLogout(TelemetryEvent):
    def __init__(self):
        self.account_id = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.account_id = json_object['accountId']


class EventItemAttach(TelemetryEvent):
    def __init__(self):
        self.character = None
        self.parent_item = None
        self.child_item = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.character = Character(json_object['character'])
        self.parent_item = Item(json_object['parentItem'])
        self.child_item = Item(json_object['childItem'])


class EventItemDrop(TelemetryEvent):
    def __init__(self):
        self.character = None
        self.item = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.character = Character(json_object['character'])
        self.item = Item(json_object['item'])


class EventPlayerKill(TelemetryEvent):
    def __init__(self):
        self.attack_id = None
        self.killer = None
        self.victim = None
        self.damage_type_category = None
        self.damage_causer_name = None
        self.distance = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.attack_id = json_object['attackId']
        self.killer = Character(json_object['killer'])
        self.victim = Character(json_object['victim'])
        self.damage_type_category = json_object['damageTypeCategory']
        self.damage_causer_name = json_object['damageCauserName']
        self.distance = json_object['distance']


class EventItemDetach(TelemetryEvent):
    def __init__(self):
        self.character = None
        self.parent_item = None
        self.child_item = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.character = Character(json_object['character'])
        self.parent_item = Item(json_object['parentItem'])
        self.child_item = Item(json_object['childItem'])


class EventItemUse(TelemetryEvent):
    def __init__(self):
        self.character = None
        self.item = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.character = Character(json_object['character'])
        self.item = Item(json_object['item'])

    
class EventCarePackageSpawn(TelemetryEvent):
    def __init__(self):
        self.item_package

    def __init__(self, json_object):
        super().__init__(json_object)
        self.item_package = ItemPackage(json_object['itemPackage'])


class EventVehicleDestroy(TelemetryEvent):
    def __init__(self):
        self.attack_id = None
        self.attacker = None
        self.vehicle = None
        self.damage_type_category = None
        self.damage_causer_name = None
        self.distance = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.attack_id = json_object['attackId']
        self.attacker = Character(json_object['attacker'])
        self.vehicle = Vehicle(json_object['vehicle'])
        self.damage_type_category = json_object['damageTypeCategory']
        self.damage_causer_name = json_object['damageCauserName']
        self.distance = json_object['distance']


class EventCarePackageLand(TelemetryEvent):
    def __init__(self):
        self.item_package

    def __init__(self, json_object):
        super().__init__(json_object)
        self.item_package = ItemPackage(json_object['itemPackage'])


class EventMatchEnd(TelemetryEvent):
    def __init__(self):
        self.characters = None

    def __init__(self, json_object):
        super().__init__(json_object)
        self.characters = []
        for character in json_object['characters']:
            self.characters.append(Character(character))
