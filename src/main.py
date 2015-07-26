#!/usr/bin/python
# -*- coding: utf-8 -*-

# Python imports
import __builtin__
import os
import atexit
import logging
from direct.showbase.ShowBase import ShowBase
from direct.fsm.FSM import FSM
from panda3d.core import (
    CardMaker,
    TextureStage,
    TransparencyAttrib,
    LVecBase4f,
    NodePath,
    AudioSound,
    CollisionTraverser,
    CollisionHandlerPusher,
    WindowProperties,
    GraphicsPipe,
    MultiplexStream,
    Notify,
    Filename,
    ConfigPageManager,
    ConfigVariableBool,
    OFileStream,
    loadPrcFileData,
    loadPrcFile)
from direct.interval.IntervalGlobal import Sequence
from direct.interval.FunctionInterval import (
    Wait,
    Func)
from direct.interval.LerpInterval import LerpColorScaleInterval

# set the application Name
__builtin__.appName = "Ajaw"
__builtin__.versionstring = "15.07"
loadPrcFileData("",
"""
    window-title GrimFang OWP - Ajaw
    cursor-hidden 0
    #show-frame-rate-meter 1
    model-path $MAIN_DIR/../assets/
"""
)

#
# PATHS AND CONFIGS
#
home = os.path.expanduser("~")
__builtin__.basedir = os.path.join(home, __builtin__.appName)
if not os.path.exists(__builtin__.basedir):
    os.makedirs(__builtin__.basedir)
prcFile = os.path.join(__builtin__.basedir, "%s.prc"%__builtin__.appName)
if os.path.exists(prcFile):
    loadPrcFile(Filename.fromOsSpecific(prcFile))
#
# PATHS AND CONFIGS END
#

#
# LOGGING
#
# setup Logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    filename=os.path.join(__builtin__.basedir, "game.log"),
    datefmt="%d-%m-%Y %H:%M:%S",
    filemode="w")

# First log entry, the program version
logging.info("Version %s" % versionstring)

# redirect the notify output to a log file
nout = MultiplexStream()
Notify.ptr().setOstreamPtr(nout, 0)
nout.addFile(Filename(os.path.join(__builtin__.basedir, "game_p3d.log")))
#
# LOGGING END
#

from world import World
from gui.mainmenu import Menu
from gui.optionsmenu import OptionsMenu
import helper

