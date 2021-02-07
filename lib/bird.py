# -*- coding: utf-8 -*-
import cocos
from cocos.actions import *
from cocos.cocosnode import *
from cocos.collision_model import *
from cocos.director import *
import random
from atlas import *
from bird import *
from score import *
from game_controller import *
import common
import pipe

#constants
gravity = -800   #重力大小
upSpeed = {0: 280, 1: 150}    #点击后上升的高度，速度快更难控制

#vars
AIFunc = None
inputListener = None
spriteBirdName = None
isAIOn = True

#create the moving bird
def creatBird():
    #create bird animate
    birdNum = str(random.randint(0, 2))
    spriteBird = CollidableAnimatingSprite("bird_"+birdNum, common.visibleSize["width"]/2, common.visibleSize["height"]/2, atlas["bird0_0"]["width"]/2 - 9)
    
    return spriteBird

#handling touch events
class birdTouchHandler(cocos.layer.Layer):
    is_event_handler = True     #: enable director.window events

    def __init__(self, spriteBird, isEasy):
        super( birdTouchHandler, self ).__init__()
        self.spriteBird = spriteBird
        self.isEasy = isEasy

    def on_mouse_press (self, x, y, buttons, modifiers):
        """This function is called when any mouse button is pressed

        (x, y) are the physical coordinates of the mouse
        'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
        'modifiers' is a bitwise or of pyglet.window.key modifier constants
           (values like 'SHIFT', 'OPTION', 'ALT')
        """
        if pipe.birdai:
            return
        #点击屏幕时，如果小鸟没有到达游戏顶部，给它一个上升速度
        if self.spriteBird.position[1] < common.visibleSize["height"]-20:
            # result = x if condition else y三元运算
            self.spriteBird.velocity = (0, upSpeed[1 if self.isEasy else 0])  # 速度，x轴为0，y为 upSpeed

HANDLER_NAME = "birdTouchHandler"

def addTouchHandler(gameScene, isGamseStart, spriteBird, isEasy):
    if isGamseStart:
        handler = birdTouchHandler(spriteBird, isEasy)
        try:
            gameScene.add(handler, z=50, name=HANDLER_NAME)
        except:
            pass

#remove touch events
def removeBirdTouchHandler(gameScene):
    try:
        gameScene.remove(HANDLER_NAME)
    except:
        pass

#get spriteBird
def getSpriteBird():
    return spriteBird
