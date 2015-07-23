from level.level01 import Level01
from player import Player
from golem import Golem
from gui.textfield import MessageWriter
from gui.hud import PlayerHUD
from direct.showbase.DirectObject import DirectObject
import helper

class World(DirectObject):
    def __init__(self):
        self.level = Level01()
        self.player = Player()
        self.golem = Golem()
        self.msgWriter = MessageWriter()
        self.hud = PlayerHUD()

        self.musicAmbient = loader.loadMusic("MayanJingle1_Ambient.ogg")
        self.musicAmbient.setLoop(True)
        self.musicFight = loader.loadMusic("MayanJingle3_Fight.ogg")
        self.musicFight.setLoop(True)
        self.musicGameOver = loader.loadMusic("MayanJingle5_GameOver.ogg")
        self.puzzleSolved = loader.loadSfx("MayanJingle4_PuzzleSolved.ogg")
        self.getItem = loader.loadSfx("MayanJingle2_GetItem.ogg")

    def start(self):
        helper.hide_cursor()
        self.level.start()
        self.player.start(self.level.getPlayerStartPoint())
        self.hud.show()
        self.hud.updateKeyCount(0)
        self.golem.start(self.level.getGolemStartPoint())

        self.playMusic("ambient")

        # catch all events that go from one class to another within the world
        # NOTE: events that stay in one class can be catched in the class itself
        #       to not pollute this class to much
        self.accept("Player_Activate", self.level.activateElement)
        self.accept("showMessage", self.msgWriter.setMessageAndShow)
        self.accept("ActionActive", self.hud.showActionKey)
        self.accept("ActionDeactive", self.hud.hideActionKey)
        self.accept("EnterFightMode", self.enterFight)
        self.accept("ExitFightMode", self.playMusic, ["ambient"])
        self.accept("PuzzleSolved", self.playSfx, ["puzzleSolved"])
        self.accept("updateKeyCount", self.hud.updateKeyCount)
        self.accept("player-die", self.player.die)
        self.accept("player-heal", self.player.heal)
        self.accept("setHealth", self.hud.setHealthStatus)
        self.accept("golemSeesPlayer", self.player.enterFightMode)
        self.accept("HitEnemy", self.golem.hit)
        self.accept("HitPlayer", self.player.hit)
        self.accept("GolemDestroyed", self.exitFight)
        self.accept("GameOver", self.gameOver)

    def enterFight(self):
        self.playMusic("fight")
        self.golem.activate(self.player.player)

    def exitFight(self):
        self.level.defeatEnemy("Golem")
        self.player.exitFightMode()

    def playMusic(self, music):
        if music == "fight":
            self.musicFight.play()
        else:
            self.musicAmbient.play()

    def gameOver(self):
        print "Game Over"
        self.stop()

    def playSfx(self, sfx):
        if sfx == "puzzleSolved":
            self.puzzleSolved.play()
        elif sfx == "getItem":
            self.getItem.play()

    def stop(self):
        helper.show_cursor()
        self.level.stop()
        self.player.stop()
        self.golem.stop()
        self.hud.hide()
        self.msgWriter.hide()
        self.ignoreAll()
