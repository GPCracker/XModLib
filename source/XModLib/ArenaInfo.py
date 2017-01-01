# Authors: GPCracker

# *************************
# Python
# *************************
# Nothing

# *************************
# BigWorld
# *************************
import BigWorld

# *************************
# WoT Client
# *************************
# Nothing

# *************************
# X-Mod Library
# *************************
# Nothing

class ArenaInfo(object):
	@staticmethod
	def isSquadMan(vehicleID):
		return BigWorld.player().guiSessionProvider.getCtx().isSquadMan(vehicleID)

	@staticmethod
	def isTeamKiller(vehicleID):
		return BigWorld.player().guiSessionProvider.getCtx().isTeamKiller(vehicleID)

	@staticmethod
	def isObserver(vehicleID):
		return BigWorld.player().guiSessionProvider.getCtx().isObserver(vehicleID)

	@staticmethod
	def isAlly(vehicleID):
		return BigWorld.player().guiSessionProvider.getCtx().isAlly(vehicleID)

	@staticmethod
	def isEnemy(vehicleID):
		return BigWorld.player().guiSessionProvider.getCtx().isEnemy(vehicleID)

	@staticmethod
	def isAlive(vehicleID):
		return BigWorld.player().guiSessionProvider.getArenaDP().getVehicleInfo(vehicleID).isAlive()

	@staticmethod
	def isReady(vehicleID):
		return BigWorld.player().guiSessionProvider.getArenaDP().getVehicleInfo(vehicleID).isReady()

	@staticmethod
	def getTeam(vehicleID):
		return BigWorld.player().guiSessionProvider.getArenaDP().getVehicleInfo(vehicleID).team

	@staticmethod
	def getLevel(vehicleID):
		return BigWorld.player().guiSessionProvider.getArenaDP().getVehicleInfo(vehicleID).vehicleType.level

	@staticmethod
	def getClass(vehicleID):
		return BigWorld.player().guiSessionProvider.getArenaDP().getVehicleInfo(vehicleID).vehicleType.classTag

	@staticmethod
	def getShortName(vehicleID):
		return BigWorld.player().guiSessionProvider.getArenaDP().getVehicleInfo(vehicleID).vehicleType.shortName

	@staticmethod
	def getFrags(vehicleID):
		return BigWorld.player().guiSessionProvider.getArenaDP().getVehicleStats(vehicleID).frags

	@staticmethod
	def getPlayerVehicleID():
		return BigWorld.player().guiSessionProvider.getArenaDP().getPlayerVehicleID()

	@staticmethod
	def getTeamScore(team):
		arenaDP = BigWorld.player().guiSessionProvider.getArenaDP()
		frags = sum(vStatsVO.frags for vStatsVO in arenaDP.getVehiclesStatsIterator() if arenaDP.getVehicleInfo(vStatsVO.vehicleID).team == team)
		alive = sum(vInfoVO.isAlive() for vInfoVO in arenaDP.getVehiclesInfoIterator() if arenaDP.getVehicleInfo(vInfoVO.vehicleID).team == team)
		return frags, alive
