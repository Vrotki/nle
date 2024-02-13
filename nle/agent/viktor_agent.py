import random
from typing import Dict, List
from nle.env import NLE
from nle.agent.agent_util.nle_map import nle_map

int_stats: List[str] = [
    'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma', 'depth', 'gold', 'ac', 'time', 'monster_level', 'dungeon_number','level_number', 'score'
]
scale_stats: List[str] = ['strength', 'hp', 'energy', 'xp']
str_stats = ['position', 'hunger', 'encumbrance', 'alignment', 'condition']

class viktor_agent:
    def __init__(self, env: NLE):
        self.x: int = 0
        self.y: int = 0
        self.env: NLE = env
        self.last_observation: Dict = {}
        self.surroundings: List[str] = []
        self.nle_map: nle_map = nle_map(self)
        self.stats: Dict = {}
        self.inventory: List[str] = []
        self.character_class: str = None
        
    def update_stats(self, blstats: List[str]):
        for current_value in blstats:
            split_stat = current_value.split(": ")
            current_stat_name = split_stat[0].lower().replace(" ", "_")
            if current_stat_name in int_stats:
                self.stats[current_stat_name] = int(split_stat[-1])
            elif current_stat_name in scale_stats:
                self.stats[current_stat_name], self.stats["max_" + current_stat_name] = [int(x) for x in split_stat[-1].split('/')]
            elif current_stat_name in str_stats:
                self.stats[current_stat_name] = split_stat[-1]

    def act(self):
        obsv, reward, done, info = self.env.step("wait")
        self.surroundings = obsv["text_glyphs"].split("\n") # Description of surroundings
        self.nle_map.update_surroundings(self.surroundings)
        text_message: str = obsv["text_message"] # Seems to be empty
        self.update_stats(obsv["text_blstats"].split("\n")) # Description of stats, statuses, and progress
        self.inventory = obsv["text_inventory"].split("\n") # Description of each inventory item
        self.character_class = obsv["text_cursor"].split(" ")[-1] # Description of character class
        print(self.nle_map)

'''
observation_keys=(
    "glyphs",
    "chars",
    "colors",
    "specials",
    "blstats",
    "message",
    "inv_glyphs",
    "inv_strs",
    "inv_letters",
    "inv_oclasses",
    "screen_descriptions",
    "tty_chars",
    "tty_colors",
    "tty_cursor",
)

Commands:
    0 MiscAction.MORE
    1 CompassDirection.N
    2 CompassDirection.E
    3 CompassDirection.S
    4 CompassDirection.W
    5 CompassDirection.NE
    6 CompassDirection.SE
    7 CompassDirection.SW
    8 CompassDirection.NW
    9 CompassDirectionLonger.N
    10 CompassDirectionLonger.E
    11 CompassDirectionLonger.S
    12 CompassDirectionLonger.W
    13 CompassDirectionLonger.NE
    14 CompassDirectionLonger.SE
    15 CompassDirectionLonger.SW
    16 CompassDirectionLonger.NW
    17 MiscDirection.UP
    18 MiscDirection.DOWN
    19 MiscDirection.WAIT
    20 Command.KICK
    21 Command.EAT
    22 Command.SEARCH
'''