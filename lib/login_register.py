# -*- coding: utf-8 -*-
# this file is attempt
# to deal with the user log in and register
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
try:
    import pygame       # in order to play background music
except:
    print 'Your laptop has no module named pygame'

import pyglet

font = pyglet._ModuleProxy('font')
visibleSizeLR = {"width":228, "height":512}
NOTEND = -1
# when user login, we will check if he finished last game
# (client and server communicate will send this content)
# Username,State,Type,Score,Login
# state = -1 not end, 1 end  -------if he finished last game?
# type = 0, (easy/1), (hard/2),(ai/3) -----the mode of game

# another layer is to appear when player did not finish last game
def anotherLayer(strL, whatToSave):
    gameScene = Scene()
    gameLayer = Layer()

    # background
    bgSprite = cocos.sprite.Sprite(common.load_image('bg_night_registerbg.png'))
    bgSprite.position = visibleSizeLR["width"] / 2, visibleSizeLR["height"] / 2
    gameLayer.add(bgSprite, z=10)

    cl = ColorLayer(255, 255, 255, 255, width=visibleSizeLR['width'], height=visibleSizeLR["height"] / 5)
    cl.position = 0, 2.8*visibleSizeLR["height"] / 4
    gameLayer.add(cl, z=20)

    # message show in screen
    labelOne = Label("You have game is not finished, Continue?",
                     font_name="Times New Roman",
                     font_size=15,
                     color=(255, 0, 0, 255),
                     width=visibleSizeLR['width'] / 1.2,
                     multiline=True,
                     anchor_x="center",
                     anchor_y="center")
    labelOne.position = 2.5 * visibleSizeLR["width"] / 5, 4 * visibleSizeLR["height"] / 5
    gameLayer.add(labelOne, z=30)

    # menu, click OK -- gameold, click cancel -- game new
    tmp = SingleGameOldNew(strL, whatToSave)
    tmp.scale = 1.2
    gameLayer.add(tmp, z=30)

    gameScene.add(gameLayer, z=10)

    if director.scene:
        director.replace(gameScene)
    else:
        director.run(gameScene)


# menu deal with the choose, if OK click, we reload the last game
# else start a new game
class SingleGameOldNew(Menu):
    def __init__(self,strL, whatToSave):
        super(SingleGameOldNew, self).__init__()
        self.menu_valign = font.Text.CENTER
        self.menu_halign = font.Text.CENTER
        self.strL = strL
        self.whatToSave = whatToSave
        items = [
            (ImageMenuItem(common.load_image('game_ok.png'),
                                 self.gameOld)),
            (ImageMenuItem(common.load_image('game_cancel.png'),
                                 self.gameNew))
        ]
        self.create_menu(items, selected_effect=shake(),
                         unselected_effect=shake_back())

    def gameOld(self):
        print 'old game'
        common.savetoFile(self.strL)
        common.remain = float(self.strL[5]) # survive time
        game_controller.imOld = True
        game_controller.score = int(self.strL[3]) # last score
        game_controller.isEasy = True if int(self.strL[2]) == 1 else False
        game_controller.initGameLayer()
        if director.scene:
            director.replace(game_controller.gameScene)
        else:
            director.run(game_controller.gameScene)
        game_controller.singleGameReady()

    def gameNew(self):
        common.savetoFile(self.whatToSave)
        main.main()


# check message return from server, check not finish game
# Username,State,Type,Score,Login = xie,0,1,8,1
def checkLoad(username='login success!xie,0,1,8,1'):
    username = username[username.find('!')+1:len(username)]
    strL = username.split(',')

    whatToSave = []
    whatToSave.append(strL[0])  # username
    whatToSave.append('-1')  # game not finish
    whatToSave.append('0')  # not have type
    whatToSave.append('0')  # score
    whatToSave.append('1')  # login is true

    if strL[1] == str(NOTEND):   # last time the game is not finished
        anotherLayer(strL, whatToSave) # go back to answer the player
                                        # whether continue last game
    else:
        common.savetoFile(whatToSave)
        main.main()


