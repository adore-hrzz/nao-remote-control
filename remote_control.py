import pygame
import math
from pygame import locals
from naoqi import ALProxy

DEFAULT_STEP = []
HIGH_STEP = [["StepHeight", 0.04], ["MaxStepX", 0.08]]
NORMAL_SPEED = 0.75
SLOW_SPEED = 0.01


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

NAO_IP = "192.168.1.103"
NAO_PORT = 9559

STAND = "Stand up"
SIT = "Sit down"

started = False
standing = False
forward = False

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

    gaitConfig = DEFAULT_STEP
    speed = NORMAL_SPEED

    while True:

        for e in pygame.event.get():
            print(e)
            if e.type == pygame.locals.JOYBUTTONDOWN:
                button = e.dict['button']
                if button == 0 and started:
                    behaviour.runBehavior(SIT)
                    motion.setStiffnesses("Body", 0.0)
                    standing = False
                if button == 1 and started:
                    motion.setStiffnesses("Body", 1.0)
                    behaviour.runBehavior(STAND)
                    motion.walkInit()
                    standing = True
                if button == 2 and started:
                    gaitConfig = HIGH_STEP
                    speed = SLOW_SPEED
                    print('Switching to high step')
                if button == 3 and started:
                    gaitConfig = DEFAULT_STEP
                    speed = NORMAL_SPEED
                    print('Switching to default step')
                if button == 9:
                    if not started:
                        print('Remote control enabled')
                        started = True
                    else:
                        print('Remote control disabled')
                        started = False
                if button == 8:
                    print('Shutting down remote control')
                    exit()
            if e.type == pygame.locals.JOYAXISMOTION and started and standing:
                axis = e.dict['axis']
                if axis == 0 or axis == 1:
                    x, y = dead_zone(joy.get_axis(1), -joy.get_axis(0), 0.05)
                    theta = math.atan2(y, x)
                    # theta = calculateSafeTurn(theta, turnAllowed)
                    motion.setWalkTargetVelocity(0, 0, theta / math.pi, 0.75)
                elif axis == 2 or axis == 3:
                    x, y = dead_zone(-joy.get_axis(3), joy.get_axis(2), 0.05)
                    # x, y = calculateSafeXY(x, y, leftAllowed, rightAllowed)
                    if x > 0:
                        forward = True
                    else:
                        forward = False
                    motion.setWalkTargetVelocity(x, 0, 0, speed, gaitConfig)

except KeyboardInterrupt:
    exit()
