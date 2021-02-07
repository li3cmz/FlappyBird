# -*- coding: utf-8 -*-

# when create pipes, we need to consider 3 types--easy, hard, birdAI
# different types have different pipeCount(random), pipeDistance, pipeInterval
#

from cocos.actions import *
from cocos.cocosnode import *
from cocos.collision_model import *
import random
from atlas import *
from bird import *
from score import *
from game_controller import *
import common
import network

# constants
pipeCount = 5
pipeHeight = 320
pipeWidth = 52
pipeDistance = {}   #上下管道间的距离 100
pipeInterval = {}    #两根管道的水平距离  180
waitDistance = 100    #开始时第一根管道距离屏幕最右侧的距离
heightOffset = 25     #管道的高度偏移值
# vars
PIPE_NEW = 0
PIPE_PASS = 1
pipes = {}    #contains nodes of pipes
pipeState = {}    #PIPE_NEW or PIPE_PASS
downPipeYPosition = {}    #朝下pipe的最下侧的y坐标
upPipeYPosition = {}  #朝上pipe的最上侧的y坐标
pipeIndex = 0
g_score = 0
liveTime =''
bestScore =''
birdai = False

class ActorModel(object):
    def __init__(self, cx, cy, half_width, half_height,name):
            self.cshape = CircleShape(eu.Vector2(center_x, center_y), radius)
            self.name = name

#             gamelayer
#   目前我觉得水管高度应该在这里修改，每次的位置、距离、间隔都只能改一次
def createPipes(layer, gameScene, spriteBird, score, isEasy):
    global g_score, movePipeFunc, calScoreFunc
    def initPipe():
        global pipeCount, pipeDistance, pipeInterval, birdai
        # --------------------------------------------
        if birdai:
            print 'change pipe count'
            pipeCount = 2
        else:
            pipeCount = 5
        # --------------------------------------------
        for i in range(0, pipeCount):  # [0,2)
            if birdai:
                pipeDistance[i] = 100
                pipeInterval[i] = 180
            else:
                if isEasy:
                    pipeDistance[i] = random.randint(180, 300)  # 水管上下之间距离
                    pipeInterval[i] = random.randint(180, 220)
                else:
                    pipeDistance[i] = random.randint(80, 180)
                    pipeInterval[i] = random.randint(120, 200)
            # 把downPipe和upPipe组合为singlePipe                  height 320   dis 100
            #                                 image,   center_x, center_y,               half_width, half_height):
            downPipe = CollidableRectSprite("pipe_down", 0, (pipeHeight + pipeDistance[i]), pipeWidth/2, pipeHeight/2) #朝下的pipe而非在下方的pipe
            upPipe = CollidableRectSprite("pipe_up", 0, 0, pipeWidth/2, pipeHeight/2)  #朝上的pipe而非在上方的pipe
            singlePipe = CocosNode()
            singlePipe.add(downPipe, name="downPipe")
            singlePipe.add(upPipe, name="upPipe")

            #设置管道高度和位置
            #            visibleSize = {"width":228, "height":512} 两根管道的水平距离 开始时第一根管道距离屏幕最右侧的距离  管道的高度偏移值
            # 两根管道现在的位置以Node位置为（0，0）
            singlePipe.position=(common.visibleSize["width"] + i*pipeInterval[i] + waitDistance, heightOffset)
            layer.add(singlePipe, z=10)
            pipes[i] = singlePipe
            pipeState[i] = PIPE_NEW


            # 朝上pipe的最上侧的y坐标 (185  ==
            #                            ||)
            upPipeYPosition[i] = heightOffset + pipeHeight/2
            # 朝下pipe的最下侧的y坐标 (285   ||
            #                             ==)
            downPipeYPosition[i] = heightOffset + pipeHeight/2 + pipeDistance[i]

    def movePipe(dt):
        moveDistance = common.visibleSize["width"]/(2*60) if (isEasy or birdai) else common.visibleSize["width"]/(90)   # 移动速度和land一致
        for i in range(0, pipeCount):
            pipes[i].position = (pipes[i].position[0]-moveDistance, pipes[i].position[1])
            if birdai:
                if pipes[i].position[0] < - pipeWidth/2:
                    pipeNode = pipes[i]
                    pipeState[i] = PIPE_NEW
                    next = i - 1
                    if next < 0: next = pipeCount - 1
                    pipeNode.position = (pipes[next].position[0] + pipeInterval[i], heightOffset)
                    upPipeYPosition[i] = heightOffset + pipeHeight / 2
                    downPipeYPosition[i] = heightOffset + pipeHeight / 2 + pipeDistance[i]
                    break
            else:
                if pipes[i].position[0] < -6 * pipeWidth:
                    pipeNode = pipes[i]
                    pipeState[i] = PIPE_NEW
                    next = i - 1
                    if next < 0: next = pipeCount - 1
                    pipeNode.position = (pipes[next].position[0] + pipeInterval[i], heightOffset)
                    upPipeYPosition[i] = heightOffset + pipeHeight / 2
                    downPipeYPosition[i] = heightOffset + pipeHeight / 2 + pipeDistance[i]
                    break
    def sendScore():
        s = common.readFile()
        s = s.split(',')
        s[3] = str(g_score)
        common.savetoFile(s)
        if g_score % 5 == 0:
            message = {}
            message['name'] = 'sendScore'
            message['USERNAME'] = s[0]
            message['STATE'] = s[1]
            message['TYPE'] = s[2]
            message['SCORE'] = s[3]
            message['LOGIN'] = s[4]
            message['LIVETIME'] = str(common.calculateTime())
            network.sendServer(message)

    def calScore(dt):
        global g_score
        birdXPosition = spriteBird.position[0]
        for i in range(0, pipeCount):
            if pipeState[i] == PIPE_NEW and pipes[i].position[0]< birdXPosition:
                pipeState[i] = PIPE_PASS
                g_score = g_score + 1
                sendScore()
                setSpriteScores(g_score) # show score on top of screen
    
    g_score = score
    initPipe()
    movePipeFunc = movePipe
    calScoreFunc = calScore
    gameScene.schedule(movePipe)
    gameScene.schedule(calScore)
    return pipes

def removeMovePipeFunc(gameScene):
    global movePipeFunc
    if movePipeFunc != None:
        gameScene.unschedule(movePipeFunc)

def removeCalScoreFunc(gameScene):
    global calScoreFunc, liveTime, bestScore
    if calScoreFunc != None:
        gameScene.unschedule(calScoreFunc)

        s = common.readFile()
        s = s.split(',')
        s[3] = str(g_score)
        common.savetoFile(s)
        message = {}
        if birdai:
            message['name'] = 'gameOverAI'
        else:
            message['name'] = 'gameOver'

        message['USERNAME'] = s[0]
        message['STATE'] = str(1)
        message['TYPE'] = s[2]
        message['SCORE'] = s[3]
        message['LOGIN'] = s[4]
        message['LIVETIME'] = str(common.calculateTime())
        liveTime = message['LIVETIME'] + 's'
        common.remain = 0
        bestScore = network.sendServer(message)

def getPipes():
    return pipes

def getUpPipeYPosition():
    return upPipeYPosition

def getPipeCount():
    return pipeCount

def getPipeWidth():
    return pipeWidth

def getPipeDistance():
    return pipeDistance

def getScore():
    return str(g_score)+'/'+liveTime, bestScore