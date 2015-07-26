from direct.gui.DirectGui import DirectFrame
from direct.gui.DirectGui import DirectLabel
from direct.gui.DirectGui import DirectButton
from panda3d.core import TextNode


class GameOverScreen():
    def __init__(self):
        # a fill panel so the player doesn't see how everything
        # gets loaded in the background
        self.frameMain = DirectFrame(
            # size of the frame
            frameSize = (base.a2dLeft, base.a2dRight,
                         base.a2dTop, base.a2dBottom),
            image = "Logo.png",
            image_scale = (0.612/2.0, 1, 0.495/2.0),
            image_pos = (0, 0, 0.7),
            # tramsparent bg color
            frameColor = (0, 0, 0, 1))
        self.frameMain.setTransparency(1)

        self.lblWin = DirectLabel(
            scale = 0.25,
            pos = (0, 0, 0.25),
            frameColor = (0, 0, 0, 0),
            text = "You Succeeded",
            text_align = TextNode.ACenter,
            text_fg = (1,1,1,1))
        self.lblWin.reparentTo(self.frameMain)

        self.lblTime = DirectLabel(
            scale = 0.07,
            pos = (0, 0, 0.00),
            frameColor = (0, 0, 0, 0),
            text = "your time",
            text_align = TextNode.ACenter,
            text_fg = (1,1,1,1))
        self.lblTime.reparentTo(self.frameMain)

        self.lblResult = DirectLabel(
            scale = 0.40,
            pos = (0, 0, -0.25),
            frameColor = (0, 0, 0, 0),
            text = "00:00",
            text_align = TextNode.ACenter,
            text_fg = (1,1,1,1))
        self.lblResult.reparentTo(self.frameMain)

        self.btnContinue = DirectButton(
            scale = (0.25, 0.25, 0.25),
            # some temp text
            text = "Continue...",
            text_scale = (0.5, 0.5, 0.5),
            # set the alignment to right
            text_align = TextNode.ACenter,
            # put the text on the right side of the button
            text_pos = (0, 0),
            # set the text color to black
            text_fg = (1,1,1,1),
            text_shadow = (0.3, 0.3, 0.1, 1),
            text_shadowOffset = (0.05, 0.05),
            relief = 1,
            frameColor = (0,0,0,0),
            pressEffect = False,
            pos = (0, 0, -0.65),
            command = lambda: base.messenger.send("Exit"),
            rolloverSound = None,
            clickSound = None)
        self.btnContinue.setTransparency(1)
        self.btnContinue.reparentTo(self.frameMain)
        self.hide()

    def show(self, winLoose, resulttime):
        if winLoose == "win":
            timestring = "%d:%02d" % (resulttime/60, resulttime%60)
            self.lblResult["text"] = timestring
            self.lblTime.show()
            self.lblResult.show()
        else:
            self.lblWin["text"] = "You Loose"
            self.lblTime.hide()
            self.lblResult.hide()
        self.frameMain.show()

    def hide(self):
        self.frameMain.hide()

