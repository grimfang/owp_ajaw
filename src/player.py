import random
from direct.actor.Actor import Actor
from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from direct.interval.ProjectileInterval import ProjectileInterval
from panda3d.core import (
    Vec3,
    Point3,
    NodePath,
    PandaNode,
    CollisionSphere,
    CollisionRay,
    CollisionSegment,
    CollisionNode,
    CollisionHandlerFloor,
    CollisionHandlerEvent,
    CollisionHandlerQueue,
    PointLight)
from direct.interval.IntervalGlobal import Sequence
from direct.interval.FunctionInterval import (
    Wait,
    Func)

class Player(FSM, DirectObject):
    NormalMode = "Normal"
    FightMode = "Fight"

    def __init__(self):
        FSM.__init__(self, "FSM-Player")
        random.seed()

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
        # this variable will set an offset to the node the cam is attached to
        # and the point the camera looks at. By default the camera will look
        # directly at the node it is attached to
        self.lookatOffset = Vec3(0, 0, 1.5)
        # the initial cam distance
        self.fightCamDistance = 3.0
        # the next two vars will set the min and max distance the cam can have
        # to the node it is attached to
        self.maxCamDistance = 4.0
        self.minCamDistance = 0.8
        # the initial cam distance
        self.camDistance = (self.maxCamDistance - self.minCamDistance) / 2.0 + self.minCamDistance
        # the next two vars set the min and max distance on the Z-Axis to the
        # node the cam is attached to
        self.maxCamHeightDist = 3.0
        self.minCamHeightDist = 1.5
        # the average camera height
        self.camHeightAvg = (self.maxCamHeightDist - self.minCamHeightDist) / 2.0 + self.minCamHeightDist
        # an invisible object which will fly above the player and will be used to
        # track the camera on it
        self.camFloater = NodePath(PandaNode("playerCamFloater"))
        self.camFloater.reparentTo(render)
        # Interval for the jump animation
        self.jumpInterval = None
        self.jumpstartFloater = NodePath(PandaNode("jumpstartFloater"))
        self.jumpstartFloater.reparentTo(render)
        self.deathComplete = None

        #
        # WEAPONS AND ACCESSORIES
        #
        self.RightHandAttach = self.player.exposeJoint(None, "modelRoot", "HandAttach_R")
        self.spear = loader.loadModel("Spear")
        self.spear.setP(90)
        self.spear.setR(180)
        self.spear.reparentTo(self.RightHandAttach)
        self.LeftHandAttach = self.player.exposeJoint(None, "modelRoot", "HandAttach_L")
        self.shield = loader.loadModel("Shield")
        self.shield.setZ(0.05)
        self.shield.setH(-90)
        self.shield.reparentTo(self.LeftHandAttach)

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
        self.lifter = CollisionHandlerFloor()
        self.lifter.addCollider(self.playerFootRay, self.player)
        self.lifter.setMaxVelocity(5)
        base.cTrav.addCollider(self.playerFootRay, self.lifter)
        # a collision segment slightly in front of the player to check for jump ledges
        self.jumpCheckSegment = CollisionSegment(0, -0.2, 0.5, 0, -0.2, -2)
        self.playerJumpRay = self.player.attachNewNode(CollisionNode("playerJumpCollision"))
        self.playerJumpRay.node().addSolid(self.jumpCheckSegment)
        self.playerJumpRay.node().setIntoCollideMask(0)
        self.jumper = CollisionHandlerEvent()
        self.jumper.addOutPattern('%fn-out')
        base.cTrav.addCollider(self.playerJumpRay, self.jumper)
        # a collision segment to check attacks
        self.attackCheckSegment = CollisionSegment(0, 0, 1, 0, -1.3, 1)
        self.playerAttackRay = self.player.attachNewNode(CollisionNode("playerAttackCollision"))
        self.playerAttackRay.node().addSolid(self.attackCheckSegment)
        self.playerAttackRay.node().setIntoCollideMask(0)
        self.attackqueue = CollisionHandlerQueue()
        base.cTrav.addCollider(self.playerAttackRay, self.attackqueue)

        #
        # SOUNDEFFECTS
        #
        self.footstep = loader.loadSfx("Footstep.ogg")
        self.footstep.setLoop(True)
        self.footstep.setPlayRate(1.5)
        self.footstep.setVolume(0.5)
        self.spearAttackSfx = loader.loadSfx("SpearAttack.ogg")
        self.spearAttackSfx.setVolume(0.5)

    #
    # START/STOP
    #
    def start(self, startPoint):
        self.player.setPos(startPoint.getPos())
        self.player.setHpr(startPoint.getHpr())
        self.player.reparentTo(render)
        self.jumpstartFloater.setPos(self.player.getPos())

        self.keyMap = {"left":0, "right":0, "forward":0, "backward":0, "center":0}

        self.health = 3
        self.trackedEnemy = None
        # this mode will be used to determine in which move mode the player currently is
        self.mode = Player.NormalMode
        # the initial cam height
        self.camHeight = self.camHeightAvg
        # a time to keep the cam zoom at a specific speed independent of
        # current framerate
        self.camElapsed = 0.0

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
        self.acceptOnce("enter", self.request, ["Action"])
        self.acceptOnce("e", self.request, ["Action"])
        self.accept("ActionDone", self.request, ["Idle"])

        self.accept("playerJumpCollision-out", self.jump)

        taskMgr.add(self.move, "task_movement", priority=-10)
        taskMgr.add(self.updateCam, "task_camActualisation", priority=-4)

        camera.setPos(self.player, 0, self.camDistance, self.camHeightAvg)

        self.hasJumped = False
        self.isActionmove = False

        self.request("Idle")

    def stop(self):
        taskMgr.remove("task_movement")
        taskMgr.remove("task_camActualisation")
        self.ignoreAll()
        self.player.hide()

    def cleanup(self):
        self.stop()
        if self.deathComplete is not None:
            self.deathComplete.finish()
        if self.jumpInterval is not None:
            self.jumpInterval.finish()
        self.spear.removeNode()
        self.shield.removeNode()
        self.player.cleanup()
        self.player.removeNode()
        self.jumpstartFloater.removeNode()
        self.camFloater.removeNode()

    #
    # BASIC FUNCTIONS
    #
    def die(self):
        self.health -= 1
        base.messenger.send("setHealth", [self.health])
        self.request("Death")

    def heal(self):
        if self.health >= 3: return
        self.health += 1
        base.messenger.send("setHealth", [self.health])

    def hit(self):
        self.health -= 1
        base.messenger.send("setHealth", [self.health])
        if self.health == 0:
            self.request("Death")
        else:
            self.request("Hit")

    def resetPlayerPos(self):
        self.player.setPos(self.jumpstartFloater.getPos())
        self.jumper.clear()
        self.request("Idle")

    def gameOver(self):
        base.messenger.send("GameOver", ["loose"])

    def enterFightMode(self, trackedEnemy):
        self.trackedEnemy = trackedEnemy
        self.mode = Player.FightMode
        base.messenger.send("EnterFightMode")

    def exitFightMode(self):
        self.trackedEnemy = None
        self.mode = Player.NormalMode
        base.messenger.send("ExitFightMode")

    #
    # MOVE FUNCTIONS
    #
    def setKey(self, key, value):
        self.keyMap[key] = value

    def move(self, task):
        dt = globalClock.getDt()
        if self.player.getAnimControl("Hit").isPlaying() or \
            self.player.getAnimControl("Death").isPlaying():
            return task.cont
        if self.deathComplete is not None:
            if self.deathComplete.isPlaying():
                return task.cont
        if self.jumpInterval is not None:
            if self.jumpInterval.isPlaying():
                return task.cont
        if self.isActionmove:
            return task.cont
        if self.mode == Player.NormalMode:
            self.__normalMove(dt)
        else:
            self.__fightMove(dt)
        return task.cont

    def __normalMove(self, dt):
        requestState = "Idle"
        if self.keyMap["left"] != 0:
            self.player.setH(self.player.getH() + 150 * dt)
            requestState = "Run"
        if self.keyMap["right"] != 0:
            self.player.setH(self.player.getH() - 150 * dt)
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
        requestState = "Idle"
        self.player.lookAt(self.trackedEnemy)
        self.player.setH(self.player, 180)
        if self.keyMap["left"] != 0:
            self.player.setX(self.player, 2 * dt)
            requestState = "FightLeft"
        elif self.keyMap["right"] != 0:
            self.player.setX(self.player, -2 * dt)
            requestState = "FightRight"
        elif self.keyMap["forward"] != 0:
            self.player.setY(self.player, -2 * dt)
            requestState = "Run"
        elif self.keyMap["backward"] != 0:
            self.player.setY(self.player, 2 * dt)
            requestState = "RunReverse"
        if self.state != requestState:
            self.request(requestState)

    def jump(self, extraArg):
        intoName = extraArg.getIntoNode().getName().lower()
        if not "floor" in intoName and not "plate" in intoName: return
        # setup the projectile interval
        startPos = self.player.getPos()
        self.jumpstartFloater.setPos(self.player, 0, 0.5, 0)
        tempFloater = NodePath(PandaNode("tempJumpFloater"))
        tempFloater.setPos(self.player, 0, -3.2, 0.1)
        endPos = tempFloater.getPos()
        tempFloater.removeNode()
        self.jumpInterval = ProjectileInterval(
            self.player,
            startPos = startPos,
            endPos = endPos,
            duration = 1.5,
            gravityMult = 0.25)
        self.request("Jump")
        self.jumpInterval.start()

    #
    # CAMERA FUNCTIONS
    #
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

        self.camFloater.setPos(self.trackedEnemy.getPos())
        self.camFloater.setX(self.trackedEnemy.getX() + self.lookatOffset.getX())
        self.camFloater.setY(self.trackedEnemy.getY() + self.lookatOffset.getY())
        self.camFloater.setZ(self.trackedEnemy.getZ() + self.lookatOffset.getZ())

        camera.lookAt(self.camFloater)

    #
    # FSM FUNCTIONS
    #
    def enterIdle(self):
        if self.mode == Player.NormalMode:
            self.player.loop("Idle")
            self.footstep.stop()
        elif self.mode == Player.FightMode:
            self.player.loop("Fight_Idle")
            self.footstep.stop()

    def enterRun(self):
        self.player.setPlayRate(3, "Run")
        self.player.loop("Run")
        self.footstep.play()

    def enterRunReverse(self):
        self.player.setPlayRate(-3, "Run")
        self.player.loop("Run")
        self.footstep.play()

    def enterAction(self):
        if self.player.getAnimControl("Hit").isPlaying() or \
            self.player.getAnimControl("Death").isPlaying():
            self.__exitAction()
            return
        self.isActionmove = True
        if self.mode == Player.NormalMode:
            self.__enterActivate()
        elif self.mode == Player.FightMode:
            self.__enterFightAttack()
        self.accept("ActionDone", self.__exitAction)

    def __exitAction(self):
        self.isActionmove = False
        self.acceptOnce("enter", self.request, ["Action"])
        self.acceptOnce("e", self.request, ["Action"])

    def __enterActivate(self):
        self.player.setPlayRate(2, "Activate")
        activateAnim = self.player.actorInterval("Activate")
        activateAnim.setDoneEvent("ActionDone")
        activateAnim.start()
        base.messenger.send("Player_Activate")
        self.footstep.stop()

    def enterDeath(self):
        self.footstep.stop()
        deathAnim = self.player.actorInterval("Death")
        deathComplete = None
        if self.health == 0:
            self.deathComplete = Sequence(
                deathAnim,
                Wait(2),
                Func(self.gameOver))
        else:
            self.deathComplete = Sequence(
                deathAnim,
                Wait(2),
                Func(self.resetPlayerPos))
        self.deathComplete.start()

    def enterJump(self):
        self.player.play("Jump")
        self.footstep.stop()

    def enterHit(self):
        self.player.setPlayRate(4, "Hit")
        self.player.play("Hit")
        self.footstep.stop()

    def __enterFightAttack(self):
        self.player.setPlayRate(2, "Fight_Attack")
        #self.player.play("Fight_Attack")
        attackAnim = self.player.actorInterval("Fight_Attack")
        attackAnim.setDoneEvent("ActionDone")
        attackAnim.start()
        self.spearAttackSfx.play()
        for i in range(self.attackqueue.getNumEntries()):
            entry = self.attackqueue.getEntry(i)
            into = entry.getIntoNode()
            if "golemHitField" in into.getName():
                if random.random() > .15:
                    base.messenger.send("HitEnemy")
        self.footstep.stop()

    def enterFightLeft(self):
        self.player.setPlayRate(2, "Fight_Left")
        self.player.loop("Fight_Left")
        self.footstep.play()

    def enterFightRight(self):
        self.player.setPlayRate(2, "Fight_Right")
        self.player.loop("Fight_Right")
        self.footstep.play()
