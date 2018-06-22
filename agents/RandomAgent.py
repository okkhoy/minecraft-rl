"""
Random agent: No learning happens. A random action is returned each step.
"""

from __future__ import print_function

from rlglue.agent.Agent import Agent
from rlglue.types import Action
from rlglue.types import Observation
from rlglue.utils import TaskSpecVRLGLUE3

from mcrl.registry import register_agent

import logging
import random
import copy
import sys

@register_agent
class RandomAgent(Agent, object):
    name = "Random Agent"

    def __init__(self, **args):

        log = logging.getLogger('pyrl.agent.RandomAgent')
        self.lastAction = Action()
        self.lastObservation = Observation()
        self.params = args

        log.info("Agent __init__ completed")

    def agent_supported(self, parsedSpec):
        if parsedSpec.valid:
            assert len(parsedSpec.getDoubleObservations()) + len(parsedSpec.getIntObservations()) > 0, "No observations"
            assert len(parsedSpec.getIntActions()) == 1, "Specify 1-D Discrete actions"
            assert len(parsedSpec.getDoubleActions()) == 0, "Doesn't support continuous actions"
            assert not parsedSpec.isSpecial(parsedSpec.getIntActions()[0][0]), "Min action should be a number"
            assert not parsedSpec.isSpecial(parsedSpec.getIntActions()[0][1]), "Max action should be a number"

            return True
        else:
            return False

    def agent_init(self, taskSpecification):

        log = logging.getLogger('pyrl.agent.RandomAgent.agent_init')

        TaskSpec = TaskSpecVRLGLUE3.TaskSpecParser(taskSpecification)

        if not self.agent_supported(TaskSpec):
            print("Task could not be parsed", file=sys.stderr)
            sys.exit(1)

        self.lastAction = Action()
        self.lastObservation = Observation()
        self.thisAction = Action()

        log.info("Agent initialized")

    def agent_start(self, thisObservation):
        log = logging.getLogger('pyrl.agent.RandomAgent.agent_start')

        self.thisAction = Action()

        self.thisAction.intArray = [random.randint(0, 4)]

        self.lastAction = copy.deepcopy(self.thisAction)
        self.lastObservation = copy.deepcopy(thisObservation)

        log.info("Agent started")
        return self.thisAction

    def getNextAction(self):

        actionToReturn = [random.randint(0, 4)]

        return actionToReturn

    def agent_step(self, reward, thisObservation):

        log = logging.getLogger('pyrl.agent.RandomAgent.agent_step')

        # copy the state of the system first.
        currentState = thisObservation.intArray[:]  # use [:] to indicate all elements
        lastState = self.lastObservation.intArray[:]  # rather than using explicit indices. this is more generic
        wallDistance = thisObservation.doubleArray[0]

        log.debug("last state: %s \t last action: %d \t current state: %s \t distance: %f \t reward: %f",
                  lastState, self.lastAction.intArray[0], currentState, wallDistance, reward)

        action = self.getNextAction()

        log.debug("This action: %s", action)

        # copy the action and observation to the system state from local variables
        self.thisAction.intArray = action

        self.lastAction = copy.deepcopy(self.thisAction)
        self.lastObservation = copy.deepcopy(thisObservation)

        return self.thisAction

    def agent_end(self, reward):
        pass

    def agent_cleanup(self):
        pass

    def agent_message(self, message):
        return "false"
