from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectFrame
from direct.gui.DirectGui import DirectButton
from direct.gui.DirectLabel import DirectLabel
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TextNode

class Menu(DirectObject):
    def __init__(self):
        self.accept("window-event", self.recalcAspectRatio)

        self.frameMain = DirectFrame(
            # size of the frame
            frameSize = (base.a2dLeft, base.a2dRight,
                         base.a2dTop, base.a2dBottom),
            # position of the frame
            image = "LogoTextGlow.png",
            image_scale = (1.06, 1, 0.7),
            image_pos = (0, 0, 0.25),
            pos = (0, 0, 0),
            # tramsparent bg color
            frameColor = (0, 0, 0, 0),
            sortOrder = 0)
        self.frameMain.setTransparency(1)
        self.frameMain.setBin("fixed", 100)

        btnGeom = None

        self.btnStart = self.createButton(_("Start"), btnGeom, -0.6, self.btnStart_Click)
        self.btnStart.reparentTo(self.frameMain)

        self.btnOptions = self.createButton(_("Options"), btnGeom, 0, self.btnOptions_Click)
        self.btnOptions.reparentTo(self.frameMain)

        self.btnQuit = self.createButton(_("Quit"), btnGeom, 0.6, self.btnQuit_Click)
        self.btnQuit.reparentTo(self.frameMain)

        self.recalcAspectRatio(base.win)

        # hide all buttons at startup
        self.hide()

    def show(self):
        self.frameMain.show()
        self.recalcAspectRatio(base.win)

    def hide(self):
        self.frameMain.hide()

    def recalcAspectRatio(self, window):
        """get the new aspect ratio to resize the mainframe"""
        screenResMultiplier = window.getXSize() / window.getYSize()
        self.frameMain["frameSize"] = (
            base.a2dLeft, base.a2dRight,
            base.a2dTop, base.a2dBottom)
        self.btnQuit["text_scale"] = (0.5*screenResMultiplier, 0.5, 0.5)
        self.btnStart["text_scale"] = (0.5*screenResMultiplier, 0.5, 0.5)


    def createButton(self, text, btnGeom, xPos, command):
        btn = DirectButton(
            scale = (0.25, 0.25, 0.25),
            # some temp text
            text = text,
            text_scale = (0.5, 0.5, 0.5),
            # set the alignment to right
            text_align = TextNode.ACenter,
            # put the text on the right side of the button
            text_pos = (0, -0.15),
            # set the text color to black
            text_fg = (1,1,1,1),
            text_shadow = (0.3, 0.3, 0.1, 1),
            text_shadowOffset = (0.05, 0.05),
            # set the buttons images
            #geom = btnGeom,
            relief = 1,
            frameColor = (0,0,0,0),
            pressEffect = False,
            pos = (xPos, 0, -0.65),
            command = command,
            rolloverSound = None,
            clickSound = None)
        btn.setTransparency(1)
        return btn

    def btnStart_Click(self):
        base.messenger.send("menu_start")

    def btnOptions_Click(self):
        base.messenger.send("menu_options")

    def btnQuit_Click(self):
        base.messenger.send("menu_quit")
