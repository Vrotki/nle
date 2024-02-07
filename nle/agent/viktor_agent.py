import random
from nle.env import NLE

class viktor_agent:
    def __init__(self, env: NLE):
        self.env: NLE = env

    def act(self):
        self.env.step(random.choice([1, 2, 3, 4])) # step(1) moves agent '@' north