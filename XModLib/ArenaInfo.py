# Authors: GPCracker

import gui.battle_control

class ArenaInfo(object):
	@staticmethod
	def isSquadMan(vehicleID):
		return gui.battle_control.g_sessionProvider.getCtx().isSquadMan(vehicleID)

	@staticmethod
	def isTeamKiller(vehicleID):
		return gui.battle_control.g_sessionProvider.getCtx().isTeamKiller(vehicleID)

	@staticmethod
	def isObserver(vehicleID):
		return gui.battle_control.g_sessionProvider.getCtx().isObserver(vehicleID)

	@staticmethod
	def isAlly(vehicleID):
		return gui.battle_control.g_sessionProvider.getCtx().isAlly(vehicleID)

	@staticmethod
	def isEnemy(vehicleID):
		return gui.battle_control.g_sessionProvider.getCtx().isEnemy(vehicleID)

	@staticmethod
	def isAlive(vehicleID):
		return gui.battle_control.g_sessionProvider.getArenaDP().getVehicleInfo(vehicleID).isAlive()

	@staticmethod
	def isReady(vehicleID):
		return gui.battle_control.g_sessionProvider.getArenaDP().getVehicleInfo(vehicleID).isReady()

	@staticmethod
	def getTeam(vehicleID):
		return gui.battle_control.g_sessionProvider.getArenaDP().getVehicleInfo(vehicleID).team

	@staticmethod
	def getLevel(vehicleID):
		return gui.battle_control.g_sessionProvider.getArenaDP().getVehicleInfo(vehicleID).vehicleType.level

	@staticmethod
	def getClass(vehicleID):
		return gui.battle_control.g_sessionProvider.getArenaDP().getVehicleInfo(vehicleID).vehicleType.classTag

	@staticmethod
	def getFrags(vehicleID):
		return gui.battle_control.g_sessionProvider.getArenaDP().getVehicleStats(vehicleID).frags

	@staticmethod
	def getPlayerVehicleID():
		return gui.battle_control.g_sessionProvider.getArenaDP().getPlayerVehicleID()

	@staticmethod
	def getTeamScore(teamID):
		return tuple(map(sum, zip(*[(vStatsVO.frags, vInfoVO.isAlive()) for vInfoVO, vStatsVO, viStatsVO in gui.battle_control.g_sessionProvider.getArenaDP().getTeamIterator(teamID)])))
