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
import AvatarInputHandler.cameras

# *************************
# X-Mod Code Library
# *************************
from .Colliders import Colliders

class XRayScanner(object):
	@staticmethod
	def getTarget(filterID=None, filterVehicle=None, maxDistance=720, skipGun=False, skipPlayer=True):
		scanDir, scanStart = AvatarInputHandler.cameras.getWorldRayAndPoint(*BigWorld.player().inputHandler.ctrl.getAim().offset())
		scanDir.normalise()
		scanStop = scanStart + scanDir * maxDistance
		scanResult = Colliders.collideVehicles(Colliders.getVisibleVehicles(filterID, filterVehicle, skipPlayer), scanStart, scanStop, skipGun)
		return scanResult[1] if scanResult is not None else None
