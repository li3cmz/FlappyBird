#! /usr/bin/env python

import sys
import os
from cocos.director import *
from lib import main
from lib import login_register

if __name__ == '__main__':
    director.init(width=login_register.visibleSizeLR["width"],
                  height=login_register.visibleSizeLR["height"], caption="Flappy Bird")
    login_register.whatEnterGame()
