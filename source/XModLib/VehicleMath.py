# Authors: Vladislav Ignatenko <gpcracker@mail.ru>

# ------------ #
#    Python    #
# ------------ #
# nothing

# -------------- #
#    BigWorld    #
# -------------- #
import Math
import BigWorld

# ---------------- #
#    WoT Client    #
# ---------------- #
# nothing

# ------------------- #
#    X-Mod Library    #
# ------------------- #
# nothing

# -------------------- #
#    Module Content    #
# -------------------- #
def getVehicleHeight(vehicle):
	typeDesc = vehicle.typeDescriptor
	hullPositionY = typeDesc.chassis.hullPosition[1]
	turretPositionY = typeDesc.hull.turretPositions[0][1]
	gunPositionY = typeDesc.turret.gunPosition[1]
	hullTopY = hullPositionY + typeDesc.hull.hitTester.bbox[1][1]
	turretTopY = hullPositionY + turretPositionY + typeDesc.turret.hitTester.bbox[1][1]
	gunTopY = hullPositionY + turretPositionY + gunPositionY + typeDesc.gun.hitTester.bbox[1][1]
	hullBottomY = hullPositionY + typeDesc.hull.hitTester.bbox[0][1]
	turretBottomY = hullPositionY + turretPositionY + typeDesc.turret.hitTester.bbox[0][1]
	gunBottomY = hullPositionY + turretPositionY + gunPositionY + typeDesc.gun.hitTester.bbox[0][1]
	return max(hullTopY, turretTopY, gunTopY) - min(hullBottomY, turretBottomY, gunBottomY)

def getVehicleHeightVector(vehicle, height=None):
	return Math.Matrix(vehicle.matrix).applyToAxis(1).scale(height if height is not None else getVehicleHeight(vehicle))

def getPlayerVehicleParams():
	player = BigWorld.player()
	return (
		player.vehicleTypeDescriptor,
		Math.Matrix(player.getOwnVehicleMatrix()),
		Math.Matrix(player.gunRotator.turretMatrix).yaw,
		Math.Matrix(player.gunRotator.gunMatrix).pitch
	)

def getShotAngles(vehicleTypeDescriptor, vehicleMP, targetPosition, adjust=True):
	hullPosition = vehicleTypeDescriptor.chassis.hullPosition
	turretPosition = vehicleTypeDescriptor.hull.turretPositions[0]
	gunPosition = vehicleTypeDescriptor.turret.gunPosition
	shotSpeed = vehicleTypeDescriptor.shot.speed
	shotGravity = vehicleTypeDescriptor.shot.gravity
	return BigWorld.wg_getShotAngles(hullPosition + turretPosition, gunPosition, vehicleMP, shotSpeed, shotGravity, 0, 0, targetPosition, adjust)

def getTurretMatrix(vehicleTypeDescriptor, vehicleMatrix, turretYaw):
	hullPosition = vehicleTypeDescriptor.chassis.hullPosition
	turretPosition = vehicleTypeDescriptor.hull.turretPositions[0]
	turretMatrix = Math.Matrix()
	turretMatrix.setRotateY(turretYaw)
	turretMatrix.translation = hullPosition + turretPosition
	turretMatrix.postMultiply(vehicleMatrix)
	return turretMatrix

def getGunMatrix(vehicleTypeDescriptor, turretMatrix, gunPitch):
	gunPosition = vehicleTypeDescriptor.turret.gunPosition
	gunMatrix = Math.Matrix()
	gunMatrix.setRotateX(gunPitch)
	gunMatrix.translation = gunPosition
	gunMatrix.postMultiply(turretMatrix)
	return gunMatrix

def getShotRayAndPoint(vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch):
	turretMatrix = getTurretMatrix(vehicleTypeDescriptor, vehicleMatrix, turretYaw)
	gunMatrix = getGunMatrix(vehicleTypeDescriptor, turretMatrix, gunPitch)
	return gunMatrix.applyToAxis(2), gunMatrix.applyToOrigin()

def getPlayerShotRayAndPoint():
	return getShotRayAndPoint(*getPlayerVehicleParams())

def getVehicleShotParams(vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch):
	shotSpeed = vehicleTypeDescriptor.shot.speed
	shotGravity = vehicleTypeDescriptor.shot.gravity
	shotMaxDistance =  vehicleTypeDescriptor.shot.maxDistance
	shotRay, shotPoint = getShotRayAndPoint(vehicleTypeDescriptor, vehicleMatrix, turretYaw, gunPitch)
	shotVector = shotRay.scale(shotSpeed)
	shotGravity = Math.Vector3(0.0, -shotGravity, 0.0)
	return (shotPoint, shotVector, shotGravity, shotMaxDistance)

def getPlayerVehicleShotParams():
	return getVehicleShotParams(*getPlayerVehicleParams())