class Main(ShowBase, FSM):
    def __init__(self):
        ShowBase.__init__(self)
        FSM.__init__(self, "FSM-Game")

        #
        # BASIC APPLICATION CONFIGURATIONS
        #
        self.disableMouse()
        self.setBackgroundColor(0, 0, 0)
        self.camLens.setFov(75)
        base.camLens.setNear(0.8)
        helper.hide_cursor()

        #
        # Basic Application configuration
        #
        # check if the config file hasn't been created
        if not os.path.exists(prcFile):
            self.__writeConfig()
            # set window properties
            # clear all properties not previously set
            base.win.clearRejectedProperties()
            # setup new window properties
            props = WindowProperties()
            # Fullscreen
            props.setFullscreen(True)
            # get the displays width and height
            w = self.pipe.getDisplayWidth()
            h = self.pipe.getDisplayHeight()
            # set the window size to the screen resolution
            props.setSize(w, h)
            # request the new properties
            base.win.requestProperties(props)
        atexit.register(self.__writeConfig)

        mute = ConfigVariableBool("audio-mute", False).getValue()
        if mute:
            base.disableAllAudio()
        else:
            base.enableAllAudio()
        particles = ConfigVariableBool("particles-enabled", True).getValue()
        if particles:
            self.enableParticles()

        # enable collision handling
        base.cTrav = CollisionTraverser("base collision traverser")
        base.pusher = CollisionHandlerPusher()
        base.pusher.addInPattern('%fn-in-%in')
        base.pusher.addOutPattern('%fn-out-%in')

        self.menu = Menu()
        self.options = OptionsMenu()

        self.musicMenu = loader.loadMusic("MayanJingle6_Menu.ogg")
        self.musicMenu.setLoop(True)

        self.accept("escape", self.__escape)
        self.accept("menu_quit", self.quit)
        self.accept("menu_start", lambda: self.request("Start"))
        self.accept("menu_options", lambda: self.request("Options"))
        self.accept("options_back", self.__escape)



        self.request("Intro")

    def enterIntro(self):
        cm = CardMaker("fade")
        cm.setFrameFullscreenQuad()
        self.gfLogo = NodePath(cm.generate())
        self.gfLogo.setTransparency(TransparencyAttrib.MAlpha)
        gfLogotex = loader.loadTexture('GrimFangLogo.png')
        gfLogots = TextureStage('gfLogoTS')
        gfLogots.setMode(TextureStage.MReplace)
        self.gfLogo.setTexture(gfLogots, gfLogotex)
        self.gfLogo.setY(-50)
        self.gfLogo.reparentTo(render2d)
        self.gfLogo.hide()

        self.pandaLogo = NodePath(cm.generate())
        self.pandaLogo.setTransparency(TransparencyAttrib.MAlpha)
        pandaLogotex = loader.loadTexture('Panda3DLogo.png')
        pandaLogots = TextureStage('pandaLogoTS')
        pandaLogots.setMode(TextureStage.MReplace)
        self.pandaLogo.setTexture(pandaLogots, pandaLogotex)
        self.pandaLogo.setY(-50)
        self.pandaLogo.reparentTo(render2d)
        self.pandaLogo.hide()


        gfFadeInInterval = LerpColorScaleInterval(
            self.gfLogo,
            2,
            LVecBase4f(0.0,0.0,0.0,1.0),
            LVecBase4f(0.0,0.0,0.0,0.0))

        gfFadeOutInterval = LerpColorScaleInterval(
            self.gfLogo,
            2,
            LVecBase4f(0.0,0.0,0.0,0.0),
            LVecBase4f(0.0,0.0,0.0,1.0))

        p3dFadeInInterval = LerpColorScaleInterval(
            self.pandaLogo,
            2,
            LVecBase4f(0.0,0.0,0.0,1.0),
            LVecBase4f(0.0,0.0,0.0,0.0))

        p3dFadeOutInterval = LerpColorScaleInterval(
            self.pandaLogo,
            2,
            LVecBase4f(0.0,0.0,0.0,0.0),
            LVecBase4f(0.0,0.0,0.0,1.0))

        self.fadeInOut = Sequence(
            Func(self.pandaLogo.show),
            p3dFadeInInterval,
            Wait(1.0),
            p3dFadeOutInterval,
            Wait(0.5),
            Func(self.pandaLogo.hide),
            Func(self.gfLogo.show),
            gfFadeInInterval,
            Wait(1.0),
            gfFadeOutInterval,
            Wait(0.5),
            Func(self.gfLogo.hide),
            Func(self.request, "Menu"),
            Func(helper.show_cursor),
            name="fadeInOut")
        self.fadeInOut.start()

    def enterMenu(self):
        if self.musicMenu.status() == AudioSound.READY:
            self.musicMenu.play()
        self.menu.show()

    def exitMenu(self):
        self.menu.hide()

    def enterOptions(self):
        self.options.show()

    def exitOptions(self):
        self.options.hide()

    def enterStart(self):
        self.musicMenu.stop()
        self.world = World()
        self.world.start()

    def exitStart(self):
        self.world.stop()
        self.world.cleanup()
        del self.world

    def __escape(self):
        """A function that should be called when hitting the esc key or
        any other similar event happens"""
        if self.fadeInOut.isPlaying():
            self.fadeInOut.finish()
            self.pandaLogo.hide()
            self.gfLogo.hide()
        elif self.state == "Menu":
            self.quit()
        else:
            self.request("Menu")

    def quit(self):
        if self.appRunner:
            self.appRunner.stop()
        else:
            exit(0)

    def __writeConfig(self):
        """Save current config in the prc file or if no prc file exists
        create one. The prc file is set in the prcFile variable"""
        page = None
        particles = str(base.particleMgrEnabled)
        volume = str(round(base.musicManager.getVolume(), 2))
        if os.path.exists(prcFile):
            page = loadPrcFile(Filename.fromOsSpecific(prcFile))
            removeDecls = []
            for dec in range(page.getNumDeclarations()):
                # Check if our variables are given.
                # NOTE: This check has to be done to not loose our base or other
                #       manual config changes by the user
                if page.getVariableName(dec) == "particles-enabled":
                    decl = page.modifyDeclaration(dec)
                    removeDecls.append(decl)
                elif page.getVariableName(dec) == "audio-mute":
                    decl = page.modifyDeclaration(dec)
                    removeDecls.append(decl)
                elif page.getVariableName(dec) == "audio-volume":
                    decl = page.modifyDeclaration(dec)
                    removeDecls.append(decl)
            for dec in removeDecls:
                page.deleteDeclaration(dec)
            # Particles
            particles = "#f" if not base.particleMgrEnabled else "#t"
            page.makeDeclaration("particles-enabled", particles)
            # audio
            page.makeDeclaration("audio-volume", volume)
            mute = "#f" if base.AppHasAudioFocus else "#t"
            page.makeDeclaration("audio-mute", mute)
        else:
            cpMgr = ConfigPageManager.getGlobalPtr()
            page = cpMgr.makeExplicitPage("%s Pandaconfig"%appName)
            page.makeDeclaration("load-display", "pandagl")
            # get the displays width and height
            w = self.pipe.getDisplayWidth()
            h = self.pipe.getDisplayHeight()
            # set the window size in the config file
            page.makeDeclaration("win-size", "%d %d"%(w, h))
            # set the default to fullscreen in the config file
            page.makeDeclaration("fullscreen", "1")
            # particles
            page.makeDeclaration("particles-enabled", "#t")
            # audio
            page.makeDeclaration("audio-volume", volume)
            page.makeDeclaration("audio-mute", "#f")
        # create a stream to the specified config file
        configfile = OFileStream(prcFile)
        # and now write it out
        page.write(configfile)
        # close the stream
        configfile.close()

APP = Main()
if __debug__:
    import debug
    debug.setupDebugHelp(APP)
APP.run()
