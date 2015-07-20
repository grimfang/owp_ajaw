#!/usr/bin/python
# -*- coding: utf-8 -*-

# Python imports
import __builtin__

# set the application Name
__builtin__.appName = "Ajaw"
__builtin__.versionstring = "15.07"

from pandac.PandaModules import loadPrcFileData
loadPrcFileData("",
"""
    window-title GrimFang OWP - Ajaw
    cursor-hidden 0
    show-frame-rate-meter 1
    model-path $MAIN_DIR/../assets/
"""
)

from direct.showbase.ShowBase import ShowBase
from direct.fsm.FSM import FSM
from panda3d.core import CollisionTraverser

from world import World

class Main(ShowBase, FSM):
    def __init__(self):
        ShowBase.__init__(self)
        FSM.__init__(self, "FSM-Game")

        self.enableParticles()
        self.disableMouse()
        self.setBackgroundColor(0, 0, 0)
        self.camLens.setFov(75)

        # enable collision handling
        base.cTrav = CollisionTraverser("base collision traverser")

        #self.menu = Menu()
        #self.options = OptionsMenu()

        self.accept("escape", self.__escape)
        self.accept("menu_quit", self.quit)
        self.accept("menu_start", lambda: self.request("Start"))
        self.accept("menu_options", lambda: self.request("Options"))

        self.request("Start")

    def enterMenu(self):
        pass
        #self.menu.show()

    def exitMenu(self):
        pass
        #self.menu.hide()

    def enterOptions(self):
        pass
        #self.options.show()

    def exitOptions(self):
        pass
        #self.options.hide()

    def enterStart(self):
        self.world = World()
        self.world.start()

    def exitStart(self):
        self.world.stop()

    def __escape(self):
        """A function that should be called when hitting the esc key or
        any other similar event happens"""
        if self.state == "Menu":
            self.quit()
        else:
            self.request("Menu")

    def quit(self):
        if self.appRunner:
            self.appRunner.stop()
        else:
            exit(0)

APP = Main()
APP.run()
