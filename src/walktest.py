import sys

from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from panda3d.core import Vec3
from panda3d.core import NodePath, PandaNode

class Runner(ShowBase, DirectObject):
    def __init__(self):
        ShowBase.__init__(self)
        self.accept("escape", sys.exit)

        # simple Player setup
        self.keyMap = {"left":0, "right":0, "forward":0, "backward":0}
        self.player = self.loader.loadModel("Character")
        self.player.setPos(0, -10, 0)
        self.player.reparentTo(self.render)

        self.enemy = self.loader.loadModel("Golem")
        self.enemy.setPos(0, 0, 0)
        self.enemy.reparentTo(self.render)

        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_right", self.setKey, ["right",1])
        self.accept("arrow_up", self.setKey, ["forward",1])
        self.accept("arrow_down", self.setKey, ["backward",1])
        self.accept("arrow_left-up", self.setKey, ["left",0])
        self.accept("arrow_right-up", self.setKey, ["right",0])
        self.accept("arrow_up-up", self.setKey, ["forward",0])
        self.accept("arrow_down-up", self.setKey, ["backward",0])
        self.taskMgr.add(self.move, "moveTask")

        #
        # Camera
        #
        # disable pandas default mouse-camera controls so we can handle the cam
        # movements by ourself
        self.disableMouse()
        # this variable will set an offset to the node the cam is attached to
        # and the point the camera looks at. By default the camera will look
        # directly at the node it is attached to
        self.lookatOffset = Vec3(0, 0, 2)
        # the initial cam distance
        self.camDistance = 7.0
        # an invisible object which will fly above the player and will be used to
        # track the camera on it
        self.camFloater = NodePath(PandaNode("playerCamFloater"))
        self.camFloater.reparentTo(self.render)
        self.taskMgr.add(self.updateCam, "task_camActualisation", priority=-4)

    def setKey(self, key, value):
        self.keyMap[key] = value

    def move(self, task):
        self.player.lookAt(self.enemy)
        self.player.setH(self.player, 180)
        if self.keyMap["left"] != 0:
            self.player.setX(self.player, 5 * globalClock.getDt())
        if self.keyMap["right"] != 0:
            self.player.setX(self.player, -5 * globalClock.getDt())
        if self.keyMap["forward"] != 0:
            self.player.setY(self.player, -5 * globalClock.getDt())
        if self.keyMap["backward"] != 0:
            self.player.setY(self.player, 5 * globalClock.getDt())
        return task.cont

    def updateCam(self, task):
        """This function will check the min and max distance of the camera to
        the defined model and will correct the position if the cam is to close
        or to far away"""
        self.camera.setX(self.player, 0)
        self.camera.setY(self.player, 6)
        self.camera.setZ(0.5)

        self.camFloater.setPos(self.enemy.getPos())
        self.camFloater.setX(self.enemy.getX() + self.lookatOffset.getX())
        self.camFloater.setY(self.enemy.getY() + self.lookatOffset.getY())
        self.camFloater.setZ(self.enemy.getZ() + self.lookatOffset.getZ())

        self.camera.lookAt(self.camFloater)

        # continue the task until it got manually stopped
        return task.cont

runner = Runner()
runner.run()
