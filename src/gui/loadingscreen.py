"""Show a directWaitbar to display the current loading state of the application"""
from direct.gui.DirectGui import DirectFrame
from direct.gui.DirectGui import DirectWaitBar
from direct.gui.DirectGui import DirectLabel
from panda3d.core import TextNode


class LoadingScreen():
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

        # the text Loading... on top
        self.lblLoading = DirectLabel(
            scale = 0.25,
            pos = (0, 0, 0),
            frameColor = (0, 0, 0, 0),
            text = "Loading...",
            text_align = TextNode.ACenter,
            text_fg = (1,1,1,1))
        self.lblLoading.reparentTo(self.frameMain)

        # the waitbar on the bottom
        self.wbLoading = DirectWaitBar(
            text = "0%",
            text_fg = (1,1,1,1),
            value = 0,
            pos = (0, 0, -0.5),
            barColor = (0.5, 0.4, 0.1, 1),
            frameColor = (0.1, 0.1, 0.1, 1))
        self.wbLoading.reparentTo(self.frameMain)

    def show(self):
        self.frameMain.show()
        # and render two frames so the loading screen
        # is realy shown on screen
        base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()

    def hide(self):
        self.frameMain.hide()

    def setLoadingValue(self, value):
        """Set the waitbar value to the given value, where
        value has to be a integer from 0 to 100"""
        if value > 100: value = 100
        if value < 0: value = 0
        self.wbLoading["value"] = value
        self.wbLoading["text"] = "{0}%".format(value)
        base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()

