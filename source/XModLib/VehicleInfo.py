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
import Vehicle
import items.vehicles

# *************************
# X-Mod Library
# *************************
# Nothing

def isVehicle(entity):
	return isinstance(entity, Vehicle.Vehicle)

def isVisible(vehicleID):
	return BigWorld.entity(vehicleID) is not None

def isTarget(vehicleID):
	target = BigWorld.target()
	return target and target.id == vehicleID

def isAutoAim(vehicleID):
	autoAimVehicle = BigWorld.player().autoAimVehicle
	return autoAimVehicle and autoAimVehicle.id == vehicleID

def isAlive(vehicleID):
	vehicle = BigWorld.entity(vehicleID)
	return vehicle and vehicle.isAlive()

def isPlayer(vehicleID):
	vehicle = BigWorld.entity(vehicleID)
	return vehicle and vehicle.isPlayer

def getSpeed(vehicleID):
	vehicle = BigWorld.entity(vehicleID)
	return vehicle and vehicle.getSpeed()

def getTeam(vehicleID):
	vehicle = BigWorld.entity(vehicleID)
	return vehicle and vehicle.publicInfo['team']

def getLevel(vehicleID):
	vehicle = BigWorld.entity(vehicleID)
	return vehicle and vehicle.typeDescriptor.type.level

def getClass(vehicleID):
	vehicle = BigWorld.entity(vehicleID)
	return vehicle and tuple(vehicle.typeDescriptor.type.tags & items.vehicles.VEHICLE_CLASS_TAGS)[0]

def getPlayerVehicleID():
	return BigWorld.player().playerVehicleID
