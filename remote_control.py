#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import math
from pygame import locals
from naoqi import ALProxy
import ConfigParser
from optparse import OptionParser


def dead_zone(x_, y_, epsilon):
    if abs(x_) < epsilon:
        x_ = 0.
    if abs(y_) < epsilon:
        y_ = 0.
    return x_, y_

try:
    pygame.init()
    pygame.joystick.init()
except:
    print("Error initializing pygame")
    raise

o_parser = OptionParser()
o_parser.add_option("-f", "--file", help="Config file", dest="c_file", type="string", default="config.ini")
o_parser.add_option("-j", "--joystick", help="Joystick to use", dest="js_num", type="int", default=0)
(opts, args_) = o_parser.parse_args()
c_file = opts.c_file
js_num = opts.js_num
c_parser = ConfigParser.ConfigParser()

if not c_parser.read(c_file):
    print("Error opening the config file")
    exit()

NAO_IP = c_parser.get('robot', 'ip')
NAO_PORT = c_parser.getint('robot', 'port')

key_map = {int(key): value for key, value in (c_parser.items('key_bindings'))}

started = False
enabled = False

try:
    behaviour = ALProxy("ALBehaviorManager", NAO_IP, NAO_PORT)
    motion = ALProxy("ALMotion", NAO_IP, NAO_PORT)
    memory = ALProxy("ALMemory", NAO_IP, NAO_PORT)
    tts = ALProxy("ALTextToSpeech", NAO_IP, NAO_PORT)
    print("Connected to the robot")
except:
    print("Error connecting to NAOqi on the robot")
    raise

try:
    joy = pygame.joystick.Joystick(js_num)
    joy.init()
    print("Enabled joystick %s" % joy.get_name())

    while True:
        for e in pygame.event.get():
            if not enabled:
                if e.type == pygame.locals.JOYBUTTONDOWN and key_map[e.dict['button']] == 'enable':
                    print('Remote control enabled')
                    enabled = True
            else:
                if e.type == pygame.locals.JOYBUTTONUP and key_map[e.dict['button']] == 'start':
                    started = False
                    motion.stopMove()
                    print('Control of the motion of the robot disabled')

                if e.type == pygame.locals.JOYBUTTONDOWN:
                    button = e.dict['button']
                    if key_map[button] == 'start':
                        started = True
                        print('Control of the motion of the robot enabled')
                        motion.setStiffnesses("Head", 1.0)
                    elif not started:
                        if key_map[button] == 'exit':
                            print('Shutting down remote control')
                            if motion.robotIsWakeUp():
                                motion.rest()
                            exit()
                    elif key_map[button] == 'wake_up':
                        motion.wakeUp()
                    elif key_map[button] == 'rest':
                        motion.rest()
                    elif key_map[button] == 'enable':
                        print('Remote control disabled')
                        enabled = False
                        started = False
                    elif key_map[button] == 'say':
                        tts.say('Hello! I am NAO robot. I am here to inform you that I suck.')
                    elif key_map[button] == 'none':
                        pass
                    else:
                        try:
                            if motion.robotIsWakeUp():
                                behaviour.runBehavior(key_map[button])
                        except:
                            print('Behaviour %s not installed' % key_map[button])
                            raise
                if e.type == pygame.locals.JOYAXISMOTION and motion.robotIsWakeUp() and started:
                    x_turn, y_turn = dead_zone(-joy.get_axis(1), -joy.get_axis(0), 0.05)
                    theta = math.atan2(y_turn, x_turn)
                    x, y = dead_zone(-joy.get_axis(3), -joy.get_axis(2), 0.05)
                    motion.moveToward(x, y, theta/math.pi)
                if e.type == pygame.locals.JOYHATMOTION and started:
                    yaw, pitch = e.dict['value']

                    motion.changeAngles("HeadYaw", -yaw*0.087, 0.1)
                    motion.changeAngles("HeadPitch", -pitch*0.087, 0.1)

except KeyboardInterrupt:
    exit()
