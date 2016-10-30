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
# Nothing

# *************************
# X-Mod Library
# *************************
# Nothing

class VehicleMath(object):
	@staticmethod
	def getVehicleHeight(vehicle):
		typeDesc = vehicle.typeDescriptor
		hullTopY = typeDesc.chassis['hullPosition'][1] + typeDesc.hull['hitTester'].bbox[1][1]
		turretTopY = typeDesc.chassis['hullPosition'][1] + typeDesc.hull['turretPositions'][0][1] + typeDesc.turret['hitTester'].bbox[1][1]
		gunTopY = typeDesc.chassis['hullPosition'][1] + typeDesc.hull['turretPositions'][0][1] + typeDesc.turret['gunPosition'][1] + typeDesc.gun['hitTester'].bbox[1][1]
		return max(hullTopY, turretTopY, gunTopY)

	@classmethod
	def getVehicleHeightVector(sclass, vehicle, height=None):
		return Math.Matrix(vehicle.matrix).applyToAxis(1).scale(height if height is not None else sclass.getVehicleHeight(vehicle))

	@staticmethod
	def getPlayerVehicleParams():
		player = BigWorld.player()
		return (
			player.vehicleTypeDescriptor,
			Math.Matrix(player.getOwnVehicleMatrix()),
			Math.Matrix(player.gunRotator.turretMatrix).yaw,
			Math.Matrix(player.gunRotator.gunMatrix).pitch
		)

	@staticmethod
	def getShotAngles(vehicleTypeDescriptor, vehicleMP, targetPosition, adjust = True):
		hullPosition = vehicleTypeDescriptor.chassis['hullPosition']
		turretPosition = vehicleTypeDescriptor.hull['turretPositions'][0]
		gunPosition = vehicleTypeDescriptor.turret['gunPosition']
		shotSpeed = vehicleTypeDescriptor.shot['speed']
		shotGravity = vehicleTypeDescriptor.shot['gravity']
		return BigWorld.wg_getShotAngles(hullPosition + turretPosition, gunPosition, vehicleMP, shotSpeed, shotGravity, 0, 0, targetPosition, adjust)

	@staticmethod
	def getTurretMatrix(vehicleTypeDescriptor, vehicleMatrix, turretYaw):
		hullPosition = vehicleTypeDescriptor.chassis['hullPosition']
		turretPosition = vehicleTypeDescriptor.hull['turretPositions'][0]
		turretMatrix = Math.Matrix()
		turretMatrix.setRotateY(turretYaw)
		turretMatrix.translation = hullPosition + turretPosition
		turretMatrix.postMultiply(vehicleMatrix)
		return turretMatrix

	@staticmethod
	def getGunMatrix(vehicleTypeDescriptor, turretMatrix, gunPitch):
		gunPosition = vehicleTypeDescriptor.turret['gunPosition']
		gunMatrix = Math.Matrix()
		gunMatrix.setRotateX(gunPitch)
		gunMatrix.translation = gunPosition
		gunMatrix.postMultiply(turretMatrix)
		return gunMatrix

	@classmethod
	def getShotRayAndPoint(sclass, vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch):
		turretMatrix = sclass.getTurretMatrix(vehicleTypeDescriptor, vehicleMatrix, turretYaw)
		gunMatrix = sclass.getGunMatrix(vehicleTypeDescriptor, turretMatrix, gunPitch)
		return gunMatrix.applyToAxis(2), gunMatrix.applyToOrigin()

	@classmethod
	def getPlayerShotRayAndPoint(sclass):
		return sclass.getShotRayAndPoint(*sclass.getPlayerVehicleParams())

	@classmethod
	def getVehicleShotParams(sclass, vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch):
		shotSpeed = vehicleTypeDescriptor.shot['speed']
		shotGravity = vehicleTypeDescriptor.shot['gravity']
		shotMaxDistance =  vehicleTypeDescriptor.shot['maxDistance']
		shotRay, shotPoint = sclass.getShotRayAndPoint(vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch)
		shotVector = shotRay.scale(shotSpeed)
		shotGravity = Math.Vector3(0.0, -shotGravity, 0.0)
		return (shotPoint, shotVector, shotGravity, shotMaxDistance)

	@classmethod
	def getPlayerVehicleShotParams(sclass):
		return sclass.getVehicleShotParams(*sclass.getPlayerVehicleParams())
