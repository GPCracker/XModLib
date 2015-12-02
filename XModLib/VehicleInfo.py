# Authors: GPCracker

import BigWorld
import items.vehicles

class VehicleInfo(object):
	@staticmethod
	def isVisible(vehicleID):
		return BigWorld.entity(vehicleID) is not None

	@staticmethod
	def isTarget(vehicleID):
		target = BigWorld.target()
		return target and target.id == vehicleID

	@staticmethod
	def isAutoAim(vehicleID):
		autoAimVehicle = BigWorld.player().autoAimVehicle
		return autoAimVehicle and autoAimVehicle.id == vehicleID

	@staticmethod
	def isAlive(vehicleID):
		vehicle = BigWorld.entity(vehicleID)
		return vehicle and vehicle.isAlive()

	@staticmethod
	def isPlayer(vehicleID):
		vehicle = BigWorld.entity(vehicleID)
		return vehicle and vehicle.isPlayer

	@staticmethod
	def getSpeed(vehicleID):
		vehicle = BigWorld.entity(vehicleID)
		return vehicle and vehicle.getSpeed()

	@staticmethod
	def getTeam(vehicleID):
		vehicle = BigWorld.entity(vehicleID)
		return vehicle and vehicle.publicInfo['team']

	@staticmethod
	def getLevel(vehicleID):
		vehicle = BigWorld.entity(vehicleID)
		return vehicle and vehicle.typeDescriptor.type.level

	@staticmethod
	def getClass(vehicleID):
		vehicle = BigWorld.entity(vehicleID)
		return vehicle and tuple(vehicle.typeDescriptor.type.tags & items.vehicles.VEHICLE_CLASS_TAGS)[0]

	@staticmethod
	def getPlayerVehicleID():
		return BigWorld.player().playerVehicleID
