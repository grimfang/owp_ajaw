from level.level01 import Level01
from player import Player
from golem import Golem
from gui.textfield import MessageWriter
from gui.hud import PlayerHUD
from gui.loadingscreen import LoadingScreen
from gui.gameOverScreen import GameOverScreen
from direct.showbase.DirectObject import DirectObject
from direct.interval.LerpInterval import LerpFunc
from direct.interval.IntervalGlobal import Sequence
from direct.interval.FunctionInterval import Func
import helper
import time

class World(DirectObject):
    def __init__(self):
        self.loadingscreen = LoadingScreen()
        self.loadingscreen.show()
        self.gameoverscreen = GameOverScreen()
        self.level = Level01()
        self.loadingscreen.setLoadingValue(10)
        self.player = Player()
        self.loadingscreen.setLoadingValue(15)
        self.golem = Golem()
        self.loadingscreen.setLoadingValue(20)
        self.msgWriter = MessageWriter()
        self.loadingscreen.setLoadingValue(25)
        self.hud = PlayerHUD()
        self.loadingscreen.setLoadingValue(30)

        self.musicAmbient = loader.loadMusic("MayanJingle1_Ambient.ogg")
        self.musicAmbient.setLoop(True)
        self.musicAmbient.setVolume(1.0)
        self.musicFight = loader.loadMusic("MayanJingle3_Fight.ogg")
        self.musicFight.setLoop(True)
        self.musicFight.setVolume(1.0)
        self.musicGameOver = loader.loadMusic("MayanJingle5_GameOver.ogg")
        self.musicGameOver.setVolume(1.0)
        self.puzzleSolved = loader.loadSfx("MayanJingle4_PuzzleSolved.ogg")
        self.getItem = loader.loadSfx("MayanJingle2_GetItem.ogg")
        self.loadingscreen.setLoadingValue(40)

    def start(self):
        helper.hide_cursor()
        self.level.start()
        self.loadingscreen.setLoadingValue(55)
        self.player.start(self.level.getPlayerStartPoint())
        self.loadingscreen.setLoadingValue(65)
        self.hud.show()
        self.hud.updateKeyCount(0)
        self.loadingscreen.setLoadingValue(75)
        self.golem.start(self.level.getGolemStartPoint())
        self.loadingscreen.setLoadingValue(85)

        self.playMusic("Ambient")

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
        self.accept("Exit", base.messenger.send, ["escape"])
        self.loadingscreen.setLoadingValue(100)
        self.loadingscreen.hide()
        self.startTime = time.time()
        base.messenger.send(
            "showMessage",
            [_("Welcome to path of Kings, follow the signposts and try to survive this dungeon.\nmove with the arrow keys or w a s d\n\nGood luck...")])

    def stop(self):
        helper.show_cursor()
        self.level.stop()
        self.player.stop()
        self.golem.stop()
        self.hud.hide()
        self.msgWriter.hide()
        self.gameoverscreen.hide()
        self.ignoreAll()
        self.musicAmbient.stop()
        self.musicFight.stop()

    def cleanup(self):
        self.player.cleanup()
        del self.player
        self.golem.cleanup()
        del self.golem
        base.cTrav.clearColliders()

    def enterFight(self):
        self.playMusic("Fight")
        self.golem.activate(self.player.player)

    def exitFight(self):
        self.playMusic("Ambient")
        self.level.defeatEnemy("Golem")
        self.player.exitFightMode()

    def audioFade(self, volume, audio):
        audio.setVolume(volume)

    def playMusic(self, music):
        curMusic = None
        nextMusic = None
        # get the current running music
        if self.musicAmbient.status() == self.musicAmbient.PLAYING:
            curMusic = self.musicAmbient
        if self.musicFight.status() == self.musicFight.PLAYING:
            curMusic = self.musicFight
        if self.musicGameOver.status() == self.musicGameOver.PLAYING:
            curMusic = self.musicGameOver

        # check which music we want to play next
        if music == "Fight":
            nextMusic = self.musicFight
        elif music == "Ambient":
            nextMusic = self.musicAmbient
        elif music == "GameOver":
            nextMusic = self.musicGameOver
        else:
            # stop all music
            self.musicFight.stop()
            self.musicAmbient.stop()
            self.musicGameOver.stop()

        fade = None
        if curMusic != None and nextMusic != None:
            # fade from cur to next
            # fade in the new music
            lerpAudioFadeOut = LerpFunc(
                self.audioFade,
                fromData=1,
                toData=0,
                duration=1.0,
                extraArgs=[curMusic])
            lerpAudioFadeIn = LerpFunc(
                self.audioFade,
                fromData=0,
                toData=1,
                duration=1.0,
                extraArgs=[nextMusic])
            fade = Sequence(
                lerpAudioFadeOut,
                Func(curMusic.stop),
                Func(nextMusic.play),
                lerpAudioFadeIn,
                name="FadeMusic"
            )

        elif nextMusic != None:
            lerpAudioFadeIn = LerpFunc(
                self.audioFade,
                fromData = 0,
                toData = 1,
                duration = 1.0,
                extraArgs = [nextMusic])
            fade = Sequence(
                Func(nextMusic.play),
                lerpAudioFadeIn,
                name="FadeMusic"
            )
        if fade != None:
            fade.start()

    def gameOver(self, winLoose):
        self.playMusic("GameOver")
        helper.show_cursor()
        self.player.stop()
        self.endTime = time.time()
        self.gameoverscreen.show(winLoose, self.endTime - self.startTime)

    def playSfx(self, sfx):
        if sfx == "puzzleSolved":
            self.puzzleSolved.play()
        elif sfx == "getItem":
            self.getItem.play()
