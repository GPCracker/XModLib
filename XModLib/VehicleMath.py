# Authors: GPCracker

import BigWorld
import Math

class VehicleMath(object):
	@staticmethod
	def getVehicleShotParams(vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch):
		turretOffset = vehicleTypeDescriptor.hull['turretPositions'][0] + vehicleTypeDescriptor.chassis['hullPosition']
		gunOffset = vehicleTypeDescriptor.turret['gunPosition']
		shotSpeed = vehicleTypeDescriptor.shot['speed']
		shotGravity = vehicleTypeDescriptor.shot['gravity']
		shotMaxDistance =  vehicleTypeDescriptor.shot['maxDistance']
		turretWorldMatrix = Math.Matrix()
		turretWorldMatrix.setRotateY(turretYaw)
		turretWorldMatrix.translation = turretOffset
		turretWorldMatrix.postMultiply(Math.Matrix(vehicleMatrix))
		position = turretWorldMatrix.applyPoint(gunOffset)
		gunWorldMatrix = Math.Matrix()
		gunWorldMatrix.setRotateX(gunPitch)
		gunWorldMatrix.postMultiply(turretWorldMatrix)
		vector = gunWorldMatrix.applyVector(Math.Vector3(0, 0, shotSpeed))
		gravity = Math.Vector3(0.0, -shotGravity, 0.0)
		return (position, vector, gravity, shotMaxDistance)

	@staticmethod
	def getPlayerVehicleShotParams():
		player = BigWorld.player()
		return getVehicleShotParams(
			player.vehicleTypeDescriptor,
			player.getOwnVehicleMatrix(),
			Math.Matrix(player.gunRotator.turretMatrix).yaw,
			Math.Matrix(player.gunRotator.gunMatrix).pitch
		)

	@staticmethod
	def getShotAngles(vehicleTypeDescriptor, vehicleMatrix, targetPosition, adjust = True):
		hullPosition = vehicleTypeDescriptor.chassis['hullPosition']
		turretPosition = vehicleTypeDescriptor.hull['turretPositions'][0]
		gunPosition = vehicleTypeDescriptor.turret['gunPosition']
		shotSpeed = vehicleTypeDescriptor.shot['speed']
		shotGravity = vehicleTypeDescriptor.shot['gravity']
		return BigWorld.wg_getShotAngles(hullPosition + turretPosition, gunPosition, vehicleMatrix, shotSpeed, shotGravity, 0, 0, targetPosition, adjust)

	@staticmethod
	def getTurretMatrix(vehicleTypeDescriptor, vehicleMatrix, turretYaw):
		hullPosition = vehicleTypeDescriptor.chassis['hullPosition']
		turretPosition = vehicleTypeDescriptor.hull['turretPositions'][0]
		turretMatrix = Math.Matrix()
		turretMatrix.setRotateYPR(Math.Vector3(turretYaw, 0, 0))
		turretMatrix.translation = hullPosition + turretPosition
		turretMatrix.postMultiply(vehicleMatrix)
		return turretMatrix

	@staticmethod
	def getGunMatrix(vehicleTypeDescriptor, turretMatrix, gunPitch):
		gunPosition = vehicleTypeDescriptor.turret['gunPosition']
		gunMatrix = Math.Matrix()
		gunMatrix.setRotateYPR(Math.Vector3(0, gunPitch, 0))
		gunMatrix.translation = gunPosition
		gunMatrix.postMultiply(turretMatrix)
		return gunMatrix

	@classmethod
	def getShotRayAndPoint(sclass, vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch):
		turretMatrix = sclass.getTurretMatrix(vehicleTypeDescriptor, vehicleMatrix, turretYaw)
		gunMatrix = sclass.getGunMatrix(vehicleTypeDescriptor, turretMatrix, gunPitch)
		return gunMatrix.applyToAxis(2), gunMatrix.applyToOrigin()

	@staticmethod
	def getVehicleHeightVector(vehicle):
		typeDesc = vehicle.typeDescriptor
		hullTopY = typeDesc.chassis['hullPosition'][1] + typeDesc.hull['hitTester'].bbox[1][1]
		turretTopY = typeDesc.chassis['hullPosition'][1] + typeDesc.hull['turretPositions'][0][1] + typeDesc.turret['hitTester'].bbox[1][1]
		gunTopY = typeDesc.chassis['hullPosition'][1] + typeDesc.hull['turretPositions'][0][1] + typeDesc.turret['gunPosition'][1] + typeDesc.gun['hitTester'].bbox[1][1]
		return Math.Matrix(vehicle.matrix).applyToAxis(1).scale(max(hullTopY, turretTopY, gunTopY))
