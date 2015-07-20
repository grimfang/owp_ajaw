from level.level01 import Level01
from player import Player

class World():
	def __init__(self):
		self.level = Level01()
		self.player = Player()

	def start(self):
		self.level.start()
		self.player.start(self.level.getPlayerStartPoint())

	def stop(self):
		self.level.stop()
		self.player.stop()
