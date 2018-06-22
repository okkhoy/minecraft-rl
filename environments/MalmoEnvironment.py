"""
Simple environment specified in ../configurations/RandomAgentExperiment.json
A room with some obstacles; and items. Mimics MaxQ Taxi.
"""

import copy
import json
import logging
import random
import time
from pprint import pformat

import MalmoPython
import numpy
from rlglue.environment.Environment import Environment
from rlglue.types import Observation
from rlglue.types import Reward_observation_terminal

from mcrl import TaskSpecRLGlue
from mcrl.registry import register_environment

malmo_env = MalmoPython.AgentHost()

@register_environment
class MalmoEnvironment(Environment):
    name = 'Malmo Basic'

    def __init__(self, **kwargs):
        log = logging.getLogger('pyrl.environment.malmoenvironment')

        self.size = numpy.array([kwargs['size_x'], kwargs['size_y']])
        self.walls = kwargs['walls']
        self.landmarks = kwargs['landMarks']

        self.mission_xml = self.generateMalmoEnvironmentXML()

        self.mission = None
        self.mission_record = MalmoPython.MissionRecordSpec()
        if self.mission_xml:
            self.mission = MalmoPython.MissionSpec(self.mission_xml, True)
            log.info("Loaded mission XML")
        else:
            log.debug("No mission XML file specified, creating default mission")
            self.mission = MalmoPython.MissionSpec()

        self.position = numpy.zeros((2,))
        self.direction = 0
        self.passenger_location = 0
        self.destination = 0
        self.domainName = "Malmo Basic Environment"

        self.actions = ["move 1", "turn 1", "turn -1", "attack 1", "discardCurrentItem"]

        self.landmark_types = ["redstone_block", "emerald_block", "lapis_block", "cobblestone", "gold_block",
                               "quartz_block"]

        # we need to keep track of what we saw the last; This is necessary 'cos malmo doesn't return all that we need
        # always, we need to save previous observation until the next valid one comes in. i don't see another way to
        # do this right now.
        self.lastObservation = None

        # to record if get is done and put is active:
        self.getCompleted = False

        log.debug("Verify configuration with input: %s", self.__dict__)

    def generateMalmoEnvironmentXML(self):
        log = logging.getLogger('pyrl.environment.malmoenvironment.generateXMLEnv')

        xml_string = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
        <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

        <About>
          <Summary>Taxi kind of experiment modeled in Malmo</Summary>
        </About>

        <ServerSection>
          <ServerInitialConditions>
              <Time><StartTime>1</StartTime></Time>
              <Weather>clear</Weather>
          </ServerInitialConditions>
          <ServerHandlers>
            <FlatWorldGenerator generatorString="3;7,220*1,5*3,2;3;,biome_1" forceReset="false" />
            <DrawingDecorator>
              <!-- coordinates for cuboid are inclusive -->
              <DrawCuboid x1="0" y1="46" z1="0" x2="''' + str(self.size[0]) + '''" y2="50" z2="''' + str(self.size[1]) + '''" type="air" />
              <DrawCuboid x1="0" y1="45" z1="0" x2="''' + str(self.size[1]) + '''" y2="45" z2="''' + str(self.size[1]) + '''" type="sandstone" />
              ''' + self.drawLandmarks() + self.drawObstacles() + '''
            </DrawingDecorator>
            <ServerQuitFromTimeUp timeLimitMs="720000"/>
            <ServerQuitWhenAnyAgentFinishes/>
          </ServerHandlers>
        </ServerSection>
        <AgentSection mode="Survival">
          <Name>ButterFingers</Name>
          <AgentStart>
            <Placement x="4" y="46.0" z="2" pitch="15" yaw="0"/>
            <Inventory>
            </Inventory>
          </AgentStart>
          <AgentHandlers>
            <DiscreteMovementCommands/>
            <MissionQuitCommands/>
            <InventoryCommands/>
            <ObservationFromFullStats/>
            <ObservationFromFullInventory/>
            <ObservationFromHotBar/>
            <ObservationFromRay/>   
            <ObservationFromDiscreteCell/>         
            <VideoProducer want_depth="false" viewpoint="1">
                <Width>320</Width>
                <Height>240</Height>
            </VideoProducer>
            <RewardForSendingCommand reward="-1" />
          </AgentHandlers>
        </AgentSection>
      </Mission>'''

        log.debug("Final mission XML String: %s", xml_string)

        return xml_string

    def drawLandmarks(self):
        log = logging.getLogger('pyrl.environment.malmoenvironment.drawlandmarks')

        landmarks = self.landmarks

        log.debug("Input landmarks: %s", landmarks)

        landmarkXML = '''<!-- draw landmarks -->'''

        landmarkTypes = ["redstone_block", "emerald_block", "lapis_block", "cobblestone", "gold_block", "quartz_block"]

        for i, l in enumerate(landmarks):
            x, z = l
            landmarkXML += '''<DrawBlock x="''' + str(x) + '''" y="45" z="''' + str(z) + '''" type="''' + \
                           landmarkTypes[i % len(landmarkTypes)] + '''"/>
                           '''

        return landmarkXML

    def drawObstacles(self):
        log = logging.getLogger('pyrl.environment.malmoenvironment.drawobstacles')

        walls = self.walls

        log.debug("Input walls: %s", walls)

        obstacleXML = '''<!-- draw the obstacles -->'''
        for w in walls:
            log.debug("Adding obstacle: %s", w)
            x, y, direction = list(w)
            obstacleString = self.drawObstacle(x, y, direction)
            log.debug("Obstacle string received: %s", obstacleString)
            obstacleXML = obstacleXML + obstacleString

        log.debug("Obstacle string obtained: %s", obstacleXML)

        return obstacleXML

    def drawObstacle(self, x, y, direction):
        """
        This method is used to add obstacles to the environment.
        For simple environment these are just walls.
        It takes the x,y coordinates of the cell and the position of the wall
        north, south, east, west
        x, denotes the x coordinate of the cell
        y, denotes the y coordinate of the cell
        direction, corresponds to the direction in the cell. 0 - north, 1 - south, 2 - east, 3 - west
        """
        _x, _y = x, y

        log = logging.getLogger('pyrl.environment.malmoenvironment.addobstacle')

        log.debug("Input x, y, d: %d, %d, %d", x, y, direction)

        cellIndex = y * self.size[0] + x

        log.info("Adding walls [x, y, direction] = [%d, %d, %d]; index: %d", x, y, direction, cellIndex)

        log.debug("Cell index: [%d, %d] = %d", x, y, cellIndex)

        if direction == 3 and x == 0:
            log.info("No wall added")
            log.debug("Trying to add wall on the left boundary.")
            return ""
        if direction == 2 and x == self.size[0] - 1:
            log.info("No wall added")
            log.debug("Trying to add wall on the right boundary.")
            return ""
        if direction == 1 and y == 0:
            log.info("No wall added")
            log.debug("Trying to add wall on the bottom boundary.")
            return ""
        if direction == 0 and y == self.size[1] - 1:
            log.info("No wall added")
            log.debug("Trying to add wall on the top boundary.")
            return ""

        if direction == 0:  # north bit value: 0001
            _y = y + 1

        elif direction == 1:  # south bit value: 0010
            _y = y - 1

        elif direction == 2:  # east bit value: 0100
            _x = x + 1

        elif direction == 3:  # west bit value: 1000
            _x = x - 1

        # clip the values between the max and min environment size.
        _x = 0 if _x < 0 else self.size[0] if _x > self.size[0] else _x
        _y = 0 if _y < 0 else self.size[0] if _y > self.size[0] else _y

        obstacleString = '''<DrawBlock x="''' + str(_x) + '''" y="45" z="''' + str(_y) + '''"  type="bedrock" />
        <DrawBlock x="''' + str(_x) + '''" y="46" z="''' + str(_y) + '''"  type="bedrock" />
        <DrawBlock x="''' + str(_x) + '''" y="47" z="''' + str(_y) + '''"  type="bedrock" />
        <DrawBlock x="''' + str(_x) + '''" y="48" z="''' + str(_y) + '''"  type="beacon" />
        '''

        log.debug("Obstacle string: %s", obstacleString)
        return obstacleString

    def makeTaskSpec(self):

        log = logging.getLogger('pyrl.environemnt.malmoenvironment.maketaskspec')
        ts = TaskSpecRLGlue.TaskSpec(discount_factor=0.9, reward_range=(-20.0, 20.0))

        ts.addDiscreteAction((0, 4))  # F, R, L, Pickup, Dropoff

        ts.addDiscreteObservation((0, self.size[0] - 1))  # for x
        ts.addDiscreteObservation((0, self.size[1] - 1))  # for y
        ts.addDiscreteObservation((0, 3))  # for direction/orientation
        ts.addDiscreteObservation((0, len(self.landmarks)))  # passenger location
        ts.addDiscreteObservation((0, len(self.landmarks) - 1))  # passenger destination

        ts.addContinuousObservation((0, 10.0))  # for the wall distance

        ts.setEpisodic()
        ts.setExtra(self.domainName)

        log.debug("Task spec from environment: %s", ts.toTaskSpec())

        return ts.toTaskSpec()

    def reset(self):
        log = logging.getLogger('pyrl.environment.malmoenvironment.reset')

        self.mission.startAt(1, 46, 1)
        self.mission.setViewpoint(1)
        landmarks = copy.deepcopy(self.landmarks)

        source_loc = random.choice(landmarks)  # first select the source to pick up from
        remaining_landmarks = [x for x in landmarks if x != source_loc]  # tentative destinations are any other landmark
        destination = random.choice(remaining_landmarks)  # now randomly choose the destination from above list

        self.passenger_location = landmarks.index(source_loc)
        self.destination = landmarks.index(destination)

        self.mission.drawBlock(source_loc[0], 47, source_loc[1], self.landmark_types[self.destination])

        log.debug("Mission XML: \n %s", self.mission_xml)

        try:
            malmo_env.startMission(self.mission, self.mission_record)
            time.sleep(2.5)
            wait_count = 0
            world_state = malmo_env.getWorldState()
            while not world_state.has_mission_begun:
                log.debug("world state: %s", pformat(world_state))
                for error in world_state.errors:
                    log.error("Error: %s", error.text)
                time.sleep(2.5)
                wait_count += 1
                world_state = malmo_env.getWorldState()
                if wait_count > 10:
                    log.error("Waited too long")
                    exit(1)
        except RuntimeError as e:
            log.error("Error: %s", e.message)
            exit(1)


    def makeObservation(self):

        log = logging.getLogger('pyrl.environment.malmoenvironment.makeobservation')

        landmarkTypes = ["redstone_block", "emerald_block", "lapis_block", "gold_block", "cobblestone", "quartz_block"]
        target_item = landmarkTypes[self.destination]

        # get the state from malmo
        world_state = malmo_env.getWorldState()

        # wait for first valid observation to be received
        while True:
            world_state = malmo_env.getWorldState()
            if not world_state.observations:
                log.warn("Waiting for observation")
                time.sleep(0.5)
                continue

            if not world_state.is_mission_running:
                log.error("Mission not running!!")
                break

            for error in world_state.errors:
                self.logger.error("Error: %s" % error.text)
            log.debug("Received: %s, Num. observations: %d", world_state, len(world_state.observations))
            log.debug("Latest observation text: %s", pformat(world_state.observations[-1]))
            log.debug("Rewards: %s", pformat(world_state.rewards))
            if len(world_state.observations) > 0 and not world_state.observations[-1].text == "{}":
                observation = json.loads(world_state.observations[-1].text)
                log.debug("Observation: %s", pformat(observation))
                log.debug("Keys: %s", observation.viewkeys())
                if u'XPos' not in observation or u'ZPos' not in observation or u'Yaw' not in observation:
                    turn = random.choice([1, -1])
                    turn_cmd = "turn " + str(turn)
                    log.error("Basic stats not present, issue a random turn: %s", turn_cmd)
                    malmo_env.sendCommand(turn_cmd)
                if u'LineOfSight' not in observation:
                    malmo_env.sendCommand("jump 0")
                    log.error("Incomplete observation received: %s", pformat(observation))
                else:
                    break

        if not world_state.is_mission_running:
            # if the environment ended for what ever reason, we need to send back
            # the information to the env_step so that it can identify the situation as mission ended
            # without succeeding (i.e. terminal = 1, or dead in this case)
            # else env_step gets stuck in getting the observation due to above being stuck in a loop
            log.debug("Mission completed: outcome : need to add outcome :")

        current_r = 0
        for reward in world_state.rewards:
            current_r += reward.getValue()

        log.debug("Received world state: %s", world_state)

        # this is for rl_glue
        return_obs = Observation()

        # observation is obtained from malmo as a json string; convert that to dict first
        observation = json.loads(world_state.observations[-1].text)
        self.lastObservation = copy.deepcopy(observation)
        log.debug("Received observation %s", pformat(observation))

        x, y = int(observation[u'XPos']), int(observation[u'ZPos'])
        self.direction = int(float(observation[u'Yaw']) / 90.0)

        if not self.getCompleted:
            self.getCompleted = self.checkHotbar(observation, target_item)

            if self.getCompleted:
                self.passenger_location = len(self.landmarks)

        if not u'LineOfSight' in observation:
            log.warning("Distance measure not obtained from Malmo, setting default 50.0")
            distance = 50.0
        else:
            distance = float(observation[u'LineOfSight'][u'distance'])

        return_obs.intArray = [x, y]
        return_obs.intArray += [self.direction]
        return_obs.intArray += [self.passenger_location, self.destination]
        return_obs.doubleArray = [distance]

        terminal = 0 if world_state.is_mission_running else 1

        return return_obs, current_r, terminal

    def env_init(self):
        log = logging.getLogger('pyrl.environment.malmoenvironment.envinit')

        log.info("Environment initialized")

        return self.makeTaskSpec()

    def env_start(self):

        log = logging.getLogger('pyrl.environment.malmoenvironment.envstart')

        # need to quit before you start a new mission, else it fails below with runtime error
        log.debug("Sending quit command to restart the mission")

        malmo_env.sendCommand("quit")

        log.debug("quit command sent to restart the mission")

        self.reset()

        log.info("Environment started")

        return_observation, reward, terminal = self.makeObservation()

        log.debug("First observation: %s, %f, %d", return_observation, reward, terminal)

        return return_observation

    def env_step(self, thisAction):

        log = logging.getLogger('pyrl.environment.malmoenvironment.envstep')

        log.debug("Received action: %s", thisAction.intArray)

        action = thisAction.intArray[0]

        malmo_action = self.actions[action]

        action_status = self.takeAction(malmo_action)

        obs, reward, terminal = self.makeObservation()

        log.debug("Observation: %s | reward: %f | terminal: %d", obs, reward, terminal)

        return_r_o = Reward_observation_terminal()
        return_r_o.o = obs
        return_r_o.r = reward if action_status else -10
        return_r_o.terminal = terminal

        log.debug("Observation after this step: %s %f", str(return_r_o.o.intArray), return_r_o.o.doubleArray[0])

        return return_r_o

    def takeAction(self, malmo_action):
        retryForObservation = 5  # num of times you want to retry to get the observation, else load back lastObservation
        log = logging.getLogger('pyrl.environment.malmoenvironment.takeaction')

        log.debug("Action to take: %s", malmo_action)

        landmarkTypes = ["redstone_block", "emerald_block", "lapis_block", "gold_block", "cobblestone", "quartz_block"]

        if "attack" in malmo_action:
            # poll for the world state to see if a breakable block of interest is in range
            observation = {}
            trial = 0
            while trial < retryForObservation:
                time.sleep(0.5)
                world_state = malmo_env.getWorldState()

                for error in world_state.errors:
                    self.logger.error("Error: %s" % error.text)
                log.debug("Received: %s, Num. observations: %d", world_state, len(world_state.observations))
                if world_state.is_mission_running and len(world_state.observations) > 0 and not \
                        world_state.observations[-1].text == "{}":
                    observation = json.loads(world_state.observations[-1].text)
                    if u'XPos' not in observation or u'ZPos' not in observation or u'Yaw' not in observation:
                        turn = random.choice([1, -1])
                        turn_cmd = "turn " + str(turn)
                        log.error("Basic stats not present, issue a random turn: %s", turn_cmd)
                        malmo_env.sendCommand(turn_cmd)
                    if u'LineOfSight' not in observation:
                        malmo_env.sendCommand("jump 0")
                    else:
                        self.lastObservation = copy.deepcopy(observation)
                        break
                trial += 1

            if not (observation[u'LineOfSight'][u'inRange'] == "True" and
                    observation[u'LineOfSight'][u'hitType'] == u'block' and
                    (observation[u'LineOfSight'][u'type'] in landmarkTypes)):
                log.warn("No breakable block detected, action failed. Get negative reward")
                observation = copy.deepcopy(self.lastObservation)
                return False

            if u'XPos' not in observation or u'ZPos' not in observation or \
                    u'Yaw' not in observation or u'LineOfSight' not in observation:
                observation = copy.deepcopy(self.lastObservation)
        elif "discardCurrentItem" in malmo_action:
            malmo_env.sendCommand("look 1")

            landmarkTypes = ["redstone_block", "emerald_block", "lapis_block", "gold_block", "cobblestone",
                             "quartz_block"]
            target_item = landmarkTypes[self.destination]

            # get the state from malmo
            world_state = malmo_env.getWorldState()

            # wait for first valid observation to be received
            while True:
                time.sleep(0.5)
                world_state = malmo_env.getWorldState()

                for error in world_state.errors:
                    self.logger.error("Error: %s" % error.text)
                log.debug("Received: %s, Num. observations: %d", world_state, len(world_state.observations))
                if world_state.is_mission_running and len(world_state.observations) > 0 and not \
                        world_state.observations[-1].text == "{}":
                    observation = json.loads(world_state.observations[-1].text)
                    if u'XPos' not in observation or u'ZPos' not in observation or u'Yaw' not in observation:
                        turn = random.choice([1, -1])
                        log.error("Basic stats not present, issue a random turns")
                        malmo_env.sendCommand("turn 1")
                        malmo_env.sendCommand("turn -1")
                    if u'LineOfSight' not in observation:
                        malmo_env.sendCommand("jump 0")
                        log.error("Incomplete observation received: %s", pformat(observation))
                    else:
                        break
                if not (observation[u'LineOfSight'][u'inRange'] == "True" and
                        observation[u'LineOfSight'][u'hitType'] == u'block' and
                        (observation[u'LineOfSight'][u'type'] == target_item)):
                    log.warn("Not correct destination, put down action failed. Get negative reward")
                    return False
            malmo_env.sendCommand("look -1")
        try:
            malmo_env.sendCommand(malmo_action)
            log.info("Action %s succeeded", malmo_action)
        except RuntimeError as e:
            log.error("Failed to send command %s", e)

        return True

    def checkInventory(self, observation, required):
        # need to find a way to see if the get task has been completed. one of the ways to do it is to check the
        # inventory, if the block has been acquired.
        for i in xrange(0, 39):
            key = 'InventorySlot_' + str(i) + '_item'
            if key in observation:
                item = observation[key]
                if item == required:
                    return True

        return False

    def checkHotbar(self, observation, required):
        # need to find a way to see if the get task has been completed. one of the ways to do it is to check the
        # inventory, if the block has been acquired.
        for i in xrange(0, 9):
            key = 'Hotbar_' + str(i) + '_item'
            if key in observation:
                item = observation[key]
                if item == required:
                    return True

        return False

    def env_cleanup(self):
        pass

    def env_message(self):
        return "I dunno what to do now! You should not reach here"
