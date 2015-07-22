from level.level01 import Level01
from player import Player
from gui.textfield import MessageWriter
from gui.hud import PlayerHUD
from direct.showbase.DirectObject import DirectObject
import helper

class World(DirectObject):
    def __init__(self):
        self.level = Level01()
        self.player = Player()
        self.msgWriter = MessageWriter()
        self.hud = PlayerHUD()

        self.musicAmbient = loader.loadMusic("MayanJingle1_Ambient.ogg")
        self.musicAmbient.setLoop(True)
        self.musicFight = loader.loadMusic("MayanJingle3_Fight.ogg")
        self.musicFight.setLoop(True)

    def start(self):
        helper.hide_cursor()
        self.level.start()
        self.player.start(self.level.getPlayerStartPoint())

        #self.musicAmbient.play()

        # catch all events that go from one class to another within the world
        # NOTE: events that stay in one class can be catched in the class itself
        #       to not pollute this class to much
        self.accept("Player_Activate", self.level.activateElement)
        self.accept("showMessage", self.msgWriter.setMessageAndShow)
        self.accept("ActionActive", self.hud.showActionKey)
        self.accept("ActionDeactive", self.hud.hideActionKey)

    def stop(self):
        helper.show_cursor()
        self.level.stop()
        self.player.stop()
        self.hud.hide()
        self.ignoreAll()
