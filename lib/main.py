# -*- coding: utf-8 -*-
import cocos
from cocos.actions import *
from cocos.director import *
from cocos.scene import *
from game_controller import *
import common

def main():
    game_start()

    if director.scene:
        director.replace(game_controller.gameScene)
    else:
        director.run(game_controller.gameScene)