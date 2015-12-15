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
# Nothing

class XRayScanner(object):
	@staticmethod
	def getActiveVehicles(fltr = None):
		for vehicleID in filter(fltr, BigWorld.player().arena.vehicles.iterkeys()):
			if vehicleID == BigWorld.player().playerVehicleID:
				continue
			vehicle = BigWorld.entity(vehicleID)
			if vehicle is not None and vehicle.isStarted:
				activeVehicles.append(vehicle)
		return activeVehicles

	@staticmethod
	def scanXRay(scanStart, scanDir, maxDistance, entities, skipGun = False):
		collisionResult = min(filter(lambda collisionResult: collisionResult[1] is not None, [(entity, entity.collideSegment(scanStart, scanStart + scanDir * maxDistance, skipGun)) for entity in entities]), key = lambda collisionResult: collisionResult[1].dist)
		return {
			'scanStart': scanStart,
			'scanDir': scanDir,
			'distance': collisionResult[1].dist,
			'hitPoint': scanStart + scanDir * collisionResult[1].dist,
			'entity': collisionResult[0],
			'hitAngleCos': collisionResult[1].hitAngleCos,
			'armor': collisionResult[1].armor
		}

	@classmethod
	def getTarget(sclass, maxDistance = 720, fltr = None, skipGun = False):
		scanDir, scanStart = AvatarInputHandler.cameras.getWorldRayAndPoint(*BigWorld.player().inputHandler.ctrl.getAim().offset())
		scanDir.normalise()
		scanResult = sclass.scanXRay(scanStart, scanDir, maxDistance, sclass.getActiveVehicles(fltr), skipGun)
		return scanResult['entity'] if scanResult is not None else None
