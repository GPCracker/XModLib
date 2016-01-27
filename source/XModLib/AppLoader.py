# Authors: GPCracker

# *************************
# Python
# *************************
# Nothing

# *************************
# BigWorld
# *************************
# Nothing

# *************************
# WoT Client
# *************************
import gui.app_loader

# *************************
# X-Mod Code Library
# *************************
# Nothing

class AppLoader(object):
	@staticmethod
	def getBattleApp():
		return gui.app_loader.g_appLoader.getDefBattleApp()

	@staticmethod
	def getLobbyApp():
		return gui.app_loader.g_appLoader.getDefLobbyApp()
