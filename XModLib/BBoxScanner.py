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
from .Geometry import BoundingBox

class BBoxScanner(object):
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
	def getVehicleBoundingBox(vehicle, scalar = 1.0):
		vehicleBB = BoundingBox.getModelBoundingBox(vehicle.model)
		vehicleBB.scale(scalar)
		return vehicleBB

	@classmethod
	def scanTarget(sclass, scanStart, scanDir, maxDistance, entities, scalar = 1.0):
		scanStop = scanStart + scanDir * maxDistance
		collisionResults = filter(lambda collisionResult: collisionResult[1], [(entity, sclass.getVehicleBoundingBox(entity, scalar).intersectSegment(scanStart, scanStop)) for entity in entities])
		return collisionResults[0][0] if len(collisionResults) == 1 else None

	@classmethod
	def getTarget(sclass, maxDistance = 720, scalar = 1.0, fltr = None):
		scanDir, scanStart = AvatarInputHandler.cameras.getWorldRayAndPoint(*BigWorld.player().inputHandler.ctrl.getAim().offset())
		scanDir.normalise()
		return sclass.scanTarget(scanStart, scanDir, maxDistance, sclass.getActiveVehicles(fltr), scalar)
