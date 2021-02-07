# -*- coding: utf-8 -*-
# this file is attempt to deal with log out(quit the game)
import login_register
import os
import cocos
import copy
from cocos.scene import *
from cocos.text import Label
from cocos.layer import *
from cocos.menu import *
import common
import main
import network
import game_controller
import pipe
import collision

font = pyglet._ModuleProxy('font')

class logout(Menu):
    def __init__(self):
        super(logout, self).__init__()
        self.menu_valign = font.Text.CENTER
        self.menu_halign = font.Text.CENTER
        items = [
            (ImageMenuItem(common.load_image('logout.png'),
                                 self.gameQuit))
        ]
        self.create_menu(items, selected_effect=shake(),
                         unselected_effect=shake_back(),layout_strategy=fixedPositionMenuLayout(
                            [(login_register.visibleSizeLR["width"]/7,
                              5.7*login_register.visibleSizeLR["height"]/6)]))

    def on_key_press(self, symbol, modifiers):
        return True

    def gameQuit(self):
        print 'quit'

        # if game has started and logout buttun is clicked, just call
        # the gameQuit->gameOver->remove many schedules
        if collision.isStart:
            collision.gameQuit()
        else:
            game_controller.score = 0
            s = common.readFile()
            s = s.split(',')
            message = {}
            if pipe.birdai:
                message['name'] = 'gameQuitAI'
            else:
                message['name'] = 'gameQuit'
            message['USERNAME'] = s[0]
            message['STATE'] = str(1)
            message['TYPE'] = s[2]
            message['SCORE'] = s[3]
            message['LOGIN'] = str(0)
            message['LIVETIME'] = common.calculateTime()
            common.remain = 0
            # message['LOGOUT'] = 'LOGOUT'
            network.sendServer(message)
        try:
            # game_controller.gameLayer.remove("game_choose")
            game_controller.gameScene.remove("gameLayer")
        except:
            pass
        game_controller.imOld = False
        network.closeSock()
        login_register.whatEnterGame()
