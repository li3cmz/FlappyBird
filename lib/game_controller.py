# -*- coding: utf-8 -*-
import cocos
from cocos.scene import *
from cocos.actions import *
from cocos.layer import *
from cocos.text  import *
from cocos.menu import *
import random
from atlas import *
from land import *
from bird import *
import pipe
from collision import *
import network
import common
import logoutAndAI
import collision

#vars
gameLayer = None
gameScene = None
spriteBird = None
land_1 = None
land_2 = None
startLayer = None
pipes = None
score = 0
listener = None
account = None
password = None
ipTextField = None
errorLabel = None
isGamseStart = False
isEasy = True
imOld = False    # false means a new game
birdOriginPosition = common.visibleSize['height'] / 2
escapehl = None

def initGameLayer():
    global spriteBird, gameLayer, land_1, land_2
    global gameScene, imOld
    if gameScene == None:
        gameScene = Scene()
    # gameLayer: 游戏场景所在的layer
    gameLayer = Layer()
    # add background
    bg = createAtlasSprite("bg_day")
    bg.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
    gameLayer.add(bg, z=0)

    lgout = logoutAndAI.logout()
    gameLayer.add(lgout, z=20)

    # add moving bird
    spriteBird = creatBird()
    # 先添加的层会被置于后添加的层之下。如果需要为它们指定先后次序，可以使用不同的z值
    gameLayer.add(spriteBird, z=20)
    # add moving land
    land_1, land_2 = createLand()
    gameLayer.add(land_1, z=10)
    gameLayer.add(land_2, z=10)
    # add gameLayer to gameScene
    gameScene.add(gameLayer, name='gameLayer')

def game_start():
    global gameScene, imOld
    # 给gameScene赋值
    if gameScene == None:
        gameScene = Scene()
    initGameLayer()     # already gameScane.add(layer)
    if not imOld:
        start_botton = SingleGameStartMenu()
        gameLayer.add(start_botton, z=20, name="start_button")
    else:
        singleGameReady()
    #connect(gameScene)

def createLabel(value, x, y):
    label=Label(value,  
        font_name='Times New Roman',  
        font_size=15, 
        color = (255,0,0,255),
        bold=True,
        width = common.visibleSize["width"] - 20,
        multiline = True,
        anchor_x='center',anchor_y='center')
    label.position = (x, y)
    return label

def rmEscape():
    try:
        print 'rm ai'
        gameScene.unschedule(escapehl)
    except:
        print 'add ai wrong'
        pass

# single game start button的回调函数
# ImageMenuItem(common.load_image("button_start.png"), self.gameStart---->
# -->再次调用singleGameReady()
def singleGameReady():
    global birdOriginPosition
    removeContent()
    print isEasy
    ready = createAtlasSprite("text_ready")
    ready.position = (common.visibleSize["width"]/2, common.visibleSize["height"] * 3/4)

    tutorial = createAtlasSprite("tutorial")
    tutorial.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
    
    spriteBird.position = (common.visibleSize["width"]/3, spriteBird.position[1])
    birdOriginPosition = spriteBird.position[1]
    #handling touch events
    class ReadyTouchHandler(cocos.layer.Layer):
        is_event_handler = True     #: enable director.window events

        def __init__(self):
            super(ReadyTouchHandler, self).__init__()

        def on_mouse_press(self, x, y, buttons, modifiers):
            """This function is called when any mouse button is pressed

            (x, y) are the physical coordinates of the mouse
            'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
            'modifiers' is a bitwise or of pyglet.window.key modifier constants
               (values like 'SHIFT', 'OPTION', 'ALT')
            """
            self.singleGameStart(buttons, x, y)
    
        # ready layer的回调函数
        def singleGameStart(self, eventType, x, y):
            global escapehl
            isGamseStart = True
            # 没有重力，直接飞走了
            common.liveTimeStart()

            def escape(dt):
                if spriteBird.position[1] < birdOriginPosition*4.15/5:
                    spriteBird.velocity = (0, 265)

            if pipe.birdai:
                print 'add ai'
                escapehl = escape
                gameScene.schedule(escape)

            spriteBird.gravity = gravity #gravity is from bird.py,  gravity
            # handling bird touch events
            addTouchHandler(gameScene, isGamseStart, spriteBird, isEasy)  # handle 本质也是一个层，on_press 是cocos layer里的
            #score = 0   #分数，飞过一个管子得到一分
            # add moving pipes
            pipes = pipe.createPipes(gameLayer, gameScene, spriteBird, score, isEasy)
            # 小鸟AI初始化
            # initAI(gameLayer)
            # add score
            createScoreLayer(gameLayer)
            # add collision detect
            addCollision(gameScene, gameLayer, spriteBird, pipes, land_1, land_2)
            # remove startLayer
            gameScene.remove(readyLayer)

    readyLayer = ReadyTouchHandler()
    readyLayer.add(ready)
    readyLayer.add(tutorial)
    gameScene.add(readyLayer, z=20)

