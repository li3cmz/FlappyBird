# -*- coding: utf-8 -*-
import os
import pyglet
import socket
import time

visibleSize = {"width":228, "height":512}

THISDIR = os.path.abspath(os.path.dirname(__file__))
DATADIR = os.path.normpath(os.path.join(THISDIR, '..', 'data'))
live = 0
remain = 0  # last time not finish, have a live time
# sock = socket.socket()
def load_image(path):
    return pyglet.image.load(os.path.join(DATADIR, path))

def savetoFile(message):
    what = ''
    for k in message:
        what = what + (','+k)
    what = what[1:len(what)]

    f = open(os.path.join(DATADIR, 'userdata.txt'), 'w')
    print what
    assert isinstance(what, basestring)
    f.write(what)
    f.flush()
    f.close()

def readFile():
    f = open(os.path.join(DATADIR, 'userdata.txt'), 'r')
    s = f.read()
    f.close()
    return s

def liveTimeStart():
    global live
    live = time.time()

def calculateTime():
    s = time.time()
    return int(s - live + remain)
