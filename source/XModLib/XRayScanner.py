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
# X-Mod Library
# *************************
from .Colliders import Colliders

class XRayScanner(object):
	@staticmethod
	def getTarget(filterID=None, filterVehicle=None, maxDistance=720.0, skipGun=False, skipPlayer=True, entities=None):
		scanDir, scanStart = AvatarInputHandler.cameras.getWorldRayAndPoint(*BigWorld.player().inputHandler.ctrl._aimOffset)
		scanDir.normalise()
		scanStop = scanStart + scanDir * maxDistance
		scanResult = Colliders.collideVehicles(
			Colliders.getVisibleVehicles(filterID, filterVehicle, skipPlayer) if entities is None else entities,
			scanStart,
			scanStop,
			skipGun
		)
		return scanResult[1] if scanResult is not None else None