def backToMainMenu():

    def showScore(gameLayer, score, best):
        intScore = int(score[0:score.find('/')])
        if intScore <= 5:
            medal = str(0)
        elif intScore <= 15:
            medal = str(3)
        elif intScore <= 30:
            medal = str(2)
        else:
            medal = str(1)
        # bgSprite = cocos.sprite.Sprite(pyglet.image.load("/Users/xieguorui/PycharmProjects/test/xie/"
        #                                                  "bg_night_registerbg.png"))
        # bgSprite.position = visibleSizeLR["width"] / 2, visibleSizeLR["height"] / 2

        bgScore = cocos.sprite.Sprite(common.load_image("score_panel.png"))
        bgScore.position = common.visibleSize["width"] / 2, 1.2 * common.visibleSize["height"] / 2

        bgMedal = cocos.sprite.Sprite(common.load_image("medals_" + medal + ".png"))
        bgMedal.position = common.visibleSize["width"] / 4.6, 1.18 * common.visibleSize["height"] / 2

        labelOne = Label(score,
                         font_name="Times New Roman",
                         font_size=13,
                         bold=True,
                         anchor_x="center",
                         anchor_y="center")
        labelOne.position = 1.6 * common.visibleSize["width"] / 2, 1.27 * common.visibleSize["height"] / 2

        labelOne2 = Label(best,
                          font_name="Times New Roman",
                          font_size=13,
                          color=(255, 0, 0, 255),

                          anchor_x="center",
                          anchor_y="center")
        labelOne2.position = 1.6 * common.visibleSize["width"] / 2, 1.1 * common.visibleSize["height"] / 2

        # gameLayer.add(bgSprite, z=10)
        gameLayer.add(bgScore, z=30)
        gameLayer.add(bgMedal, z=30)
        gameLayer.add(labelOne, z=30)
        gameLayer.add(labelOne2, z=30)
    x, y = pipe.getScore()
    showScore(gameLayer,x,y)
    restartButton = RestartMenu()
    gameLayer.add(restartButton, z=50)

def showNotice():
    # connected = connect(gameScene) # connect is from network.py
    # if not connected:
    #     content = "Cannot connect to server"
    #     showContent(content)
    # else:
    network.request_notice() # request_notice is from network.py

def showContent(content):
    removeContent()
    notice = createLabel(content, common.visibleSize["width"]/2+20, common.visibleSize["height"] * 8.5/10)
    gameLayer.add(notice, z=70, name="content")

def removeContent():
    try:
        gameLayer.remove("content")
    except Exception, e:
        pass

