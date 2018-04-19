# Authors: Vladislav Ignatenko <gpcracker@mail.ru>

# ------------ #
#    Python    #
# ------------ #
import operator
import itertools

# -------------- #
#    BigWorld    #
# -------------- #
import Math
import BigWorld

# ---------------- #
#    WoT Client    #
# ---------------- #
import constants
import vehicle_systems.tankStructure

# ------------------- #
#    X-Mod Library    #
# ------------------- #
from . import MathUtils
from . import VehicleInfo
from . import VehicleMath

# -------------------- #
#    Module Content    #
# -------------------- #
def collideStatic(startPoint, endPoint, excludeFlags=128, includeFlags=0):
	'''
	BigWorld.wg_collideSegment(spaceID, startPoint, endPoint, excludeFlags, includeFlags) -->
		PyCollideSegment(closestPoint, normal, matKind, isTerrain()) or None
	Collision flags:
		1 - unknown
		2 - unknown
		4 - unknown
		8 - terrain
		16 - unknown
		32 - unknown
		64 - unknown
		128 - weak destructible objects
	'''
	return BigWorld.wg_collideSegment(BigWorld.player().spaceID, startPoint, endPoint, excludeFlags, includeFlags)

def getVisibleVehicles(filterID=None, filterVehicle=None, skipPlayer=False):
	vehicleIDs = iter(BigWorld.player().arena.vehicles)
	if skipPlayer:
		excludeIDs = (BigWorld.player().observedVehicleID or BigWorld.player().playerVehicleID, )
		vehicleIDs = itertools.ifilter(lambda vehicleID: vehicleID not in excludeIDs, vehicleIDs)
	vehicleIDs = itertools.ifilter(filterID, vehicleIDs)
	vehicles = itertools.imap(BigWorld.entity, vehicleIDs)
	vehicles = itertools.ifilter(VehicleInfo.isStarted, vehicles)
	return list(itertools.ifilter(filterVehicle, vehicles))

def collideVehicle(vehicle, startPoint, endPoint, skipGun=False):
	# This method returns collision data for the first armor layer only
	# Therefore it should not be used for vehicle total armor calculations
	if vehicle.appearance.collisions is not None:
		gunPartIndex = vehicle_systems.tankStructure.TankPartIndexes.GUN
		collisions = vehicle.appearance.collisions.collideAllWorld(startPoint, endPoint)
		if collisions is not None:
			for distance, hitAngleCos, materialKind, partIndex in collisions:
				materialInfo = vehicle.getMatinfo(partIndex, materialKind)
				if materialInfo and (not skipGun or partIndex != gunPartIndex):
					return distance, hitAngleCos, materialInfo.armor
	return None

def collideVehicles(vehicles, startPoint, endPoint, skipGun=False):
	collisions = list()
	for vehicle in vehicles:
		collision = collideVehicle(vehicle, startPoint, endPoint, skipGun)
		if collision is not None:
			collisions.append((vehicle, ) + collision)
	if collisions:
		vehicle, distance, cos, armor = min(collisions, key=operator.itemgetter(1))
		collpoint = startPoint + MathUtils.getNormalisedVector(endPoint - startPoint).scale(distance)
		return collpoint, vehicle, cos, armor
	return None

def collideSpaceBB(startPoint, endPoint):
	collisionResult = BigWorld.player().arena.collideWithSpaceBB(startPoint, endPoint)
	return (collisionResult, ) if collisionResult is not None else None

def collideArenaBB(startPoint, endPoint):
	collisionResult = BigWorld.player().arena.collideWithArenaBB(startPoint, endPoint)
	return (collisionResult, ) if collisionResult is not None else None

def collideGeometry(function, startPoint, endPoint):
	collisionResult = function(startPoint, endPoint)
	return (collisionResult, ) if collisionResult is not None else None

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

def computeVehicleProjectileTrajectoryEnd(vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch, colliders):
	shotRay, shotPoint = VehicleMath.getShotRayAndPoint(vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch)
	shotVector = shotRay.scale(vehicleTypeDescriptor.shot.speed)
	shotGravity = Math.Vector3(0, -1, 0).scale(vehicleTypeDescriptor.shot.gravity)
	return computeProjectileTrajectoryEnd(shotPoint, shotVector, shotGravity, colliders)

def computePlayerVehicleProjectileTrajectoryEnd(colliders):
	vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch = VehicleMath.getPlayerVehicleParams()
	return computeVehicleProjectileTrajectoryEnd(vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch, colliders)
