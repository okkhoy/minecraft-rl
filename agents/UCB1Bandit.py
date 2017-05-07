"""
Created on May 8, 2017

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


class UCB1:
    def __init__(self, counts, values):
        self.counts = counts
        self.vaues = values

    def initialize(self, n_arms):
        self.counts = [0 for col in xrange(n_arms)]
        self.values = [0.0 for col in xrange(n_arms)]

    def select_arm(self):
        n_arms = len(self.counts)

        for arm in xrange(n_arms):
            if self.counts[arm] == 0:
                return arm

        ucb_values = [0.0 for arm in xrange(n_arms)]
        total_counts = sum(self.counts)

        for arm in xrange(n_arms):
            bonus = math.sqrt((2 * math.log(total_counts)) / float(self.counts[arm]))
            ucb_values[arm] = self.values[arm] + bonus

        return index_max(ucb_values)


def index_max(x):
    """
    :param x: vector whose max index has to be returned 
    :return: index of the max element in x
    """
    m = max(x)
    return x.index(m)