# choose the mode of game
class SingleGameChooseMenu(Menu):
    def __init__(self):
        super(SingleGameChooseMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        items = [
            (ImageMenuItem(common.load_image("button_easy.png"), self.gameEasy)),
            (ImageMenuItem(common.load_image("button_hard.png"), self.gameHard)),
            (ImageMenuItem(common.load_image("button_ai.png"), self.gameAI))
        ]
        self.create_menu(items, selected_effect=zoom_in(), unselected_effect=zoom_out())
    def gameEasy(self):
        print 'easy'
        global isEasy
        isEasy = True
        try:
            gameLayer.remove("game_choose")
        except:
            pass
        s = common.readFile()
        s = s.split(',')
        s[1] = '-1'
        s[2] = '1'
        s[3] = '0'
        message = {}
        pipe.birdai = False
        collision.birdAI = False
        message['name'] = 'gameEasy'
        message['USERNAME'] = s[0]
        message['STATE'] = s[1]
        message['TYPE'] = s[2]
        message['SCORE'] = s[3]
        message['LOGIN'] = s[4]
        common.remain = 0
        network.sendServer(message)
        common.savetoFile(s)
        singleGameReady()

    def gameHard(self):
        global isEasy
        isEasy = False
        try:
            gameLayer.remove("game_choose")
        except:
            pass
        s = common.readFile()
        s = s.split(',')
        s[1] = '-1'
        s[2] = '2'
        s[3] = '0'
        message = {}
        pipe.birdai = False
        collision.birdAI = False
        message['name'] = 'gameHard'
        message['USERNAME'] = s[0]
        message['STATE'] = s[1]
        message['TYPE'] = s[2]
        message['SCORE'] = s[3]
        message['LOGIN'] = s[4]
        common.remain = 0
        network.sendServer(message)
        common.savetoFile(s)
        singleGameReady()
        # 这里 加入 难易 程度选择Layer

    def gameAI(self):  # sendserver nothing use
        try:
            gameLayer.remove("game_choose")
        except:
            pass
        s = common.readFile()
        s = s.split(',')
        s[1] = '1'
        s[2] = '1'
        s[3] = '0'
        message = {}
        message['name'] = 'gameEasy'
        message['USERNAME'] = s[0]
        message['STATE'] = s[1]
        message['TYPE'] = s[2]
        message['SCORE'] = s[3]
        message['LOGIN'] = s[4]
        common.remain = 0
        network.sendServer(message)
        pipe.birdai = True
        collision.birdAI = True
        common.savetoFile(s)
        singleGameReady()

class RestartMenu(Menu):
    def __init__(self):  
        super(RestartMenu, self).__init__()
        self.menu_valign = CENTER  
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_restart.png"), self.initMainMenu)),
                (ImageMenuItem(common.load_image("button_notice.png"), showNotice))
                ]
        self.create_menu(items, selected_effect=zoom_out(), unselected_effect=zoom_in(),
                         layout_strategy=fixedPositionMenuLayout(
                             [(common.visibleSize["width"] / 2, 1.5 * common.visibleSize["height"] / 5),
                              (common.visibleSize["width"] / 2, 1.1 * common.visibleSize["height"] / 5)])
                         )

    def initMainMenu(self):
        try:
            # game_controller.gameLayer.remove("game_choose")
            game_controller.gameScene.remove("gameLayer")
        except:
            pass
        initGameLayer()
        game_choose = SingleGameChooseMenu()
        gameLayer.add(game_choose, z=20, name="game_choose")
        # ---------------------上面是我加的----------------------------
        # isGamseStart = False
        # singleGameReady()

class SingleGameStartMenu(Menu):
    def __init__(self):  
        super(SingleGameStartMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_start.png"), self.gameStart)),
                (ImageMenuItem(common.load_image("button_notice.png"), showNotice))
                ]  
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def gameStart(self):
        try:
            gameLayer.remove("start_button")  # remove layer start_button
        except:
            pass
        pipe.birdai = False
        collision.birdAI = False
        game_controller.rmEscape()

        game_choose = SingleGameChooseMenu()
        print 'add choose'
        gameLayer.add(game_choose, z=20, name="game_choose")
