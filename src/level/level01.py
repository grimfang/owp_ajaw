#!/usr/bin/env python

from panda3d.core import (
    AmbientLight,
    Spotlight,
    PointLight,
    PerspectiveLens,
    Filename,
    CollideMask)
from direct.particles.ParticleEffect import ParticleEffect

class Level01():
    def __init__(self):
        # Level model
        self.level = loader.loadModel("Level")

        """Logic connections INFO

        Switch.000 opens door Wooden_Door_Basic

        Switch.001-4 in correct order open Boulder_Door

        Key opens Boulder_Door.001

        Switch.005 opens Boulder_Door.002

        Defeating Golem opens Wooden_Door_Basic.001
        """

        self.switchLogic = {
            "Switch.000":"Wooden_Door_Basic",
            "Switch.001":"ORDER1",
            "Switch.002":"ORDER1",
            "Switch.003":"ORDER1",
            "Switch.004":"ORDER1",
            "ORDER1":"Boulder_Door",
            "Switch.005":"Boulder_Door.002"}
        self.switchOrderLogic = {
            "ORDER1", "Switch.001,Switch.002,Switch.003,Switch.004"}
        self.KeyDoorLogic = ["Boulder_Door.001"]
        self.chestLogic = {
            "Box_long_looseLid.000":"GET_Key",
            "Box_long_looseLid.001":"GET_Artifact"}
        self.gameEnd = "GET_artifact"

        # Set up all the little details
        #self.initTorchParticles()
        self.initSwitches()
        self.initDoors()
        self.initChests()

    def initTorchParticles(self):
        torchTops = self.level.findAllMatches("**/TorchTop*")
        fxList = ['../assets/TorchSmoke.ptf', '../assets/TorchFire.ptf']
        for torch in torchTops:
            for fx in fxList:
                p = ParticleEffect()
                p.loadConfig(Filename(fx))
                p.setPos(torch.getPos(render))
                p.start(self.level)

    def initLights(self):
        torches = self.level.findAllMatches("**/TorchTop*")
        for torch in torches:
            tLight = PointLight(torch.getName())
            tLight.setColor((.4, .2, .0, 1))
            tlnp = render.attachNewNode(tLight)
            tlnp.setPos(torch.getPos(render))
            render.setLight(tlnp)

        windows = self.level.findAllMatches("**/Window*")
        plates = self.level.findAllMatches("**/Plate*")
        spikes = self.level.findAllMatches("**/Spikes*")
        for window in windows:
            wLight = Spotlight(window.getName())
            lens = PerspectiveLens()
            wLight.setLens(lens)
            wLight.setColor((0.5, 0.4, 0.5, 1))
            wlnp = render.attachNewNode(wLight)
            wlnp.setPos(window.getPos(render))
            wlnp.lookAt((0, window.getY(), 0))
            for plate in plates:
                plate.setLight(wlnp)

        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((.1, .1, .025, 1))
        render.setLight(render.attachNewNode(ambientLight))

    def initSwitches(self):
        # Find switch armatures
        objects = self.level.findAllMatches('**/Switch')

        # Load switch anim
        switchAnimNode = loader.loadModel("Switch-Activate.egg")
        switchAnim = switchAnimNode.find("+AnimBundleNode").node().getBundle()

        self.switchControls = []

        for object in objects:
            bundle = object.node().getBundle(0)
            control = bundle.bindAnim(switchAnim, ~0)
            self.switchControls.append(control)

    def initChests(self):
        objects = self.level.findAllMatches('**/Box_long_looseLid')

        boxAnimNode = loader.loadModel("Box_long_looseLid-open.egg")
        boxAnim = boxAnimNode.find("+AnimBundleNode").node().getBundle()

        self.boxControls = []

        for object in objects:
            bundle = object.node().getBundle(0)
            control = bundle.bindAnim(boxAnim, ~0)
            self.boxControls.append(control)

    def initDoors(self):
        objects = self.level.findAllMatches('**/*Door*Armature')
        colliders = self.level.findAllMatches('**/*Door*collision')

        bdoorAnimNode = loader.loadModel("Boulder_Door-open.egg")
        bdoorAnim = bdoorAnimNode.find("+AnimBundleNode").node().getBundle()

        wdoorAnimNode = loader.loadModel("Wood_Door_Basic-open.egg")
        wdoorAnim = wdoorAnimNode.find("+AnimBundleNode").node().getBundle()

        self.doorControls = {}

        for object in objects:
            bundle = object.node().getBundle(0)
            print
            if "Boulder" in object.getName():
                control = bundle.bindAnim(bdoorAnim, ~0)
                self.doorControls.setdefault(object.getParent(),[control])
            elif "Wood" in object.getName():
                control = bundle.bindAnim(wdoorAnim, ~0)
                self.doorControls.setdefault(object.getParent(),[control])

        for collider in colliders:
            if "Boulder_Door_door_collision" in collider.getName():
                self.doorControls[collider.getParent()].append(collider)
            elif "Wodd" in collider.getName():
                #TODO FIXME: Typo Wodd -> Wood
                self.doorControls[collider.getParent()].append(collider)

        for key, value in self.doorControls.iteritems():
            #value[0].pose(23)
            value[0].play()
            value[1].node().setIntoCollideMask(CollideMask.allOff())

    def start(self):
        self.level.reparentTo(render)
        self.initLights()

        self.music = loader.loadMusic("../Design/Audio/Music/MayanJingle1_Ambient.ogg")
        self.music.play()

    def stop(self):
        self.level.removeNode()

    def getPlayerStartPoint(self):
        return self.level.find("**/Character")

    def getGolemStartPoint(self):
        return self.level.find("**/Golem")

    def activateSwitch(self, switch):
        if not switch in self.switchLogic.keys(): return
        if "ORDER" in self.switchLogic[switch]:
            order = self.switchOrderLogic[self.switchLogic[switch]]
            #TODO: Check if all switches before the actual one have already been activated. Otherwise reset all.
        else:
            self.__openDoor(self.switchLogic[switch])

    def openChest(self, chest):
        pass

    def defeatEnemy(self, enemy):
        pass

    def __openDoor(self, door):
        pass
