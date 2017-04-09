"""
Created on April 3, 2017

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

import collections
import logging
import json
import random
import time
import copy

from pprint import pformat

import MalmoPython


malmo_env = MalmoPython.AgentHost()
list_compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

class SimpleMalmoEnvironment:

    def __init__(self):
        log = logging.getLogger('SimpleMalmoEnvironment.init')

        # actions available for the agent
        self.actions = ["move 1", "turn 1", "turn -1", "use 1"]

        # mission elements: landmarks, size, landmark types, obstacles etc.,
        self.landmark_types = ["redstone_block", "emerald_block", "lapis_block", "gold_block", "cobblestone",
                               "quartz_block"]
        self.size = [6, 6]
        self.landmarks = [[1, 2], [2, 5], [5, 6], [5, 2]]
        self.obstacles = [[2, 2, 2], [3, 2, 2], [3, 3, 2], [4, 3, 2], [1, 4, 2], [2, 5, 2], [2, 6, 2]]

        # mission related objects
        self.mission_xml = self.generate_malmo_environment_xml()
        log.debug("Obtained mission XML: \n %s", self.mission_xml)
        self.mission_record = MalmoPython.MissionRecordSpec()
        self.mission = MalmoPython.MissionSpec(self.mission_xml, True)
        log.info("Loaded mission XML")

        # observation stuff that needs to be passed to the learning algorithm
        self.item_location = 0
        self.current_agent_location = []
        self.destination = 0
        self.last_observation = None
        self.last_action = ""
        self.direction = 0
        self.is_get_completed = False

        log.debug("Verify experiment config:\n%s", pformat(self.__dict__))

    def generate_malmo_environment_xml(self):
        log = logging.getLogger('SimpleMalmoEnvironment.generateMalmoEnvironmentXML')
        xml_string = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
        <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <About>
                <Summary>Simple Malmo Environment</Summary>
            </About>
            <ServerSection>
                <ServerInitialConditions>
                    <Time><StartTime>1</StartTime></Time>
                    <Weather>clear</Weather>
                </ServerInitialConditions>
                <ServerHandlers>
                    <FlatWorldGenerator generatorString="3;7,220*1,5*3,2;3;,biome_1" forceReset="true" />
                <DrawingDecorator>
                    <!-- coordinates for cuboid are inclusive -->
                    <DrawCuboid x1="0" y1="46" z1="0" x2="''' + str(self.size[0]) + '''" y2="50" z2="''' + str(
                    self.size[1]) + '''" type="air" />            <!-- limits of our arena -->
                    <DrawCuboid x1="0" y1="45" z1="0" x2="''' + str(self.size[1]) + '''" y2="45" z2="''' + str(
                    self.size[1]) + '''" type="sandstone" />      <!-- floor of the arena -->
                    ''' + self.draw_landmarks() + self.draw_obstacles() + '''
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
                    <ObservationFromRay/>
                    <ObservationFromFullInventory/>
                    <ObservationFromDiscreteCell/>
                    <VideoProducer want_depth="false" viewpoint="1">
                        <Width>480</Width>
                        <Height>320</Height>
                    </VideoProducer>
                    <RewardForSendingCommand reward="-1" />
                </AgentHandlers>
                </AgentSection>
        </Mission>'''

        log.debug("Final mission XML String: \n%s", xml_string)

        return xml_string

    def draw_landmarks(self):
        log = logging.getLogger('SimpleMalmoEnvironment.drawLandmarks')

        landmarks = self.landmarks

        log.debug("Input landmarks: %s", landmarks)

        landmark_xml = '''<!-- draw landmarks -->'''

        for i, l in enumerate(landmarks):
            x, z = l
            landmark_xml += '''<DrawBlock x="''' + str(x) + '''" y="45" z="''' + str(z) + '''" type="''' + \
                            self.landmark_types[i % len(self.landmark_typesn)] + '''"/>'''

        return landmark_xml

    def draw_obstacles(self):
        log = logging.getLogger('SimpleMalmoEnvironment.drawObstacles')

        log.debug("Input walls: %s", self.obstacles)

        obstacle_xml = '''<!-- draw the obstacles -->'''
        for w in self.obstacles:
            log.debug("Adding obstacle: %s", w)
            x, y, direction = list(w)
            obstacle_string = self.draw_obstacle(x, y, direction)
            obstacle_xml = obstacle_xml + obstacle_string

        log.debug("Obstacle string obtained: %s", obstacle_xml)

        return obstacle_xml

    def draw_obstacle(self, x, y, direction):
        _x, _y = x, y

        log = logging.getLogger('SimpleMalmoEnvironment.drawObstacle')

        log.debug("Input x, y, d: %d, %d, %d", x, y, direction)

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

        obstacle_string = '''<DrawBlock x="''' + str(_x) + '''" y="45" z="''' + str(_y) + '''"  type="bedrock" />
                    <DrawBlock x="''' + str(_x) + '''" y="46" z="''' + str(_y) + '''"  type="bedrock" />
                    <DrawBlock x="''' + str(_x) + '''" y="47" z="''' + str(_y) + '''"  type="bedrock" />
                    <DrawBlock x="''' + str(_x) + '''" y="48" z="''' + str(_y) + '''"  type="beacon" />
                    '''

        log.debug("Obstacle string: %s", obstacle_string)
        return obstacle_string

    def makeObservation(self, action_status=False):
        log = logging.getLogger('SimpleMalmoEnvironment.makeObservation')

        target_item = self.landmark_types[self.destination]

        # get the state from malmo
        world_state = malmo_env.getWorldState()

        terminal = 0
        # wait for first valid observation to be received
        while True:
            time.sleep(0.1)
            world_state = malmo_env.getWorldState()

            for error in world_state.errors:
                self.logger.error("Error: %s" % error.text)
            log.debug("Received: %s, Num. observations: %d", world_state, len(world_state.observations))
            if world_state.is_mission_running and len(world_state.observations) > 0 \
                    and not world_state.observations[-1].text == "{}":
                observation = json.loads(world_state.observations[-1].text)
                if not u'XPos' in observation or not u'ZPos' in observation or not u'Yaw' in observation \
                        or not u'LineOfSight' in observation:
                    # hack to force an observation; sometimes the world_state.observations may not have LineOfSight
                    # this line below forces the environment to return an observation.
                    malmo_env.sendCommand("jump 0")
                    log.error("Incomplete observation received: %s", pformat(observation))
                else:
                    self.last_observation = copy.deepcopy(observation)
                    break
            if not world_state.is_mission_running:
                terminal = 1
                break

        if not world_state.is_mission_running:
            terminal = 1
            log.warn("Malmo mission ended")

        current_r = 0
        for reward in world_state.rewards:
            current_r += reward.getValue()

        log.debug("Received world state: %s", world_state)
        log.debug("Received observation %s", pformat(observation))

        x, y = int(observation[u'XPos']), int(observation[u'ZPos'])
        self.direction = int(observation[u'Yaw'])/90

        if not self.is_get_completed:
            self.is_get_completed = self.checkInventory(observation, target_item)

            if self.is_get_completed:
                self.item_location = len(self.landmarks)
                current_r += 11
                log.debug("Get successfully completed")
        elif self.is_get_completed:
            if "use" in self.last_action:
                if action_status is True:
                    current_r += 21
                    log.debug("Put successfully completed")
                    terminal = 1
                else:
                    current_r -= 10
                    log.debug("Put failed")

        distance = float(observation[u'LineOfSight'][u'distance'])
        return_observation = {"intobs": [x, y, self.direction, self.item_location, self.destination],
                              "floatobs": [distance]}

        return return_observation, current_r, terminal

    def reset(self):
        log = logging.getLogger('SimpleMalmoEnvironment.reset')
        self.mission.startAt(1, 46, 1)
        self.mission.setViewpoint(1)
        self.current_agent_location = [1, 1]

        # set mission variables - landmarks, source and destination
        landmarks = copy.deepcopy(self.landmarks)
        source_loc = random.choice(landmarks)  # first select the source to pick up from
        remaining_landmarks = [x for x in landmarks if x != source_loc]  # tentative destinations are any other landmark
        destination = random.choice(remaining_landmarks)  # now randomly choose the destination from above list

        self.item_location = landmarks.index(source_loc)
        self.destination = landmarks.index(destination)

        self.mission.drawBlock(source_loc[0], 47, source_loc[1], self.landmark_types[self.destination])

        retries = 3
        log.debug("Mission XML: \n %s", self.mission_xml)
        for retry in range(retries):
            try:
                malmo_env.startMission(self.mission, self.mission_record)
                time.sleep(2.5)

                world_state = malmo_env.getWorldState()
                if world_state.has_mission_begun:
                    break
            except RuntimeError as e:
                if retry == retries - 1:
                    log.error("Error starting mission. Max retries elapsed. Closing! %s", e.message)
                    exit(1)
                else:
                    time.sleep(2.5)

        world_state = malmo_env.getWorldState()

        while not world_state.has_mission_begun:
            log.debug("Waiting for mission to begin")
            time.sleep(0.1)
            world_state = malmo_env.getWorldState()
            for error in world_state.errors:
                log.error("Error: %s", error.text)

        return_observation, reward, terminal = self.makeObservation()

        return return_observation

    def env_start(self):
        log = logging.getLogger('SimpleMalmoEnvironment.envStart')

        # need to quit before you start a new mission, else it fails below with runtime error
        log.debug("Sending quit command to restart the mission")
        malmo_env.sendCommand("quit")

        self.reset()
        log.info("Environment started")

        return_observation, reward, terminal = self.makeObservation()
        log.debug("First observation: %s, %f, %d", return_observation, reward, terminal)

        return return_observation
