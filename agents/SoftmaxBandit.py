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

import math
import random


def categorical_draws(probabilities):
    z = random.random()
    cum_prob = 0.0

    for i in xrange(len(probabilities)):
        prob = probabilities[i]
        cum_prob += prob
        if cum_prob > z:
            return i

    return len(probabilities) - 1


class Softmax:
    """
    Provides structured exploration. Tries to cope with the arms differing in estimated value by incorporating
    information about reward rates of the available arms while choosing the arms. This is done via exponential
    rescaling.
    """

    def __init__(self, temperature, counts, values):
        """
        When temperature is high, the randomness is high via: -exp(prob/temp)
        :param temperature: parameter that controls the randomness of the softmax function
        :param counts: vector of length N that tells how many times we played each of N arms
        :param values: vector of length N that tells the average amount of rewards obtained playing each of N arms
        """
        self.temperature = temperature
        self.counts = counts
        self.values = values

    def initialize(self, n_arms):
        """
        :param n_arms: tells the number of arms (or actions) in the problem 
        """
        self.counts = [0 for col in xrange(n_arms)]
        self.values = [0.0 for col in xrange(n_arms)]