import argparse
import logging
import os
import pprint
import threading
import time
import timeit
import traceback
import gym
import random
import nle  # noqa: F401, E402
from nle import nethack  # noqa: E402
from nle.agent import vtrace  # noqa: E402
from nle.agent import viktor_agent
from nle.env import NLE
from nle_language_wrapper import NLELanguageWrapper

# yapf: disable
parser = argparse.ArgumentParser(description="Viktor Agent")

parser.add_argument("--mode", default="train",
                    choices=["train", "test", "fast_test", "help", "step_test"],
                    help="Training or test mode.")

def train(flags):
    return

def print_help(flags):
    env: NLE = gym.make("NetHackScore-v0")
    env.print_action_meanings()

def test(flags):
    env: NLE = NLELanguageWrapper(gym.make("NetHackScore-v0"))
    
    env.reset()  # each reset generates a new dungeon
    current_agent = viktor_agent.viktor_agent(env)
    continue_run = True

    if flags.mode == "step_test":
        repeats = 1
        delay = 0
    elif flags.mode == "fast_test":
        repeats = 10
        delay = 0
    else:
        repeats = 100
        delay = 0.05

    new_command = ''
    current_agent.act('wait')
    while(continue_run):
        #env.render()
        #print(current_agent.last_text_message)
        #print(current_agent.nle_map)
        new_command = input('Enter "quit" to terminate run: ')
        continue_run = new_command != 'quit'
        if continue_run:
            for i in range(repeats):
                if new_command not in ['', 'quit']:
                    current_agent.act(specified_command=new_command, display=(i == repeats - 1))
                else:
                    current_agent.act(display=(i == repeats - 1))
                if delay:
                    time.sleep(delay)
                    env.render()
    return

def main(flags):
    if flags.mode == "train":
        train(flags)
    elif flags.mode == "help":
        print_help(flags)
    else:
        test(flags)


if __name__ == "__main__":
    flags = parser.parse_args()
    main(flags)

# Run with python -m nle.agent.viktor_main --mode=test
# Run step by step: python -m nle.agent.viktor_main --mode=step_test

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
