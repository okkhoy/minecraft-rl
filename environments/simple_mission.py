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

import logging
import numpy
import json
import random
import time
import copy
import MalmoPython


class SimpleMalmoEnvironment:

    def __init__(self):
        log = logging.getLogger('SimpleMalmoEnvironment.init')
        self.actions = ["move 1", "turn 1", "turn -1", "attack 1", "discardCurrentItem"]
        self.landmark_types = ["redstone_block", "emerald_block", "lapis_block", "cobblestone", "gold_block",
                               "quartz_block"]
        self.size = [7, 7]
        self.landmarks = [[1, 2], [2, 5], [5, 6], [5, 2]]
        self.walls = [[2, 2, 2], [3, 2, 2], [3, 3, 2], [4, 3, 2], [1, 4, 2], [2, 5, 2], [2, 6, 2]],

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
                    <VideoProducer want_depth="false" viewpoint="1">
                        <Width>640</Width>
                        <Height>480</Height>
                    </VideoProducer>
                    <RewardForSendingCommand reward="-1" />
                </AgentHandlers>
                </AgentSection>
        </Mission>'''

        log.debug("Final mission XML String: %s", xml_string)

        return xml_string

    def draw_landmarks(self):
        log = logging.getLogger('SimpleMalmoEnvironment.drawlandmarks')

        landmarks = self.landmarks

        log.debug("Input landmarks: %s", landmarks)

        landmark_xml = '''<!-- draw landmarks -->'''

        for i, l in enumerate(landmarks):
            x, z = l
            landmark_xml += '''<DrawBlock x="''' + str(x) + '''" y="45" z="''' + str(z) + '''" type="''' + self.landmark_types[i % len(self.landmark_typesn)] + '''"/>'''

        return landmark_xml

    def draw_obstacles(self):
        log = logging.getLogger('SimpleMalmoEnvironment.drawobstacles')

        log.debug("Input walls: %s", walls)

        obstacle_xml = '''<!-- draw the obstacles -->'''
        for w in self.walls:
            log.debug("Adding obstacle: %s", w)
            x, y, direction = list(w)
            obstacle_string = self.drawObstacle(x, y, direction)
            log.debug("Obstacle string received: %s", obstacle_string)
            obstacle_xml = obstacle_xml + obstacle_string

        log.debug("Obstacle string obtained: %s", obstacle_xml)

        return obstacle_xml