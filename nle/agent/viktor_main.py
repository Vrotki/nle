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
        repeats = 100
        delay = 0
    else:
        repeats = 100
        delay = 0.05

    new_command = ''
    current_agent.act('wait')
    while(continue_run):
        env.render()
        print(current_agent.nle_map)
        new_command = input('Enter "quit" to terminate run: ')
        continue_run = new_command != 'quit'
        if continue_run:
            for i in range(repeats):
                if new_command not in ['', 'quit']:
                    current_agent.act(specified_command=new_command)
                else:
                    current_agent.act()
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
