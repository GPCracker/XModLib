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
import constants

# *************************
# X-Mod Code Library
# *************************
from .VehicleMath import VehicleMath

class Colliders(object):
	@staticmethod
	def collideStatic(startPoint, endPoint, collisionFlags = 128):
		collisionResult = BigWorld.wg_collideSegment(BigWorld.player().spaceID, startPoint, endPoint, collisionFlags)
		return collisionResult[0] if collisionResult is not None else None

	@staticmethod
	def computeProjectileTrajectoryEnd(vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch, colliders):
		shotRay, shotPoint = VehicleMath.getShotRayAndPoint(vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch)
		shotSpeed = shotRay.scale(vehicleTypeDescriptor.shot['speed'])
		shotGravity = Math.Vector3(0, -1, 0).scale(vehicleTypeDescriptor.shot['gravity'])
		currentPoint, currentSpeed = Math.Vector3(shotPoint), Math.Vector3(shotSpeed)
		hitPoint, hitVector = None, None
		while True:
			checkPoints = BigWorld.wg_computeProjectileTrajectory(currentPoint, currentSpeed, shotGravity, constants.SERVER_TICK_LENGTH, constants.SHELL_TRAJECTORY_EPSILON_CLIENT)
			collisionTestStart = currentPoint
			for collisionTestStop in checkPoints:
				for collider in colliders:
					collisionResult = collider(collisionTestStart, collisionTestStop)
					if isinstance(collisionResult, (list, tuple)):
						collisionResult = collisionResult[0] if collisionResult else None
					if collisionResult is not None:
						hitPoint = collisionResult
						hitVector = collisionTestStop - collisionTestStart
						hitVector.normalise()
						break
				if hitPoint is not None and hitVector is not None:
					break
				collisionTestStart = collisionTestStop
			if hitPoint is not None and hitVector is not None:
				break
			currentPoint += currentSpeed.scale(constants.SERVER_TICK_LENGTH) + shotGravity.scale(constants.SERVER_TICK_LENGTH ** 2 * 0.5)
			currentSpeed += shotGravity.scale(constants.SERVER_TICK_LENGTH)
		return hitPoint, hitVector