# menu for log in and register
class SingleGameLoginRegisterMenu(Menu):
    # KI -- keyinput, type is mainmune, to get input
    def __init__(self, KI, gameLayer):
        super(SingleGameLoginRegisterMenu, self).__init__()
        self.menu_valign = font.Text.CENTER
        self.menu_halign = font.Text.CENTER
        self.KI = KI
        self.gameLayer = gameLayer
        items = [
            (ImageMenuItem(common.load_image('login.png'),
                                 self.gameLogin)),
            (ImageMenuItem(common.load_image('register.png'),
                                 self.gameRegister))
        ]
        self.create_menu(items, selected_effect=shake(),
                         unselected_effect=shake_back(), layout_strategy=fixedPositionMenuLayout(
                            [(1.9*visibleSizeLR["width"]/5, 2.3*visibleSizeLR["height"]/5),
                             (3.1*visibleSizeLR["width"]/5, 2.3*visibleSizeLR["height"]/5)]))

    def on_key_press(self, symbol, modifiers):
        return True

    def sendServer(self, message):
        if not network.connect():
            return 'Connect Server wrong, reenter and try'
        else:
            return network.sendServer(message)

    def printWrong(self, message):
        cl = ColorLayer(255, 255,255,255, width=visibleSizeLR['width'], height=visibleSizeLR["height"]/5)
        cl.position = 0, visibleSizeLR["height"]/25
        cl.do(cocos.actions.FadeOut(5))
        self.gameLayer.add(cl, z=25)
        labelerror = Label('',
                           font_name='Times New Roman',
                           font_size=15,
                           color=(255, 0, 0, 255),
                           width=visibleSizeLR['width'] / 1.2,
                           multiline=True,
                           anchor_x='center', anchor_y='center')
        labelerror.position = visibleSizeLR['width'] / 2, visibleSizeLR["height"] / 7
        labelerror.element.text = message
        labelerror.do(cocos.actions.FadeOut(5))
        self.gameLayer.add(labelerror, z=30)


    def gameLogin(self):
        u = self.KI.getname()
        x = self.KI.getpw()
        if len(x) > 0 and len(u) > 0:
            message = {'STATE': 'LOGIN', 'USER': str(u), 'PASS': str(x)}
            result = self.sendServer(message)

            print 'Input: '
            print '   {USER:' + message['USER'] + ', ' + 'PASSWORD:' + message['PASS'] + ', ' + 'STATE:' + message[
                'STATE'] + '}'

            if isinstance(result, basestring):
                print 'result: ' + result
                if result.find('success') != -1:
                    checkLoad(result)
                    # main.main()
                else:
                    self.printWrong(result)
                    # self.KI.reset()
            else:
                print 'get something wrong from server'


    def gameRegister(self):
        u = self.KI.getname()
        x = self.KI.getpw()
        if len(x) > 0 and len(u) > 0:
            try:
                message = {'STATE': 'REGISTER', 'USER': str(u), 'PASS': str(x)}

            except:
                self.printWrong("Invalid input!")
                return

            result = self.sendServer(message)

            print 'Input: '
            print '   {USER:' + message['USER'] + ', ' + 'PASSWORD:' + message['PASS'] + ', ' + 'STATE:' + message[
                'STATE'] + '}'

            if isinstance(result, basestring):
                print 'result: ' + result
                if result.find('success') != -1:
                    checkLoad(username=result+message['USER']+',0,0,0,1')
                    # main.main()
                else:
                    self.printWrong(result)
                    return
                    # self.KI.reset()
            else:
                print result
                print 'get something wrong from server'

# reload EntryMenuItem for input password -- example: ********
class EntryMenuItem2(MenuItem):
    """A menu item for entering a value.

    When selected, ``self.value`` is toggled, the callback function is
    called with ``self.value`` as argument."""

    value = property(lambda self: u''.join(self._value),
                     lambda self, v: setattr(self, '_value', list(v)))

    def __init__(self, label, callback_func, value, max_length=0):
        """Creates an Entry Menu Item

        :Parameters:
            `label` : string
                Item's label
            `callback_func` : function
                Callback function taking one argument.
            `value` : String
                Default value: any string
            `max_length` : integer
                Maximum value length (Defaults to 0 for unbound length)
        """
        self._value = list(value)
        self._label = label
        super(EntryMenuItem2, self).__init__("%s %s" % (label, value), callback_func)
        self.max_length = max_length

    def on_text(self, text):
        if self.max_length == 0 or len(self._value) < self.max_length:
            self._value.append(text)
            self._calculate_value()
        return True

    def on_key_press(self, symbol, modifiers):
        if symbol == 0xff08:
            try:
                self._value.pop()
            except IndexError:
                pass
            self._calculate_value()
            return True

    def _calculate_value(self):
        self.callback_func(self.value)
        val = ''
        for k in self.value:
            val = val+'*'
        new_text = u"%s %s" % (self._label, val)
        self.item.text = new_text
        self.item_selected.text = new_text


