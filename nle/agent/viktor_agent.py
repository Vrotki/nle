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
from nle.env import NLE

# yapf: disable
parser = argparse.ArgumentParser(description="PyTorch Scalable Agent")

parser.add_argument("--mode", default="train",
                    choices=["train", "test", "help"],
                    help="Training or test mode.")

def train(flags):
    return

def print_help(flags):
    env: NLE = gym.make("NetHackScore-v0")
    env.print_action_meanings()

def test(flags):
    env: NLE = gym.make("NetHackScore-v0")
    
    env.reset()  # each reset generates a new dungeon
    continue_run = True
    while(continue_run):
        for i in range(100):
            #env.step(1)  # move agent '@' north
            env.step(random.choice([1, 2, 3, 4])) # step(1) moves agent '@' north
            env.render()
            time.sleep(0.05)
        continue_run = input('Enter "quit" to continue run: ') != 'quit'
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

# Run with python -m nle.agent.viktor_agent --mode=test
