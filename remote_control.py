import pygame
import math
from pygame import locals
from naoqi import ALProxy


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

NAO_IP = "192.168.1.102"
NAO_PORT = 9559

started = False
enabled = False

try:
    behaviour = ALProxy("ALBehaviorManager", NAO_IP, NAO_PORT)
    motion = ALProxy("ALMotion", NAO_IP, NAO_PORT)
    memory = ALProxy("ALMemory", NAO_IP, NAO_PORT)
    print("Connected to the robot")
except:
    print("Error connecting to NAOqi on the robot")
    raise

try:
    joy = pygame.joystick.Joystick(0)
    joy.init()
    print("Enabled joystick %s" % joy.get_name())

    while True:
        for e in pygame.event.get():
            if not enabled:
                if e.type == pygame.locals.JOYBUTTONDOWN and e.dict['button'] == 9:
                    print('Remote control enabled')
                    enabled = True
            else:
                if e.type == pygame.locals.JOYBUTTONUP and e.dict['button'] == 6:
                    started = False
                    print('Control of the motion of the robot disabled')

                if e.type == pygame.locals.JOYBUTTONDOWN:
                    button = e.dict['button']
                    if button == 6:
                        started = True
                        print('Control of the motion of the robot enabled')
                    if button == 0:
                        motion.wakeUp()
                    if button == 1:
                        pass
                    if button == 2:
                        pass
                    if button == 3:
                        motion.rest()
                    if button == 9:
                        print('Remote control disabled')
                        enabled = False
                    if button == 8:
                        print('Shutting down remote control')
                        if motion.robotIsWakeUp():
                            motion.rest()
                        exit()
                if e.type == pygame.locals.JOYAXISMOTION and motion.robotIsWakeUp() and enabled:
                    x_turn, y_turn = dead_zone(joy.get_axis(1), -joy.get_axis(0), 0.05)
                    theta = math.atan2(y_turn, x_turn)
                    x, y = dead_zone(-joy.get_axis(3), -joy.get_axis(2), 0.05)
                    motion.moveToward(x, y, theta/math.pi)

except KeyboardInterrupt:
    exit()