# key input
class MainMenu(Menu):
    def __init__( self ):
        super( MainMenu, self ).__init__()
        self.name = ''
        self.pw = ''
        self.font_item = {
            'font_name': 'Arial',
            'font_size': 15,
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'center',
            'color': (192, 192, 192, 255),
            'dpi': 96,
        }
        self.font_item_selected = {
            'font_name': 'Arial',
            'font_size': 18,
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'center',
            'color': (255, 255, 255, 255),
            'dpi': 96,
        }
        l = []
        l.append( EntryMenuItem(':', self.on_name, '') )
        l.append( EntryMenuItem2(':', self.on_quit,'' ) )

        self.create_menu( l,layout_strategy=fixedPositionMenuLayout(
                            [(2.4*visibleSizeLR["width"] / 5, 4.1 * visibleSizeLR["height"] / 5),
                             (2.4*visibleSizeLR["width"] / 5, 3.1 * visibleSizeLR["height"] / 5)]) )

    # def on_key_press(self, symbol, modifiers):
    #     return True

    def on_name( self, value ):
        self.name = value

    def on_quit( self, value ):
        self.pw = value

    def getpw(self):
        return self.pw

    def getname(self):
        return self.name


# when you click the .bat file, this function will run at first
def whatEnterGame():
    # pygame.init()
    try:
        pygame.mixer.init()
        # pygame.time.delay(100)
        pygame.mixer.music.load(os.path.join(common.DATADIR,'bg.mp3'))
        pygame.mixer.music.play(loops=-1)
    except:
        print 'Your laptop has no module named pygame, try pip install pygame\n' \
              'or you cannot listen the background music!\n' \
              'also you can try the venve(if in Linux/Mac source venve/bin/activate) in this folder\n'

    gameScene = Scene()
    gameLayer = Layer()

    # login or register background
    bgSprite = cocos.sprite.Sprite(common.load_image('bg_night_registerbg.png'))
    bgSprite.position = visibleSizeLR["width"] / 2, visibleSizeLR["height"] / 2

    # display 'user name'
    usrnameSprite = cocos.sprite.Sprite(common.load_image('usr_name.png'))
    usrnameSprite.position = visibleSizeLR["width"] / 5, 4 * visibleSizeLR["height"] / 5
    usrnameSprite.scale = 0.5

    cl = ColorLayer(255, 255, 255, 255, width=visibleSizeLR['width']/2, height=1)
    cl.position = 2*visibleSizeLR["width"] / 5, 3.9*visibleSizeLR["height"] / 5
    gameLayer.add(cl, z=20)
    # --------maybe the labelOne has not actual use, but I am not sure , so just keep here--------------
    labelOne = Label("",
                     font_name="Times New Roman",
                     font_size=15,
                     anchor_x="center",
                     anchor_y="center")
    labelOne.position = 2.5 * visibleSizeLR["width"] / 5, 4 * visibleSizeLR["height"] / 5
    # show 'password' label
    passSprite = cocos.sprite.Sprite(common.load_image('pass_word.png'))
    passSprite.position = visibleSizeLR["width"] / 5, 3 * visibleSizeLR["height"] / 5
    passSprite.scale = 0.5

    cl2 = copy.deepcopy(cl)
    cl2.position = 2*visibleSizeLR["width"] / 5, 2.9*visibleSizeLR["height"] / 5
    gameLayer.add(cl2, z=20)
    # this gameInput is to deal keyboard input
    gameInput = MainMenu()
    gameScene.add(gameInput, z=20)

    # menu for login or register
    game_chooseLR = SingleGameLoginRegisterMenu(gameInput, gameLayer)
    game_chooseLR.scale = 1.5

    gameLayer.add(bgSprite, z=10)
    gameLayer.add(usrnameSprite, z=20)
    gameLayer.add(labelOne, z=20)
    gameLayer.add(passSprite, z=20)
    gameLayer.add(game_chooseLR, z=20, name="game_choose")

    gameScene.add(gameLayer, z=10)

    if director.scene:
        director.replace(gameScene)
    else:
        director.run(gameScene)