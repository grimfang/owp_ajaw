#!/usr/bin/python
# -*- coding: utf-8 -*-

from pandac.PandaModules import loadPrcFileData
loadPrcFileData("",
"""
    window-title GrimFang OWP - Ajaw
    cursor-hidden 0
    show-frame-rate-meter 1
    model-path $MAIN_DIR/assets/
"""
)

from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject

class Main(ShowBase, DirectObject):
    def __init__(self):
        ShowBase.__init__(self)

        self.gameStarted = False

        # Setup Gui

        # Menu events

        # ingame events

    # Start everything needed to play the game
    def start(self):
        self.gameStarted = True

    # When the game stops, we do some cleanups
    def stop(self):
        pass
        
    def quit(self):
        if self.appRunner:
            self.appRunner.stop()
        else:
            exit(0)

APP = Main()
APP.run()