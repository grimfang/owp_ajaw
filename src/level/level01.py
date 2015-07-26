#!/usr/bin/env python

import random
from panda3d.core import (
    AmbientLight,
    Spotlight,
    PointLight,
    PerspectiveLens,
    Filename,
    CollideMask,
    CollisionSphere,
    CollisionBox,
    CollisionPlane,
    CollisionNode,
    BillboardEffect,
    CardMaker,
    TextureStage,
    TransparencyAttrib,
    Plane,
    Vec3,
    Point3)
from direct.interval.IntervalGlobal import (
    Parallel,
    Sequence)
from direct.interval.FunctionInterval import (
    Func,
    Wait)
from direct.interval.AnimControlInterval import AnimControlInterval
from direct.showbase.DirectObject import DirectObject
from direct.particles.ParticleEffect import ParticleEffect

class Level01(DirectObject):
    def __init__(self):
        # Level model
        self.level = loader.loadModel("Level")
        self.key = loader.loadModel("Key")
        self.artifact = loader.loadModel("Artifact")

        """Logic connections INFO

        Switch.000 opens door Wooden_Door_Basic

        Switch.001-4 in correct order open Boulder_Door

        Key opens Boulder_Door.001

        Switch.005 opens Boulder_Door.002

        Defeating Golem opens Wooden_Door_Basic.001
        """

        random.seed()

        self.switchLogic = {
            "Switch.000":"Wooden_Door_Basic",
            "Switch.001":"ORDER1",
            "Switch.002":"ORDER1",
            "Switch.003":"ORDER1",
            "Switch.004":"ORDER1",
            "ORDER1":"Boulder_Door",
            "Switch.005":"Boulder_Door.002"}
        self.switchOrderLogic = {}
        self.switchOrders = [
            ["First the highest, the second comes third and the lowest before the last.",[2,3,4,1]],
            ["The second lowest is the first then lower highest higher.",[2,1,4,3]],
            ["Before the last comes the second lowest, the first is the second highest followed by the lowest.",[2,3,1,4]]]
        self.enemyLogic = {"Golem":"Wooden_Door_Basic.001"}
        self.KeyDoorLogic = ["Boulder_Door.001"]
        self.chestLogic = {
            "Box_long_looseLid.000":"GET_Key",
            "Box_long_looseLid.001":"GET_Artifact"}
        self.activeSwitch = None
        self.activePostsign = None
        self.activeBox = None
        self.activeDoor = None

        self.numKeys = 0

        # Set up all the little details
        if base.particleMgrEnabled:
            self.initTorchParticles()
        self.initSwitches()
        self.initSwitchSigns()
        self.initPostsigns()
        self.initDoors()
        self.initKeyDoors()
        self.initChests()
        self.initHearts()

        plane = self.level.find("**/Deathplane")
        deathplane = CollisionPlane(Plane((0, 0, 1), (0,0,-1)))
        deathplane.setTangible(False)
        self.deathplaneColNP = render.attachNewNode(CollisionNode('deathplane'))
        self.deathplaneColNP.node().addSolid(deathplane)
        self.accept("playerCollision-in-deathplane", lambda args: base.messenger.send("player-die"))

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

        self.switchControls = {}

        i = 0
        for object in objects:
            bundle = object.node().getBundle(0)
            control = bundle.bindAnim(switchAnim, ~0)

            switchsphere = CollisionSphere(0, 0, 0, 0.5)
            switchsphere.setTangible(False)
            switchColNP = object.getParent().attachNewNode(CollisionNode('switchActivation%d'%i))
            switchColNP.node().addSolid(switchsphere)
            self.switchControls.setdefault(object.getParent(), [control, switchColNP])
            switchName = object.getParent().getParent().getName()
            self.accept("playerCollision-in-switchActivation%d"%i,
                        self.__setActivateElement,
                        extraArgs=[True, switchName, "switch"])
            self.accept("playerCollision-out-switchActivation%d"%i,
                        self.__setActivateElement,
                        extraArgs=[False, switchName, "switch"])
            i+=1

        for key, value in self.switchControls.iteritems():
            value[0].pose(0)

    def initSwitchSigns(self):
        self.switchSigns = []
        for i in range(11):
            cm = CardMaker('card%d'%i)
            cm.setColor(0,0,0,0)
            cm.setFrame(-0.5, 0.5, -0.5, 0.5)
            card = self.level.attachNewNode(cm.generate())
            card.setAttrib(TransparencyAttrib.make(TransparencyAttrib.M_alpha))
            tex = loader.loadTexture('%d.png'%i)
            ts = TextureStage('ts')
            ts.setMode(TextureStage.MReplace)
            card.setTexture(ts, tex)
            card.setEffect(BillboardEffect.makePointEye())
            card.hide()
            self.switchSigns.append(card)

    def initPostsigns(self):
        objects = self.level.findAllMatches('**/Signpost.*')

        self.postsigns = {}

        i = 0
        for object in objects:
            postsphere = CollisionSphere(0, 0, 0.5, 1)
            postsphere.setTangible(False)
            postColNP = object.attachNewNode(CollisionNode('postsignInfo%d'%i))
            postColNP.node().addSolid(postsphere)
            self.postsigns.setdefault(object, postColNP)
            postName = object.getName()
            self.accept("playerCollision-in-postsignInfo%d"%i,
                        self.__setActivateElement,
                        extraArgs=[True, postName, "postsign"])
            self.accept("playerCollision-out-postsignInfo%d"%i,
                        self.__setActivateElement,
                        extraArgs=[False, postName, "postsign"])
            i+=1

    def initChests(self):
        objects = self.level.findAllMatches('**/Box_long_looseLid')

        boxAnimNode = loader.loadModel("Box_long_looseLid-open.egg")
        boxAnim = boxAnimNode.find("+AnimBundleNode").node().getBundle()

        self.boxControls = {}

        i = 0
        for object in objects:
            bundle = object.node().getBundle(0)
            control = bundle.bindAnim(boxAnim, ~0)

            boxsphere = CollisionSphere(0, 0, 0, 1.0)
            boxsphere.setTangible(False)
            boxColNP = object.getParent().attachNewNode(CollisionNode('boxActivation%d'%i))
            boxColNP.node().addSolid(boxsphere)
            #boxColNP.show()
            self.boxControls.setdefault(object.getParent(), [control, boxColNP])
            boxName = object.getParent().getParent().getName()
            self.accept("playerCollision-in-boxActivation%d"%i,
                        self.__setActivateElement,
                        extraArgs=[True, boxName, "box"])
            self.accept("playerCollision-out-boxActivation%d"%i,
                        self.__setActivateElement,
                        extraArgs=[False, boxName, "box"])
            i+=1

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
            if "Boulder" in object.getName():
                control = bundle.bindAnim(bdoorAnim, ~0)
                self.doorControls.setdefault(object.getParent(),[control])
            elif "Wood" in object.getName():
                control = bundle.bindAnim(wdoorAnim, ~0)
                self.doorControls.setdefault(object.getParent(),[control])

        for collider in colliders:
            if "Boulder_Door_door_collision" in collider.getName():
                self.doorControls[collider.getParent()].append(collider)
            elif "Wood" in collider.getName():
                self.doorControls[collider.getParent()].append(collider)

        for key, value in self.doorControls.iteritems():
            value[0].pose(0)

    def initKeyDoors(self):
        i = 0
        for keyDoor in self.KeyDoorLogic:
            for door, value in self.doorControls.iteritems():
                if keyDoor == door.getParent().getName():
                    c = Point3(0,0,0)
                    p1 = Point3(c.getX()-1, c.getY()-0.8, c.getZ())
                    p2 = Point3(c.getX()+1, c.getY()+0.8, c.getZ()+2)
                    keyDoorBox = CollisionBox(p1, p2)
                    keyDoorBox.setTangible(False)
                    keyDoorColNP = door.getParent().attachNewNode(CollisionNode('keyDoorActivation%d'%i))
                    keyDoorColNP.node().addSolid(keyDoorBox)
                    keyDoorName = door.getParent().getName()
                    self.accept("playerCollision-in-keyDoorActivation%d"%i,
                                self.__setActivateElement,
                                extraArgs=[True, keyDoorName, "door"])
                    self.accept("playerCollision-out-keyDoorActivation%d"%i,
                                self.__setActivateElement,
                                extraArgs=[False, keyDoorName, "door"])
                    i+=1

    def initHearts(self):
        heartPositions = self.level.findAllMatches('**/*Heart*')
        self.hearts = []
        i = 0
        for pos in heartPositions:
            heart = loader.loadModel("Heart")
            heart.reparentTo(pos)
            heartRotation = heart.hprInterval(2.0, Vec3(360, 0, 0))
            heartRotation.loop()
            heartsphere = CollisionSphere(0, 0, 0, 0.5)
            heartsphere.setTangible(False)
            heartColNP = heart.attachNewNode(CollisionNode('heart%d'%i))
            heartColNP.node().addSolid(heartsphere)
            self.accept("playerCollision-in-heart%d"%i,
                        self.__collectHeart,
                        extraArgs=[i])
            self.hearts.append(heart)
            i+=1

    def start(self):
        self.level.reparentTo(render)
        self.key.reparentTo(render)
        self.key.hide()
        self.artifact.reparentTo(render)
        self.artifact.hide()
        self.initLights()

        #
        # SETUP THE LOGIC PUZZLE IN ROOM 2
        #
        # get a random order
        self.order1 = random.choice(self.switchOrders)
        # set the switch order
        switchlist = []
        for item in self.order1[1]:
            switchlist.append("Switch.00%d"%item)
        self.switchOrderLogic.setdefault("ORDER1", switchlist)
        # randomly assign numbers between 0 and 10 to the switches
        signlist = []
        for i in range(4):
            inList = True
            while inList:
                num = random.randint(0, 10)
                if num not in signlist:
                    inList = False
                    signlist.append(num)
        # sort the signlist to map it to the final order
        sortedOrder = sorted(signlist)
        # map the sorted list to the order of the order1 list
        signlist[self.order1[1][0]-1] = sortedOrder[0]
        signlist[self.order1[1][1]-1] = sortedOrder[1]
        signlist[self.order1[1][2]-1] = sortedOrder[2]
        signlist[self.order1[1][3]-1] = sortedOrder[3]
        # add the new values to the order1 list
        self.order1.append(signlist)
        # Now we should have random numbers between 0 and 10 in the same order
        # as the order1 list needs
        # Finally add the signs above the switches
        for i in range(4):
            for switch, value in self.switchControls.iteritems():
                if self.switchOrderLogic.get("ORDER1")[i] in switch.getParent().getName():
                    pos = switch.getPos(render)
                    pos.setZ(pos.getZ() + 1.0)
                    self.switchSigns[signlist[i]].setPos(pos)
                    self.switchSigns[signlist[i]].show()

        #
        # SETUP THE SIGN TEXTS
        #
        self.signTexts = {
            "Signpost.000":"You who dare to undergo the test of kings, actiavate the lever to the left and enter.",
            "Signpost.001":"This room will test your mind. Your mind is important to make wise decissions for your people. To open the door you have to solve this riddle:\n\n\"%s\"\n\nThe signs above the levers will guide you." % self.order1[0],
            "Signpost.002":"The next door can only be opend with a key placed in this chamber.",
            "Signpost.003":"Be careful here, not to fall into the dangerous spikes. But go on without fear and you'll prove yourself to being able to guide your people throuh dangerous times.\n\nWith the heartstones you can see here you can refil your health.",
            "Signpost.004":"In the next chamber a ferocious enemy will await you defending the artifact. Defeate him and show that you'll be able to defend your people.\n\nTo attack use the action key.",
            "Signpost.005":"Finally you made it all the way through path of the kings. Open the chest, take the artefact and you'll be ready for becomming the next king."}

    def stop(self):
        self.level.removeNode()

    def getPlayerStartPoint(self):
        return self.level.find("**/Character")

    def getGolemStartPoint(self):
        return self.level.find("**/Golem")

    def activateElement(self):
        if self.activeSwitch is not None: self.__activateSwitch()
        if self.activePostsign is not None: self.__activatePost()
        if self.activeBox is not None: self.__activateChest()
        if self.activeDoor is not None: self.__activateKeyDoor()

    def __activateSwitch(self):
        if not self.activeSwitch in self.switchLogic.keys(): return
        for key, value in self.switchControls.iteritems():
            if self.activeSwitch == key.getParent().getName():
                if value[0].getFrame() != 0: return
                value[0].play()
        if "ORDER" in self.switchLogic[self.activeSwitch]:
            order = self.switchOrderLogic[self.switchLogic[self.activeSwitch]]
            #NOTE: order is set up as follow:
            #["Display text", "sort order (1 based integer list)", "additional content..."]
            orderCorrect = True
            orderDone = True
            for switchname in self.switchOrderLogic[self.switchLogic[self.activeSwitch]]:
                if switchname == self.activeSwitch: break
                # check if earlier switches have been activated already
                for key, value in self.switchControls.iteritems():
                    if switchname == key.getParent().getName():
                        if value[0].getFrame() == 0: orderCorrect = False
                        break
                if orderCorrect == False:
                    break
            # check if all switches have successfully been activated
            for switchname in self.switchOrderLogic[self.switchLogic[self.activeSwitch]]:
                for key, value in self.switchControls.iteritems():
                    if switchname == self.activeSwitch: continue
                    if switchname == key.getParent().getName():
                        if value[0].getFrame() == 0:
                            orderDone = False
                            break
                if not orderDone:
                    break
            if not orderCorrect:
                # reset all switches in the logic puzzle
                for switchname in self.switchOrderLogic[self.switchLogic[self.activeSwitch]]:
                    for key, value in self.switchControls.iteritems():
                        if switchname == key.getParent().getName():
                            value[0].pose(0)
            if orderDone:
                self.__openDoor(self.switchLogic[self.switchLogic[self.activeSwitch]])
        else:
            self.__openDoor(self.switchLogic[self.activeSwitch])

    def __activatePost(self):
        base.messenger.send("showMessage", [self.signTexts[self.activePostsign]])

    def __activateChest(self):
        for box, value in self.boxControls.iteritems():
            if self.activeBox == box.getParent().getName():
                if value[0].getFrame() != 0: return
                if self.chestLogic[self.activeBox] == "GET_Key":
                    self.key.show()
                    self.key.setPos(box.getParent().getPos())
                    self.key.setZ(self.key.getZ() + 0.5)
                    self.key.setHpr(box.getParent().getHpr())
                    self.key.setH(self.key.getH() + 90.0)
                    keyRisingInterval = self.key.posInterval(1.5, Point3(self.key.getX(), self.key.getY(), self.key.getZ() + 1.0))
                    keyRotationInterval = self.key.hprInterval(3.0, Vec3(self.key.getH() + 360*2, 0, 0))
                    keyAnimation = Parallel(keyRisingInterval, keyRotationInterval, name="keyAnimation")
                    boxAnimation = AnimControlInterval(value[0])
                    chestFullAnimation = Sequence(
                        boxAnimation,
                        keyAnimation,
                        Wait(0.25),
                        Func(self.key.hide),
                        Func(self.addKey))
                elif self.chestLogic[self.activeBox] == "GET_Artifact":
                    self.artifact.show()
                    self.artifact.setPos(box.getParent().getPos())
                    self.artifact.setZ(self.artifact.getZ() + 0.5)
                    artifactRisingInterval = self.artifact.posInterval(
                        1.5,
                        Point3(self.artifact.getX(), self.artifact.getY(), self.artifact.getZ() + 1.0))
                    artifactRotationInterval = self.artifact.hprInterval(
                        3.0,
                        Vec3(self.artifact.getH() + 360*2, 0, 0))
                    artifactAnimation = Parallel(
                        artifactRisingInterval,
                        artifactRotationInterval,
                        name="artifactAnimation")
                    boxAnimation = AnimControlInterval(value[0])
                    chestFullAnimation = Sequence(
                        boxAnimation,
                        artifactAnimation,
                        Wait(0.25),
                        Func(self.artifact.hide),
                        Func(self.getArtifact))
                chestFullAnimation.start()

    def __activateKeyDoor(self):
        if self.numKeys > 0:
            self.__openDoor(self.activeDoor)
            self.numKeys -= 1
        base.messenger.send("updateKeyCount", [self.numKeys])

    def __collectHeart(self, index, extraArgs):
        heart = self.hearts[index]
        heart.removeNode()
        base.messenger.send("player-heal")

    def addKey(self):
        self.numKeys += 1
        base.messenger.send("updateKeyCount", [self.numKeys])

    def getArtifact(self):
        base.messenger.send("GameOver", ["win"])

    def __setActivateElement(self, active, element, elementType, CollEntry):
        if active:
            base.messenger.send("ActionActive")
        else:
            base.messenger.send("ActionDeactive")
        if elementType == "switch":
            if active:
                self.activeSwitch = element
            else:
                self.activeSwitch = None
        elif elementType == "postsign":
            if active:
                self.activePostsign = element
            else:
                self.activePostsign = None
        elif elementType == "box":
            if active:
                self.activeBox = element
            else:
                self.activeBox = None
        elif elementType == "door":
            if active:
                self.activeDoor = element
            else:
                self.activeDoor = None

    def defeatEnemy(self, enemy):
        for key, value in self.enemyLogic.iteritems():
            if key == enemy:
                self.__openDoor(value)

    def __openDoor(self, door):
        for key, value in self.doorControls.iteritems():
            if door == key.getParent().getName():
                base.messenger.send("PuzzleSolved")
                value[0].play()
                value[1].node().setIntoCollideMask(CollideMask.allOff())
