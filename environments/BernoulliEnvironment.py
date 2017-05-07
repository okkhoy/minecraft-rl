"""
Created on May 7, 2017

@author: Akshay Narayan

This code is shared under The MIT License
-----------------------------------------

The MIT License (MIT)

Copyright (c) <year> <copyright holders>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import random

from rlglue.environment.Environment import Environment
from rlglue.environment import EnvironmentLoader as EnvironmentLoader
from rlglue.types import Observation
from rlglue.types import Action
from rlglue.types import Reward_observation_terminal
from rlglue import TaskSpecRLGlue
from rlglue.registry import register_environment


class BernoulliArm:

    def __init__(self, p):
        """
        Implements a simple random reward generator
        :param p: the probability with which the arm associated returns 1 as reward
        """
        self.p = p

    def draw(self):
        """
        Returns reward 1 with probability p
        """
        if random.random() > self.p:
            return 0.0
        else:
            return 1.0


def test():
    means = [0.1, 0.2, 0.6, 0.1]  # probabilities with which each arm emits a reward 1
    n_arms = len(means)
    random.shuffle(means)
    arms = map(lambda mu: BernoulliArm(mu), means)
    print "Arms: ", arms
    for a in arms:
        a.draw()