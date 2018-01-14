# Authors: Vladislav Ignatenko <gpcracker@mail.ru>

# ------------ #
#    Python    #
# ------------ #
import math

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
from . import VehicleMath

# -------------------- #
#    Module Content    #
# -------------------- #
def getPlayerAimingInfo():
	'''
	PlayerVehicleTypeDescriptor parameters:
	* staticDispersionAngle - constant dispersion of full aimed not damaged gun (passport gun dispersion).
	PlayerAvatarAimingInfo parameters:
	* aimingStartTime - time when aiming was started, since this moment player stopped bothering his vehicle.
	* aimingStartFactor - dispersion factor at time when aiming was started.
	* dispersionFactor - gun dispersion angle factor (depends on gun condition).
	* dispersionFactorTurretRotation - <NotImplemented> (used by WG scripts to calculate other aiming parameters on client side).
	* dispersionFactorChassisMovement - <NotImplemented> (used by WG scripts to calculate other aiming parameters on client side).
	* dispersionFactorChassisRotation - <NotImplemented> (used by WG scripts to calculate other aiming parameters on client side).
	* expAimingTime - aiming exp time (<aimingFactor> decreases exp times every <expAimingTime> seconds).
	'''
	aimingInfo = getattr(BigWorld.player(), '_PlayerAvatar__aimingInfo', None)
	if aimingInfo is None or aimingInfo[0] == 0.0:
		return None
	aimingStartTime, aimingStartFactor, dispersionFactor, dispersionFactorTurretRotation, dispersionFactorChassisMovement, dispersionFactorChassisRotation, expAimingTime = aimingInfo
	staticDispersionAngle = BigWorld.player().vehicleTypeDescriptor.gun.shotDispersionAngle
	return staticDispersionAngle, aimingStartTime, aimingStartFactor, dispersionFactor, expAimingTime

def getAimingFactor(aimingStartTime, aimingStartFactor, dispersionFactor, expAimingTime, aimingThreshold=1.05):
	# Calculates current aiming factor.
	negElapsedTime = aimingStartTime - BigWorld.time()
	if aimingStartFactor / dispersionFactor >= aimingThreshold:
		return aimingStartFactor * math.exp(negElapsedTime / expAimingTime)
	return dispersionFactor

def getFullAimingTime(aimingStartFactor, dispersionFactor, expAimingTime):
	# Calculates time required for dispersion decreasing <aimingStartFactor>/<gunDispersionFactor> times.
	return expAimingTime * math.log(aimingStartFactor / dispersionFactor)

def getRemainingAimingTime(aimingStartTime, fullAimingTime):
	return max(0.0, aimingStartTime + fullAimingTime - BigWorld.time())

def getDispersionAngle(dispersionAngle, aimingFactor):
	return dispersionAngle * aimingFactor

def getDeviation(dispersionAngle, aimingDistance):
	return dispersionAngle * aimingDistance

def getBallisticsInfo(vehicleTypeDescriptor, vehicleMP, targetPoint):
	turretYaw, gunPitch = VehicleMath.getShotAngles(vehicleTypeDescriptor, vehicleMP, targetPoint)
	shotPoint, shotVector, shotGravity, shotMaxDistance = VehicleMath.getVehicleShotParams(vehicleTypeDescriptor, Math.Matrix(vehicleMP), turretYaw, gunPitch)
	flyTime = targetPoint.flatDistTo(shotPoint) / shotVector.flatDistTo(Math.Vector3(0.0, 0.0, 0.0))
	return targetPoint.distTo(shotPoint), flyTime, shotVector.pitch, (shotVector + shotGravity * flyTime).pitch

def getPlayerBallisticsInfo():
	player = BigWorld.player()
	return getBallisticsInfo(player.vehicleTypeDescriptor, player.getOwnVehicleMatrix(), player.gunRotator.markerInfo[0])
