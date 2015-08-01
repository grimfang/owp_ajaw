#!/usr/bin/python
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import os
import __builtin__
from direct.showbase.DirectObject import DirectObject
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectCheckBox import DirectCheckBox
from direct.gui.DirectGui import (
    DirectFrame,
    DirectLabel,
    DirectButton,
    DirectSlider,
    DirectCheckButton,
    DirectOptionMenu,
    DGG)
from panda3d.core import (
    TextNode,
    VBase3)

#
# Customized DirectOptionsMenu functions
#
def showPopupMenuExtra(self, args):
    showPopupMenu(self)
def showPopupMenu(self, event = None):
    """
    Make popup visible and try to position it below the main control.
    Adjust popup position if default position puts it outside of
    visible screen region
    """
    # Show the menu
    self.popupMenu.show()
    # Make sure its at the right scale
    self.popupMenu.setScale(self, VBase3(1))
    # Compute bounds
    b = self.getBounds()
    fb = self.popupMenu.getBounds()
    # Position menu at midpoint of button
    self.popupMenu.setX(self, b[0])
    # Try to set height to line up selected item with button
    self.popupMenu.setZ(self, -0.25)
    # Make sure the whole popup menu is visible
    pos = self.popupMenu.getPos(render2d)
    scale = self.popupMenu.getScale(render2d)
    # How about up and down?
    minZ = pos[2] + fb[2] * scale[2]
    maxZ = pos[2] + fb[3] * scale[2]
    if minZ < -1.0:
        # Menu too low, move it up
        self.popupMenu.setZ(render2d, pos[2] + (-1.0 - minZ))
    elif maxZ > 1.0:
        # Menu too high, move it down
        self.popupMenu.setZ(render2d, pos[2] + (1.0 - maxZ))
    # Also display cancel frame to catch clicks outside of the popup
    self.cancelFrame.show()
    # Position and scale cancel frame to fill entire window
    self.cancelFrame.setPos(render2d, 0, 0, 0)
    self.cancelFrame.setScale(render2d, 1, 1, 1)

