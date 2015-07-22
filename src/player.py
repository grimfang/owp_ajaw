from direct.actor.Actor import Actor
from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from panda3d.core import (
    Vec3,
    NodePath,
    PandaNode,
    CollisionSphere,
    CollisionRay,
    CollisionSegment,
    CollisionNode,
    CollisionHandlerFloor,
    CollisionHandlerEvent,
    PointLight)
from direct.interval.LerpInterval import LerpPosInterval

class Player(FSM, DirectObject):
    NormalMode = "Normal"
    FightMode = "Fight"

    def __init__(self):
        FSM.__init__(self, "FSM-Player")

        #
        # PLAYER CONTROLS AND CAMERA
        #
        self.player = Actor("Character", {
            "Idle":"Character-Idle",
            "Run":"Character-Run",
            "Activate":"Character-Activate",
            "Death":"Character-Death",
            "Jump":"Character-Jump",
            "Hit":"Character-Hit",
            "Fight_Attack":"Character-FightAttack",
            "Fight_Idle":"Character-FightIdle",
            "Fight_Left":"Character-FightLeft",
            "Fight_Right":"Character-FightRight"})
        self.player.setBlend(frameBlend = True)
        self.keyMap = {"left":0, "right":0, "forward":0, "backward":0, "center":0}
        # this mode will be used to determine in which move mode the player currently is
        self.mode = Player.NormalMode
        self.trackedEnemy = None
        # this variable will set an offset to the node the cam is attached to
        # and the point the camera looks at. By default the camera will look
        # directly at the node it is attached to
        self.lookatOffset = Vec3(0, 0, 1)
        # the initial cam distance
        self.fightCamDistance = 7.0
        # the next two vars will set the min and max distance the cam can have
        # to the node it is attached to
        self.maxCamDistance = 3.0
        self.minCamDistance = 0.5
        # the initial cam distance
        self.camDistance = (self.maxCamDistance - self.minCamDistance) / 2.0 + self.minCamDistance
        # the next two vars set the min and max distance on the Z-Axis to the
        # node the cam is attached to
        self.maxCamHeightDist = 3.0
        self.minCamHeightDist = 1.5
        # the average camera height
        self.camHeightAvg = (self.maxCamHeightDist - self.minCamHeightDist) / 2.0 + self.minCamHeightDist
        # the initial cam height
        self.camHeight = self.camHeightAvg
        # a time to keep the cam zoom at a specific speed independent of
        # current framerate
        self.camElapsed = 0.0
        # an invisible object which will fly above the player and will be used to
        # track the camera on it
        self.camFloater = NodePath(PandaNode("playerCamFloater"))
        self.camFloater.reparentTo(render)

        #
        # PLAYER COLLISION DETECTION AND PHYSICS
        #
        self.playerSphere = CollisionSphere(0, 0, 0.8, 0.7)
        self.playerCollision = self.player.attachNewNode(CollisionNode("playerCollision"))
        self.playerCollision.node().addSolid(self.playerSphere)
        base.pusher.addCollider(self.playerCollision, self.player)
        base.cTrav.addCollider(self.playerCollision, base.pusher)
        # The foot collision checks
        self.footRay = CollisionRay(0, 0, 0, 0, 0, -1)
        self.playerFootRay = self.player.attachNewNode(CollisionNode("playerFootCollision"))
        self.playerFootRay.node().addSolid(self.footRay)
        self.playerFootRay.node().setIntoCollideMask(0)
        self.playerFootRay.show()
        self.lifter = CollisionHandlerFloor()
        self.lifter.addCollider(self.playerFootRay, self.player)
        self.lifter.setMaxVelocity(0.1)
        base.cTrav.addCollider(self.playerFootRay, self.lifter)
        # a collision segment slightly in front of the player to check for jump ledges
        self.jumpCheckSegment = CollisionSegment(0, 0.1, 0, 0, 0.1, -1)
        self.playerJumpRay = self.player.attachNewNode(CollisionNode("playerJumpCollision"))
        self.playerJumpRay.node().addSolid(self.jumpCheckSegment)
        self.playerJumpRay.node().setIntoCollideMask(0)
        self.jumper = CollisionHandlerEvent()
        self.jumper.addOutPattern('%fn-out')
        base.cTrav.addCollider(self.playerJumpRay, self.jumper)

    def start(self, startPoint):
        self.player.setPos(startPoint.getPos())
        self.player.setHpr(startPoint.getHpr())
        self.player.reparentTo(render)

        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_right", self.setKey, ["right",1])
        self.accept("arrow_up", self.setKey, ["forward",1])
        self.accept("arrow_down", self.setKey, ["backward",1])
        self.accept("arrow_left-up", self.setKey, ["left",0])
        self.accept("arrow_right-up", self.setKey, ["right",0])
        self.accept("arrow_up-up", self.setKey, ["forward",0])
        self.accept("arrow_down-up", self.setKey, ["backward",0])
        self.accept("a", self.setKey, ["left",1])
        self.accept("d", self.setKey, ["right",1])
        self.accept("w", self.setKey, ["forward",1])
        self.accept("s", self.setKey, ["backward",1])
        self.accept("a-up", self.setKey, ["left",0])
        self.accept("d-up", self.setKey, ["right",0])
        self.accept("w-up", self.setKey, ["forward",0])
        self.accept("s-up", self.setKey, ["backward",0])
        self.accept("q", self.setKey, ["center",1])
        self.accept("q-up", self.setKey, ["center",0])
        self.accept("home", self.setKey, ["center",1])
        self.accept("home-up", self.setKey, ["center",0])
        self.acceptOnce("+", self.zoom, [True])
        self.acceptOnce("-", self.zoom, [False])
        self.acceptOnce("enter", self.request, ["Activate"])
        self.acceptOnce("e", self.request, ["Activate"])

        self.accept("playerJumpCollision-out", self.jump)

        taskMgr.add(self.move, "task_movement", priority=-10)
        taskMgr.add(self.updateCam, "task_camActualisation", priority=-4)

        camera.setPos(self.player, 0, self.camDistance, self.camHeightAvg)

        self.request("Idle")

    def stop(self):
        self.ignoreAll()
        self.player.hide()

    def setKey(self, key, value):
        self.keyMap[key] = value

    def jump(self, extraArg):
        print "JUMPING", extraArg

    def move(self, task):
        dt = globalClock.getDt()

        ac = self.player.getAnimControl("Activate")
        if ac.isPlaying():
            return task.cont

        if self.mode == Player.NormalMode:
            self.__normalMove(dt)
        else:
            self.__fightMove(dt)
        return task.cont

    def __normalMove(self, dt):
        requestState = "Idle"
        if self.keyMap["left"] != 0:
            self.player.setH(self.player.getH() + 250 * globalClock.getDt())
            requestState = "Run"
        if self.keyMap["right"] != 0:
            self.player.setH(self.player.getH() - 250 * globalClock.getDt())
            requestState = "Run"
        if self.keyMap["forward"] != 0:
            self.player.setY(self.player, -2 * dt)
            requestState = "Run"
        if self.keyMap["backward"] != 0:
            self.player.setY(self.player, 2 * dt)
            requestState = "RunReverse"
        if self.state != requestState:
            self.request(requestState)

    def __fightMove(self, dt):
        if self.trackedEnemy == None: return
        requestState = "Fight_Idle"
        self.player.lookAt(self.trackedEnemy)
        self.player.setH(self.player, 180)
        if self.keyMap["left"] != 0:
            self.player.setX(self.player, 5 * dt)
            requestState = "Fight_Left"
        elif self.keyMap["right"] != 0:
            self.player.setX(self.player, -5 * dt)
            requestState = "Fight_Right"
        elif self.keyMap["forward"] != 0:
            self.player.setY(self.player, -5 * dt)
            requestState = "Run"
        elif self.keyMap["backward"] != 0:
            self.player.setY(self.player, 5 * dt)
            requestState = "RunReverse"
        if self.state != requestState:
            self.request(requestState)

    def updateCam(self, task):
        if self.mode == Player.NormalMode:
            self.__normalCam()
        else:
            self.__fightCam()
        return task.cont

    def zoom(self, zoomIn):
        if zoomIn:
            if self.maxCamDistance > self.minCamDistance:
                self.maxCamDistance = self.maxCamDistance - 0.5
            self.acceptOnce("+", self.zoom, [True])
        else:
            if self.maxCamDistance < 15: # 15 is the default maximum
                self.maxCamDistance = self.maxCamDistance + 0.5
            self.acceptOnce("-", self.zoom, [False])

    def __normalCam(self):
        """This function will check the min and max distance of the camera to
        the defined model and will correct the position if the cam is to close
        or to far away"""

        # Camera Movement Updates
        camvec = self.player.getPos() - camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()

        # If far from player start following
        if camdist > self.maxCamDistance:
            camera.setPos(camera.getPos() + camvec*(camdist-self.maxCamDistance))
            camdist = self.maxCamDistance

        # If player to close move cam backwards
        if camdist < self.minCamDistance:
            camera.setPos(camera.getPos() - camvec*(self.minCamDistance-camdist))
            camdist = self.minCamDistance

        # get the cameras current offset to the player model on the z-axis
        offsetZ = camera.getZ() - self.player.getZ()
        # check if the camera is within the min and max z-axis offset
        if offsetZ < self.minCamHeightDist:
            camera.setZ(self.player.getZ() + self.minCamHeightDist)
            offsetZ = self.minCamHeightDist
        elif offsetZ > self.maxCamHeightDist:
            camera.setZ(self.player.getZ() + self.maxCamHeightDist)
            offsetZ = self.maxCamHeightDist

        if offsetZ != self.camHeightAvg:
            # if we are not moving up or down, set the cam to an average position
            if offsetZ != self.camHeightAvg:
                if offsetZ > self.camHeightAvg:
                    # the cam is higher then the average cam height above the player
                    # so move it slowly down
                    camera.setZ(camera.getZ() - 5 * globalClock.getDt())
                    newOffsetZ = camera.getZ() - self.player.getZ()
                    # check if the cam has reached the desired offset
                    if newOffsetZ < self.camHeightAvg:
                        # set the cam z position to exactly the desired offset
                        camera.setZ(self.player.getZ() + self.camHeightAvg)
                else:
                    # the cam is lower then the average cam height above the player
                    # so move it slowly up
                    camera.setZ(camera.getZ() + 5 * globalClock.getDt())
                    newOffsetZ = camera.getZ() - self.player.getZ()
                    # check if the cam has reached the desired offset
                    if newOffsetZ > self.camHeightAvg:
                        # set the cam z position to exactly the desired offset
                        camera.setZ(self.player.getZ() + self.camHeightAvg)

        if self.keyMap["center"]:
            camera.setPos(self.player, 0, camdist, offsetZ)

        self.camFloater.setPos(self.player.getPos())
        self.camFloater.setX(self.player.getX() + self.lookatOffset.getX())
        self.camFloater.setY(self.player.getY() + self.lookatOffset.getY())
        self.camFloater.setZ(self.player.getZ() + self.lookatOffset.getZ())
        camera.lookAt(self.camFloater)#self.player)

    def __fightCam(self):
        """This function will check the min and max distance of the camera to
        the defined model and will correct the position if the cam is to close
        or to far away"""
        camera.setX(self.player, 0)
        camera.setY(self.player, self.fightCamDistance)
        camera.setZ(0.5)

        self.camFloater.setPos(self.enemy.getPos())
        self.camFloater.setX(self.enemy.getX() + self.lookatOffset.getX())
        self.camFloater.setY(self.enemy.getY() + self.lookatOffset.getY())
        self.camFloater.setZ(self.enemy.getZ() + self.lookatOffset.getZ())

        camera.lookAt(self.camFloater)

    def enterIdle(self):
        self.player.loop("Idle")

    def enterRun(self):
        self.player.setPlayRate(3, "Run")
        self.player.loop("Run")

    def enterRunReverse(self):
        self.player.setPlayRate(-3, "Run")
        self.player.loop("Run")

    def enterActivate(self):
        self.player.setPlayRate(2, "Activate")
        self.player.play("Activate")
        base.messenger.send("Player_Activate")
        self.acceptOnce("enter", self.request, ["Activate"])
        self.acceptOnce("e", self.request, ["Activate"])

    def enterDeath(self):
        self.player.play("Death")

    def enterJump(self):
        self.player.play("Jump")

    def enterHit(self):
        self.player.play("Hit")

    def enterFightAttack(self):
        self.player.play("Fight_Attack")

    def enterFightIdle(self):
        self.player.loop("Fight_Idle")

    def enterFightLeft(self):
        self.player.loop("Fight_Left")

    def enterFightRight(self):
        self.player.loop("Fight_Right")
