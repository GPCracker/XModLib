# Authors: GPCracker

# *************************
# Python
# *************************
import math

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
# X-Mod Code Library
# *************************
from .VehicleMath import VehicleMath

class BallisticsMath(object):
	@staticmethod
	def getPlayerAimingInfo():
		'''
		dispersionAngle - gun dispersion angle (static gun property),
		aimingStartTime - time when aiming started,
		aimingStartFactor - dispersion factor when aiming started,
		dispersionFactor - gun dispersion angle factor (gun condition),
		aimingTime - aiming exp time.
		'''
		aimingInfo = BigWorld.player()._PlayerAvatar__aimingInfo
		vehicleTypeDescriptor = BigWorld.player().vehicleTypeDescriptor
		dispersionAngle = vehicleTypeDescriptor.gun['shotDispersionAngle']
		aimingStartTime = aimingInfo[0]
		aimingStartFactor = aimingInfo[1]
		dispersionFactor = aimingInfo[2]
		aimingTime = aimingInfo[6]
		return dispersionAngle, aimingStartTime, aimingStartFactor, dispersionFactor, aimingTime

	@staticmethod
	def getAimingFactor(aimingStartTime, aimingStartFactor, dispersionFactor, aimingTime, aimingFactorThreshold = 1.05):
		#Every <aimingTime> seconds dispersion decreases EXP times.
		deltaTime = aimingStartTime - BigWorld.time()
		deltaFactor = aimingStartFactor / dispersionFactor
		if abs(deltaFactor) < aimingFactorThreshold:
			return dispersionFactor
		return aimingStartFactor * math.exp(deltaTime / aimingTime)

	@staticmethod
	def getFullAimingTime(aimingStartFactor, dispersionFactor, aimingTime):
		#Calculates time required for dispersion decreasing <aimingStartFactor>/<shotDispersionFactor> times.
		return aimingTime * math.log(aimingStartFactor / dispersionFactor)

	@staticmethod
	def getRemainingAimingTime(aimingStartTime, fullAimingTime):
		return max(0.0, aimingStartTime + fullAimingTime - BigWorld.time())

	@staticmethod
	def getDispersionAngle(dispersionAngle, aimingFactor):
		return dispersionAngle * aimingFactor

	@staticmethod
	def getDeviation(aimingDistance, dispersionAngle):
		return aimingDistance * dispersionAngle

	@staticmethod
	def getBallisticsInfo(vehicleTypeDescriptor, vehicleMP, targetPoint):
		turretYaw, gunPitch = VehicleMath.getShotAngles(vehicleTypeDescriptor, vehicleMP, targetPoint)
		shotPoint, shotVector, shotGravity, shotMaxDistance = VehicleMath.getVehicleShotParams(vehicleTypeDescriptor, Math.Matrix(vehicleMP), turretYaw, gunPitch)
		flyTime = targetPoint.flatDistTo(shotPoint) / shotVector.flatDistTo(Math.Vector3(0.0, 0.0, 0.0))
		return targetPoint.distTo(shotPoint), (shotVector + shotGravity * flyTime).pitch, flyTime

	@classmethod
	def getPlayerBallisticsInfo(sclass):
		player = BigWorld.player()
		return sclass.getBallisticsInfo(player.vehicleTypeDescriptor, player.getOwnVehicleMatrix(), player.gunRotator.markerInfo[0])