def setItems(self):
    """
    self['items'] = itemList
    Create new popup menu to reflect specified set of items
    """
    # Remove old component if it exits
    if self.popupMenu != None:
        self.destroycomponent('popupMenu')
    # Create new component
    self.popupMenu = self.createcomponent('popupMenu', (), None,
                                          DirectFrame,
                                          (self,),
                                          relief = 'raised',
                                          )
    # Make sure it is on top of all the other gui widgets
    self.popupMenu.setBin('gui-popup', 0)
    if not self['items']:
        return
    # Create a new component for each item
    # Find the maximum extents of all items
    itemIndex = 0
    self.minX = self.maxX = self.minZ = self.maxZ = None
    for item in self['items']:
        c = self.createcomponent(
            'item%d' % itemIndex, (), 'item',
            DirectButton, (self.popupMenu,),
            text = item, text_align = TextNode.ALeft,
            command = lambda i = itemIndex: self.set(i))
        bounds = c.getBounds()
        if self.minX == None:
            self.minX = bounds[0]
        elif bounds[0] < self.minX:
            self.minX = bounds[0]
        if self.maxX == None:
            self.maxX = bounds[1]
        elif bounds[1] > self.maxX:
            self.maxX = bounds[1]
        if self.minZ == None:
            self.minZ = bounds[2]
        elif bounds[2] < self.minZ:
            self.minZ = bounds[2]
        if self.maxZ == None:
            self.maxZ = bounds[3]
        elif bounds[3] > self.maxZ:
            self.maxZ = bounds[3]
        itemIndex += 1
    # Calc max width and height
    self.maxWidth = self.maxX - self.minX
    self.maxHeight = self.maxZ - self.minZ
    # Adjust frame size for each item and bind actions to mouse events
    for i in range(itemIndex):
        item = self.component('item%d' %i)
        # So entire extent of item's slot on popup is reactive to mouse
        item['frameSize'] = (self.minX, self.maxX, self.minZ, self.maxZ)
        item["frameColor"] = (0, 0, 0, 0)
        item["text_fg"] = (1,1,1,1)
        item["relief"] = DGG.FLAT
        # Move it to its correct position on the popup
        item.setPos(-self.minX, 0, -self.maxZ - i * self.maxHeight)
        item.bind(DGG.B1RELEASE, self.hidePopupMenu)
        # Highlight background when mouse is in item
        item.bind(DGG.WITHIN,
                  lambda x, i=i, item=item:self._highlightItem(item, i))
        # Restore specified color upon exiting
        fc = item['frameColor']
        item.bind(DGG.WITHOUT,
                  lambda x, item=item, fc=fc: self._unhighlightItem(item, fc))
    # Set popup menu frame size to encompass all items
    f = self.component('popupMenu')
    f['frameSize'] = (0, self.maxWidth, -self.maxHeight * itemIndex, 0)
    f["frameColor"] = (0.10, 0.10, 0.10, 1)
    f["relief"] = DGG.FLAT

    # Determine what initial item to display and set text accordingly
    if self['initialitem']:
        self.set(self['initialitem'], fCommand = 0)
    else:
        # No initial item specified, just use first item
        self.set(0, fCommand = 0)

    # Position popup Marker to the right of the button
    pm = self.popupMarker
    pmw = (pm.getWidth() * pm.getScale()[0] +
           2 * self['popupMarkerBorder'][0])
    if self.initFrameSize:
        # Use specified frame size
        bounds = list(self.initFrameSize)
    else:
        # Or base it upon largest item
        bounds = [self.minX, self.maxX, self.minZ, self.maxZ]
    pm.setPos(bounds[1] + pmw/2.0, 0,
              bounds[2] + (bounds[3] - bounds[2])/2.0)
    # Adjust popup menu button to fit all items (or use user specified
    # frame size
    bounds[1] += pmw
    self['frameSize'] = (bounds[0], bounds[1], bounds[2], bounds[3])
    # Set initial state
    self.hidePopupMenu()


