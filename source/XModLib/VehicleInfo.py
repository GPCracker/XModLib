# Authors: Vladislav Ignatenko <gpcracker@mail.ru>

# ------------ #
#    Python    #
# ------------ #
import types

# -------------- #
#    BigWorld    #
# -------------- #
import BigWorld

# ---------------- #
#    WoT Client    #
# ---------------- #
import Vehicle
import items.vehicles

# ------------------- #
#    X-Mod Library    #
# ------------------- #
# nothing

# -------------------- #
#    Module Content    #
# -------------------- #
def isVehicle(entity):
	if not isinstance(entity, (BigWorld.Entity, types.NoneType)):
		entity = BigWorld.entity(entity)
	return isinstance(entity, Vehicle.Vehicle)

def isVisible(entity):
	if not isinstance(entity, (BigWorld.Entity, types.NoneType)):
		entity = BigWorld.entity(entity)
	return entity is not None

def isTarget(vehicle):
	if not isinstance(vehicle, (BigWorld.Entity, types.NoneType)):
		vehicle = BigWorld.entity(vehicle)
	return vehicle and vehicle is BigWorld.target()

def isAutoAim(vehicle):
	if not isinstance(vehicle, (BigWorld.Entity, types.NoneType)):
		vehicle = BigWorld.entity(vehicle)
	return vehicle and vehicle is BigWorld.player().autoAimVehicle

def isAlive(vehicle):
	if not isinstance(vehicle, (BigWorld.Entity, types.NoneType)):
		vehicle = BigWorld.entity(vehicle)
	return vehicle and vehicle.isAlive()

def isPlayer(vehicle):
	if not isinstance(vehicle, (BigWorld.Entity, types.NoneType)):
		vehicle = BigWorld.entity(vehicle)
	return vehicle and vehicle.isPlayer

def getSpeed(vehicle):
	if not isinstance(vehicle, (BigWorld.Entity, types.NoneType)):
		vehicle = BigWorld.entity(vehicle)
	return vehicle and vehicle.getSpeed()

def getTeam(vehicle):
	if not isinstance(vehicle, (BigWorld.Entity, types.NoneType)):
		vehicle = BigWorld.entity(vehicle)
	return vehicle and vehicle.publicInfo['team']

def getLevel(vehicle):
	if not isinstance(vehicle, (BigWorld.Entity, types.NoneType)):
		vehicle = BigWorld.entity(vehicle)
	return vehicle and vehicle.typeDescriptor.type.level

def getClass(vehicle):
	if not isinstance(vehicle, (BigWorld.Entity, types.NoneType)):
		vehicle = BigWorld.entity(vehicle)
	return vehicle and next(iter(vehicle.typeDescriptor.type.tags & items.vehicles.VEHICLE_CLASS_TAGS))

def getPlayerVehicleID():
	return BigWorld.player().playerVehicleID
