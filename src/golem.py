import random
from direct.actor.Actor import Actor
from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from panda3d.core import (
    CollisionNode,
    CollisionSphere)

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
        self.trackedEnemy = None
        self.health = 5
        golemViewSphere = CollisionSphere(0, 0, 0.5, 6)
        golemViewSphere.setTangible(False)
        golemViewColNP = self.golem.attachNewNode(CollisionNode('golemViewField'))
        golemViewColNP.node().addSolid(golemViewSphere)
        self.accept("playerCollision-in-golemViewField",
                    lambda extraArgs: base.messenger.send("golemSeesPlayer", [self.golem]))
        golemHitSphere = CollisionSphere(0, 0, 0.5, 1)
        golemHitColNP = self.golem.attachNewNode(CollisionNode('golemHitField'))
        golemHitColNP.node().addSolid(golemHitSphere)
        golemHitColNP.show()

    def start(self, startPos):
        self.golem.setPos(startPos.getPos())
        self.golem.setHpr(startPos.getHpr())
        self.golem.reparentTo(render)

    def stop(self):
        self.golem.removeNode()

    def activate(self, trackedEnemy):
        self.trackedEnemy = trackedEnemy
        taskMgr.add(self.aiTask, "GolemAI_task")

    def aiTask(self, task):
        self.golem.lookAt(self.trackedEnemy)
        self.golem.setH(self.golem.getH() + 180)
        # TODO:
        # 1. Move toward tracked enemy
        # 2. if close enough start atack
        # 3. if not attack enter idle
        return task.cont

    def hit(self):
        self.health -= 1
        if self.health == 0:
            self.request("Destroyed")

    def enterIdle(self):
        self.golem.loop("Idle")

    def enterWalk(self):
        self.golem.loop("Walk")

    def enterAttack(self):
        self.golem.play("Attack")

    def enterDestroyed(self):
        taskMgr.remove("GolemAI_task")
        self.golem.play("Destroyed")
        base.messenger.send("GolemDestroyed")
        print "GOLEM DESTROYED"
