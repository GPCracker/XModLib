# Authors: GPCracker

# *************************
# Python
# *************************
# Nothing

# *************************
# BigWorld
# *************************
import BigWorld
import Math

# *************************
# WoT Client
# *************************
import constants

# *************************
# X-Mod Code Library
# *************************
from .MathUtils import MathUtils
from .VehicleMath import VehicleMath

class Colliders(object):
	@staticmethod
	def collideStatic(startPoint, endPoint, collisionFlags=128, resultFilter=None):
		'''
		BigWorld.wg_collideSegment(spaceID, start, end, collFlags, lambda matKind, collFlags, itemId, chunkId: True) --> (point, normal, matKind, ???(pos), itemId, chunkId) or None
		'''
		return BigWorld.wg_collideSegment(BigWorld.player().spaceID, startPoint, endPoint, collisionFlags, resultFilter)

	@staticmethod
	def getVisibleVehicles(filterID=None, filterVehicle=None, skipPlayer=False):
		vehicles = list()
		for vehicleID in filter(filterID, BigWorld.player().arena.vehicles):
			if skipPlayer and vehicleID == BigWorld.player().playerVehicleID:
				continue
			vehicle = BigWorld.entity(vehicleID)
			if vehicle is not None and vehicle.isStarted:
				vehicles.append(vehicle)
		return filter(filterVehicle, vehicles)

	@staticmethod
	def collideVehicles(vehicles, startPoint, endPoint, skipGun=False):
		'''
		vehicle.collideSegment(startPoint, endPoint, skipGun) --> (distance, hitAngleCos, armor)
		'''
		collisionResults = list()
		for vehicle in vehicles:
			collisionResult = vehicle.collideSegment(startPoint, endPoint, skipGun)
			if collisionResult is not None:
				distance, cos, armor = collisionResult
				collisionResults.append((distance, vehicle, cos, armor))
		if collisionResults:
			distance, vehicle, cos, armor = min(collisionResults, key = lambda collisionResult: collisionResult[0])
			return startPoint + MathUtils.getNormalisedVector(endPoint - startPoint).scale(distance), vehicle, cos, armor
		return None

	@staticmethod
	def collideSpaceBB(startPoint, endPoint):
		collisionResult = BigWorld.player().arena.collideWithSpaceBB(startPoint, endPoint)
		return (collisionResult, ) if collisionResult is not None else None

	@staticmethod
	def collideArenaBB(startPoint, endPoint):
		collisionResult = BigWorld.player().arena.collideWithArenaBB(startPoint, endPoint)
		return (collisionResult, ) if collisionResult is not None else None

	@staticmethod
	def collideGeometry(function, startPoint, endPoint):
		collisionResult = function(startPoint, endPoint)
		return (collisionResult, ) if collisionResult is not None else None

	@staticmethod
	def computeProjectileTrajectoryEnd(shotPoint, shotVector, shotGravity, colliders):
		currentTime, currentPoint, currentSpeed = 0.0, shotPoint, shotVector
		hitPoint, hitVector, hitResult, hitCollider = None, None, None, None
		while True:
			checkPoints = BigWorld.wg_computeProjectileTrajectory(currentPoint, currentSpeed, shotGravity, constants.SERVER_TICK_LENGTH, constants.SHELL_TRAJECTORY_EPSILON_CLIENT)
			collisionTestStart = currentPoint
			for collisionTestStop in checkPoints:
				collisions = list()
				for collider in colliders:
					collisionResult = collider(collisionTestStart, collisionTestStop)
					if collisionResult is not None:
						collisions.append((collider, collisionResult))
				if collisions:
					collision = min(collisions, key=lambda collision: collision[1][0].distSqrTo(collisionTestStart))
					hitPoint = collision[1][0]
					hitVector = MathUtils.getNormalisedVector(collisionTestStop - collisionTestStart)
					hitResult = collision[1]
					hitCollider = collision[0]
					break
				collisionTestStart = collisionTestStop
			if hitResult is not None and hitPoint is not None and hitVector is not None and hitCollider is not None:
				break
			currentTime += constants.SERVER_TICK_LENGTH
			# Additional calculation type has less accuracy.
			currentPoint = shotPoint + shotVector.scale(currentTime) + shotGravity.scale(currentTime * currentTime * 0.5)
			currentSpeed = shotVector + shotGravity.scale(currentTime)
		return hitPoint, hitVector, hitResult, hitCollider

	@classmethod
	def computeVehicleProjectileTrajectoryEnd(sclass, vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch, colliders):
		shotRay, shotPoint = VehicleMath.getShotRayAndPoint(vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch)
		shotVector = shotRay.scale(vehicleTypeDescriptor.shot['speed'])
		shotGravity = Math.Vector3(0, -1, 0).scale(vehicleTypeDescriptor.shot['gravity'])
		return sclass.computeProjectileTrajectoryEnd(shotPoint, shotVector, shotGravity, colliders)

	@classmethod
	def computePlayerVehicleProjectileTrajectoryEnd(sclass, colliders):
		vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch = VehicleMath.getPlayerVehicleParams()
		return sclass.computeVehicleProjectileTrajectoryEnd(vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch, colliders)
