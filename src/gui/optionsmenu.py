#!/usr/bin/python
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import os
import __builtin__
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectCheckBox import DirectCheckBox
from direct.gui.DirectGui import (
	DirectFrame,
	DirectLabel,
	DirectButton,
	DirectCheckButton,
	DGG)
from panda3d.core import TextNode

class OptionsMenu(DirectObject):
	def __init__(self):
		"""Default constructor"""
		# create a main frame as big as the window
		self.frameMain = DirectFrame(
			# set framesize the same size as the window
			frameSize = (base.a2dLeft, base.a2dRight,
						 base.a2dTop, base.a2dBottom),
			image = "LogoText.png",
			image_scale = (1/2.0, 1, 0.7/2.0),
			image_pos = (0, 0, 0.5),
			# position center
			pos = (0, 0, 0),
			# set tramsparent background color
			frameColor = (0, 0, 0, 0))

		buttonScale = 0.25
		geom = None

		isChecked = not base.AppHasAudioFocus
		img = None
		if base.AppHasAudioFocus:
			img = "AudioSwitch_on.png"
		else:
			img = "AudioSwitch_off.png"
		self.cbVolumeMute = DirectCheckBox(
			text = "",
			pos = (0, 0, -0.5),
			scale = 0.25,
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

		self.cbParticles = DirectCheckButton(
			text = "Particles",
			text_fg = (1, 1, 1, 1),
			text_shadow = (0, 0, 0, 0.35),
			pos = (0, 0, -0.2),
			scale = 0.15,
			command = self.cbParticles_CheckedChanged,
			rolloverSound = None,
			clickSound = None,
			#relief = None,
			pressEffect = False,
			indicatorValue = base.particleMgrEnabled
			)
		self.cbParticles.setTransparency(1)
		#self.cbParticles.setImage()
		self.cbParticles.reparentTo(self.frameMain)

		# create the back button
		self.btnBack = DirectButton(
			scale = buttonScale,
			# position on the window
			pos = (0, 0, base.a2dBottom + 0.15),
			frameColor = (0,0,0,0),
			#geom = geom,
			# text properties
			text = "Back",
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

	def cbParticles_CheckedChanged(self, unchecked):
		if unchecked:
			base.enableParticles()
		else:
			base.disableParticles()
