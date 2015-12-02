# Authors: GPCracker

import gui.app_loader

class AppLoader(object):
	@staticmethod
	def getBattleApp():
		return gui.app_loader.g_appLoader.getDefBattleApp()

	@staticmethod
	def getLobbyApp():
		return gui.app_loader.g_appLoader.getDefLobbyApp()