class OptionsMenu(DirectObject):
    def __init__(self):
        """Default constructor"""
        # create a main frame as big as the window
        self.frameMain = DirectFrame(
            # set framesize the same size as the window
            frameSize = (base.a2dLeft, base.a2dRight,
                         base.a2dTop, base.a2dBottom),
            image = "LogoTextGlow.png",
            image_scale = (1.06/2.0, 1, 0.7/2.0),
            image_pos = (0, 0, 0.7),
            # position center
            pos = (0, 0, 0),
            # set tramsparent background color
            frameColor = (0, 0, 0, 0))
        self.frameMain.setTransparency(1)
        self.frameMain.setBin("fixed", 100)

        sliderscale = 0.5
        buttonScale = 0.25
        textscale = 0.1
        checkboxscale = 0.05
        left = -0.5
        right = 0.5

        self.sliderTextspeed = DirectSlider(
            scale = sliderscale,
            pos = (left, 0, 0.2),
            range = (0.2,0.01),
            scrollSize = 0.01,
            text = _("Textspeed %0.1f%%")%(base.textWriteSpeed * 10),
            text_scale = textscale,
            text_align = TextNode.ACenter,
            text_pos = (0.0, 0.15),
            text_fg = (1,1,1,1),
            thumb_frameColor = (0.65, 0.65, 0.0, 1),
            thumb_relief = DGG.FLAT,
            frameColor = (0.15, 0.15, 0.15, 1),
            value = base.textWriteSpeed,
            command = self.sliderTextspeed_ValueChanged)
        self.sliderTextspeed.reparentTo(self.frameMain)

        self.cbParticles = DirectCheckButton(
            text = _(" Enable Particles"),
            text_fg = (1, 1, 1, 1),
            text_shadow = (0, 0, 0, 0.35),
            pos = (left, 0, -0.0),
            scale = checkboxscale,
            frameColor = (0,0,0,0),
            command = self.cbParticles_CheckedChanged,
            rolloverSound = None,
            clickSound = None,
            pressEffect = False,
            boxPlacement = "below",
            boxBorder = 0.8,
            boxRelief = DGG.FLAT,
            indicator_scale = 1.5,
            indicator_text_fg = (0.65, 0.65, 0.0, 1),
            indicator_text_shadow = (0, 0, 0, 0.35),
            indicator_frameColor = (0.15, 0.15, 0.15, 1),
            indicatorValue = base.particleMgrEnabled
            )
        self.cbParticles.indicator['text'] = (' ', 'x')
        self.cbParticles.indicator['text_pos'] = (0, 0.1)
        #self.cbParticles.indicator.setX(self.cbParticles.indicator, -0.5)
        #self.cbParticles.indicator.setZ(self.cbParticles.indicator, -0.1)
        #self.cbParticles.setFrameSize()
        self.cbParticles.setTransparency(1)
        self.cbParticles.reparentTo(self.frameMain)

        volume = base.musicManager.getVolume()
        self.sliderVolume = DirectSlider(
            scale = sliderscale,
            pos = (left, 0, -0.35),
            range = (0,1),
            scrollSize = 0.01,
            text = _("Volume %d%%")%volume*100,
            text_scale = textscale,
            text_align = TextNode.ACenter,
            text_pos = (.0, 0.15),
            text_fg = (1,1,1,1),
            thumb_frameColor = (0.65, 0.65, 0.0, 1),
            thumb_relief = DGG.FLAT,
            frameColor = (0.15, 0.15, 0.15, 1),
            value = volume,
            command = self.sliderVolume_ValueChanged)
        self.sliderVolume.reparentTo(self.frameMain)

        self.lblControltype = DirectLabel(
            text = _("Control type"),
            text_fg = (1, 1, 1, 1),
            text_shadow = (0, 0, 0, 0.35),
            frameColor = (0, 0, 0, 0),
            scale = textscale/2,
            pos = (right, 0, 0.27))
        self.lblControltype.setTransparency(1)
        self.lblControltype.reparentTo(self.frameMain)
        selectedControlType = 0
        if base.controlType == "MouseAndKeyboard":
            selectedControlType = 1
        self.controltype = DirectOptionMenu(
            pos = (right, 0, 0.18),
            text_fg = (1, 1, 1, 1),
            scale = 0.1,
            items = [_("Keyboard"),_("Keyboard + Mouse")],
            initialitem = selectedControlType,
            frameColor = (0.15, 0.15, 0.15, 1),
            popupMarker_frameColor = (0.65, 0.65, 0.0, 1),
            popupMarker_relief = DGG.FLAT,
            highlightColor = (0.65, 0.65, 0.0, 1),
            relief = DGG.FLAT,
            command=self.controlType_Changed)
        self.controltype.reparentTo(self.frameMain)
        b = self.controltype.getBounds()
        xPos = right - ((b[1] - b[0]) / 2.0 * 0.1)
        self.controltype.setX(xPos)
        setItems(self.controltype)
        self.controltype.setItems = setItems
        self.controltype.showPopupMenu = showPopupMenu
        self.controltype.popupMarker.unbind(DGG.B1PRESS)
        self.controltype.popupMarker.bind(DGG.B1PRESS, showPopupMenu)
        self.controltype.unbind(DGG.B1PRESS)
        self.controltype.bind(DGG.B1PRESS, showPopupMenuExtra, [self.controltype])

        isChecked = not base.AppHasAudioFocus
        img = None
        if base.AppHasAudioFocus:
            img = "AudioSwitch_on.png"
        else:
            img = "AudioSwitch_off.png"
        self.cbVolumeMute = DirectCheckBox(
            text = _("Mute Audio"),
            text_scale = 0.5,
            text_align = TextNode.ACenter,
            text_pos = (0.0, 0.65),
            text_fg = (1,1,1,1),
            pos = (right, 0, -0.35),
            scale = 0.21/2.0,
            command = self.cbVolumeMute_CheckedChanged,
            rolloverSound = None,
            clickSound = None,
            relief = None,
            pressEffect = False,
            isChecked = isChecked,
            image = img,
            image_scale = 0.5,
            checkedImage = "AudioSwitch_off.png",
            uncheckedImage = "AudioSwitch_on.png")
        self.cbVolumeMute.setTransparency(1)
        self.cbVolumeMute.setImage()
        self.cbVolumeMute.reparentTo(self.frameMain)

        sensitivity = base.mouseSensitivity
        self.sliderSensitivity = DirectSlider(
            scale = sliderscale,
            pos = (right, 0, -0.075),
            range = (0.5,2),
            scrollSize = 0.01,
            text = _("Mouse Sensitivity %0.1fx")%sensitivity,
            text_scale = textscale,
            text_align = TextNode.ACenter,
            text_pos = (.0, 0.15),
            text_fg = (1,1,1,1),
            thumb_frameColor = (0.65, 0.65, 0.0, 1),
            thumb_relief = DGG.FLAT,
            frameColor = (0.15, 0.15, 0.15, 1),
            value = sensitivity,
            command = self.sliderSensitivity_ValueChanged)
        self.sliderSensitivity.reparentTo(self.frameMain)
        if base.controlType == "Gamepad":
            self.sliderSensitivity.hide()

        # create the back button
        self.btnBack = DirectButton(
            scale = buttonScale,
            # position on the window
            pos = (0, 0, base.a2dBottom + 0.15),
            frameColor = (0,0,0,0),
            # text properties
            text = _("Back"),
            text_scale = 0.5,
            text_fg = (1,1,1,1),
            text_pos = (0.0, -0.15),
            text_shadow = (0, 0, 0, 0.35),
            text_shadowOffset = (-0.05, -0.05),
            # sounds that should be played
            rolloverSound = None,
            clickSound = None,
            pressEffect = False,
            relief = None,
            # the event which is thrown on clickSound
            command = lambda: base.messenger.send("options_back"))
        self.btnBack.setTransparency(1)
        self.btnBack.reparentTo(self.frameMain)

        self.hide()


    def show(self, enableResume=False):
        self.frameMain.show()

    def hide(self):
        self.frameMain.hide()

    def cbVolumeMute_CheckedChanged(self, checked):
        if checked:
            base.disableAllAudio()
        else:
            base.enableAllAudio()

    def sliderVolume_ValueChanged(self):
        volume = round(self.sliderVolume["value"], 2)
        self.sliderVolume["text"] = _("Volume %d%%") % int(volume * 100)
        base.sfxManagerList[0].setVolume(volume)
        base.musicManager.setVolume(volume)

    def sliderSensitivity_ValueChanged(self):
        sensitivity = round(self.sliderSensitivity["value"], 2)
        self.sliderSensitivity["text"] = _("Mouse Sensitivity %0.1fx") % sensitivity
        base.mouseSensitivity = sensitivity

    def sliderTextspeed_ValueChanged(self):
        newSpeed = round(self.sliderTextspeed["value"], 2)
        displaySpeed = 1.0 / newSpeed
        self.sliderTextspeed["text"] = _("Textspeed %0.1f%%")%displaySpeed
        base.textWriteSpeed = newSpeed

    def cbParticles_CheckedChanged(self, unchecked):
        if unchecked:
            base.enableParticles()
        else:
            base.disableParticles()

    def controlType_Changed(self, arg):
        if arg == _("Keyboard"):
            self.sliderSensitivity.hide()
            base.controlType = "Gamepad"
        elif arg == _("Keyboard + Mouse"):
            self.sliderSensitivity.show()
            base.controlType = "MouseAndKeyboard"
