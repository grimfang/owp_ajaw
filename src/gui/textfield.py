#!/usr/bin/python
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import logging

from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DGG
from direct.gui.DirectGui import DirectFrame
from panda3d.core import TextNode


class MessageWriter(DirectObject):
    def __init__(self):
        # the tasktime the last sign in the textfield was written
        self.lastSign = 0.0
        # the sign that is actually written in the textfield
        self.currentSign = 0
        # the text to write in the textfield
        self.textfieldText = ""
        # stop will be used to check if the writing is finished or
        # somehow else stoped
        self.stop = False
        # the speed new letters are added to the text
        self.writespeed = 0.05
        # the time, how long the text is shown after it is fully written
        self.showlength = 4

        # the textfield to put instructions hints and everything else, that
        # should be slowly written on screen and disappear after a short while
        self.textfield = TextNode('textfield')
        self.textfield.clearText()
        self.textfield.setShadow(0.005, 0.005)
        self.textfield.setShadowColor(0, 0, 0, 1)
        self.textfield.setWordwrap(base.a2dRight*2-0.4)
        self.textfield.setCardActual(
            -0.1, base.a2dRight*2-0.3,
            0.1, base.a2dBottom+0.5)
        self.textfield.setCardColor(0,0,0,0.45)
        self.textfield.setFlattenFlags(TextNode.FF_none)
        self.textfield.setTextScale(0.06)
        self.textfieldNodePath = aspect2d.attachNewNode(self.textfield)
        self.textfieldNodePath.setScale(1)
        self.textfieldNodePath.setPos(base.a2dLeft+0.2, 0, -0.4)

        self.hide()

    def show(self):
        self.textfieldNodePath.show()

    def hide(self):
        self.textfield.clearText()
        self.textfieldNodePath.hide()

    def clear(self):
        """Clear the textfield and stop the current written text"""
        self.hide()
        taskMgr.remove("writeText")
        self.stop = False
        self.writeDone = False
        self.currentSign = 0
        self.lastSign = 0.0
        self.textfield.clearText()

    def cleanup(self):
        """Function that should be called to remove and reset the
        message writer"""
        self.clear()
        self.ignore("showMessage")

    def run(self):
        """This function can be called to start the writer task."""
        self.textfield.setFlattenFlags(TextNode.FF_none)
        taskMgr.add(self.__writeText, "writeText", priority=30)

    def setMessageAndShow(self, message):
        """Function to simply add a new message and show it if no other
        message is currently shown"""
        logging.debug("show message %s" % message)
        self.textfieldText = message
        self.show()
        # start the writer task
        self.run()

    def __writeText(self, task):
        elapsed = globalClock.getDt()
        if(self.stop):
            # text is finished and can be cleared now
            self.clear()
            return task.done

        if self.currentSign == len(self.textfieldText)-1:
            self.textfield.setFlattenFlags(TextNode.FF_dynamic_merge)

        if self.currentSign >= len(self.textfieldText):
            # check if the text is fully written
            if task.time - self.lastSign >= self.showlength:
                # now also check if the time the text should
                # be visible on screen has elapsed
                self.stop = True
                self.textfieldNodePath.flattenStrong()
        elif (task.time - self.lastSign > self.writespeed) and (not self.stop):
            # write the next letter of the text
            self.textfield.appendText(self.textfieldText[self.currentSign])
            self.currentSign += 1
            self.lastSign = task.time

        return task.cont
