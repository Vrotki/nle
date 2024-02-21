import random
import math
from typing import Dict, List
from nle.env import NLE
from nle.agent.agent_util.nle_map import nle_map
import nle.agent.agent_util.misc_util as misc_util

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

    def think(self):
        return('wait')

    def act(self, specified_command = None):
        if specified_command:
            command = specified_command
        else:
            command = self.think() #"wait"
        try:
            obsv, reward, done, info = self.env.step(command)
        except:
            print(specified_command + ' is not a valid command.\n')
            return
        self.surroundings = obsv['text_glyphs'].split("\n") # Description of surroundings
        text_message: str = obsv['text_message'] # Immediate feedback, like "It's solid stone."
        self.nle_map.update_position(command, text_message)
        self.nle_map.update_surroundings(self.surroundings)
        self.update_stats(obsv['text_blstats'].split('\n')) # Description of stats, statuses, and progress
        self.inventory = obsv['text_inventory'].split('\n') # Description of each inventory item
        self.character_class = obsv['text_cursor'].split(' ')[-1] # Description of character class
        print(self.nle_map)

    def interpret(self, text_glyph: str, verbose: bool = False) -> Dict:
        original_glyph = text_glyph
        print('Interpreting observation: ' + text_glyph)
        superfluous_words = [',', '.']
        location_distances = {'adjacent': 1, 'verynear': 2, 'near': 3, 'far': 6, 'veryfar': 12}
        location_max_distances = {'adjacent': 1, 'verynear': 2, 'near': 5, 'far': 11, 'veryfar': 30}
        '''
        Observed boundaries:
            Adjacent: 1-1
            Very near: 2-2
            Near: 3-5
            Far: 6-?
            Very far: ?
        '''
        cardinal_directions = ['north', 'west', 'south', 'east']
        text_glyph = text_glyph.replace(' and ', ' ')
        text_glyph = misc_util.remove_multiple_substrings(text_glyph, superfluous_words).replace('very near', 'verynear').replace('very far', 'veryfar').split(' ')
        if verbose:
            print(text_glyph)
        location_separated = False
        num_words = len(text_glyph)
        index = 0
        while index < num_words and not location_separated:
            current_word = text_glyph[index]
            if current_word in location_distances:
                glyph_subject = text_glyph[:index]
                glyph_location = text_glyph[index:]
                location_word = glyph_location.pop(0)
                min_glyph_distance = location_distances[location_word]
                # Should have a way to detect a previously found glyph of the same subject in the approximate location
                for location_index, current_copy in enumerate(glyph_location):
                    for cardinal_direction in cardinal_directions:
                        glyph_location[location_index] = glyph_location[location_index].replace(cardinal_direction, cardinal_direction + ' ')
                    glyph_location[location_index] = glyph_location[location_index].split(' ')
                    glyph_location[location_index].pop(-1)
                    angle = misc_util.cardinal_directions_to_angle(glyph_location[location_index])
                    if verbose:
                        print(angle)
                    if len(glyph_location[location_index]) <= 2: # Angles like north northeast are too imprecise to incorporate accurately
                        glyph_location[location_index] = set([])

                        for estimated_glyph_distance in range(min_glyph_distance, location_max_distances[location_word] + 1):
                            x_change = estimated_glyph_distance * math.cos(math.radians(angle))
                            if round(x_change, 2) < 0:
                                x_change = -1 * int(math.ceil(-1 * x_change))
                            elif round(x_change, 2) > 0:
                                x_change = int(math.ceil(x_change))
                            else:
                                x_change = int(round(x_change))

                            y_change = estimated_glyph_distance * math.sin(math.radians(angle))
                            if round(y_change, 2) < 0:
                                y_change = -1 * int(math.ceil(-1 * y_change))
                            elif round(y_change, 2) > 0:
                                y_change = int(math.ceil(y_change))
                            else:
                                y_change = int(round(y_change))
                            glyph_location[location_index].add((self.x + x_change, self.y + y_change))

                location_separated = True
            index += 1
        print('Encoding ' + str(glyph_subject) + ' about ' + str(min_glyph_distance) + ' away at the coordinates ' + str(glyph_location) +'\n')
        return({
            'subject': glyph_subject,
            'locations': glyph_location,
            'glyph': original_glyph
        })

    def allows_move(self, text_message: str) -> bool:
        if text_message.startswith('You kill '):
            return(False)
        elif text_message == "It's solid stone.":
            return(False)
        elif text_message == "It's a wall.":
            return(False)
        elif text_message.startswith('You stop. '):
            return(False)
        elif text_message.startswith('The door resists'):
            return(False)
        elif text_message.startswith('The door opens'):
            return(False)
        elif text_message.startswith('Wait! '):
            return(False)
        elif text_message.startswith('It recoils! '):
            return(False)
        elif text_message.startswith('You miss '):
            return(False)
        elif text_message.startswith('You hit '):
            return(False)
        elif text_message.startswith("You can't move"):
            return(False)
        return(True)

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