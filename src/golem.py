import random
from direct.actor.Actor import Actor
from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from panda3d.core import (
    CollisionNode,
    CollisionHandlerQueue,
    CollisionSphere,
    NodePath,
    PandaNode,
    CollisionSegment)
from direct.interval.IntervalGlobal import (
    Parallel,
    Sequence)
from direct.interval.FunctionInterval import (
    Wait,
    Func)

class Golem(FSM, DirectObject):
    def __init__(self):
        FSM.__init__(self, "FSM-Golem")
        random.seed()
        self.golem = loader.loadModel("Golem")
        self.golem = Actor("Golem", {
            "Idle":"Golem-Idle",
            "Walk":"Golem-Walk",
            "Attack":"Golem-Attack",
            "Destroyed":"Golem-Destroyed"})
        self.golem.setBlend(frameBlend = True)
        golemViewSphere = CollisionSphere(0, 0, 0.5, 6)
        golemViewSphere.setTangible(False)
        golemViewColNP = self.golem.attachNewNode(CollisionNode('golemViewField'))
        golemViewColNP.node().addSolid(golemViewSphere)
        golemHitSphere = CollisionSphere(0, 0, 0.5, 1)
        golemHitColNP = self.golem.attachNewNode(CollisionNode('golemHitField'))
        golemHitColNP.node().addSolid(golemHitSphere)

        # a collision segment to check attacks
        self.attackCheckSegment = CollisionSegment(0, 0, 1, 0, -1.3, 1)
        self.golemAttackRay = self.golem.attachNewNode(CollisionNode("golemAttackCollision"))
        self.golemAttackRay.node().addSolid(self.attackCheckSegment)
        self.golemAttackRay.node().setIntoCollideMask(0)
        self.attackqueue = CollisionHandlerQueue()
        base.cTrav.addCollider(self.golemAttackRay, self.attackqueue)

        attackAnim = self.golem.actorInterval("Attack", playRate = 2)
        self.AttackSeq = Parallel(
            attackAnim,
            Sequence(
                Wait(0.5),
                Func(self.ceckAttack)
            ))

        self.lookatFloater = NodePath(PandaNode("golemTracker"))
        self.lookatFloater.setPos(self.golem, 0, 0, 3.4)
        self.lookatFloater.hide()
        self.lookatFloater.reparentTo(render)
        self.trackerObject = loader.loadModel("misc/Pointlight")
        self.trackerObject.setColor(0, 1, 0)
        self.trackerObject.setScale(0.25)
        self.trackerObject.reparentTo(self.lookatFloater)

    def start(self, startPos):
        self.golem.setPos(startPos.getPos())
        self.golem.setHpr(startPos.getHpr())
        self.golem.reparentTo(render)
        self.trackedEnemy = None
        self.health = 5
        self.accept("playerCollision-in-golemViewField",
                    lambda extraArgs: base.messenger.send("golemSeesPlayer", [self.golem]))

    def stop(self):
        self.trackedEnemy = None
        taskMgr.remove("GolemAI_task")
        self.golem.hide()
        self.ignoreAll()

    def cleanup(self):
        self.stop()
        self.lookatFloater.removeNode()
        self.golem.cleanup()
        self.golem.removeNode()

    def activate(self, trackedEnemy):
        self.trackedEnemy = trackedEnemy
        taskMgr.add(self.aiTask, "GolemAI_task")
        self.lookatFloater.show()

    def aiTask(self, task):
        dt = globalClock.getDt()
        if self.AttackSeq.isPlaying(): return task.cont

        self.lookatFloater.setPos(self.golem, 0, 0, 3.4)
        self.lookatFloater.lookAt(self.trackedEnemy)
        self.lookatFloater.setH(self.lookatFloater.getH() + 180)
        self.lookatFloater.setP(0)
        self.lookatFloater.setR(0)

        self.golem.lookAt(self.trackedEnemy)
        self.golem.setH(self.golem.getH() + 180)

        distanceVec = self.golem.getPos() - self.trackedEnemy.getPos()
        enemyDist = distanceVec.length()

        if enemyDist < 2.0:
            # close enough for combat
            action = random.choice(["Attack", "Idle"])
            if action == "Attack":
                self.request("Attack")
            else:
                if self.state != "Idle":
                    self.request("Idle")
        else:
            self.golem.setY(self.golem, -0.5 * dt)
            if self.state != "Walk":
                self.request("Walk")

        return task.cont

    def hit(self):
        hitInterval = Sequence(
            Func(self.golem.setColorScale, 1, 0, 0, 0.75),
            Wait(0.15),
            Func(self.golem.clearColorScale),
            Wait(0.15),
            Func(self.golem.setColorScale, 1, 0, 0, 0.75),
            Wait(0.15),
            Func(self.golem.clearColorScale),
            Wait(0.15),
            Func(self.golem.setColorScale, 1, 0, 0, 0.75),
            Wait(0.15),
            Func(self.golem.clearColorScale),
            Wait(0.15),
            Func(self.golem.setColorScale, 1, 0, 0, 0.75),
            Wait(0.15),
            Func(self.golem.clearColorScale),
            Wait(0.15))
        self.health -= 1
        if self.health == 4:
            self.trackerObject.setColor(0, 1, 0)
            hitInterval.start()
        elif self.health == 3:
            self.trackerObject.setColor(0.25, 0.75, 0)
            hitInterval.start()
        elif self.health == 2:
            self.trackerObject.setColor(0.5, .5, 0)
            hitInterval.start()
        elif self.health == 1:
            self.trackerObject.setColor(0.75, 0.25, 0)
            hitInterval.start()
        elif self.health == 0:
            self.trackerObject.setColor(0, 0, 0)
            self.request("Destroyed")

    def ceckAttack(self):
        for i in range(self.attackqueue.getNumEntries()):
            entry = self.attackqueue.getEntry(i)
            into = entry.getIntoNode()
            if "playerCollision" in into.getName():
                if random.random() > .5:
                    base.messenger.send("HitPlayer")

    def enterIdle(self):
        self.golem.loop("Idle")

    def enterWalk(self):
        self.golem.setPlayRate(2, "Walk")
        self.golem.loop("Walk")

    def enterAttack(self):
        self.AttackSeq.start()

    def enterDestroyed(self):
        self.ignoreAll()
        taskMgr.remove("GolemAI_task")
        self.AttackSeq.finish()
        self.golem.play("Destroyed")
        self.lookatFloater.hide()
        base.messenger.send("GolemDestroyed")
