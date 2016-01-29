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
import AvatarInputHandler.cameras

# *************************
# X-Mod Code Library
# *************************
from .Colliders import Colliders
from .Geometry import BoundingBox

class BBoxScanner(object):
	@classmethod
	def scanTarget(sclass, scanStart, scanStop, entities, scalar=1.0):
		unitBB = BoundingBox.getUnitBoundingBox()
		unitBB.scale(scalar)
		def scanTransform(entity, scanStart, scanStop):
			matrix = Math.Matrix(Math.MatrixInverse(entity.model.bounds))
			return matrix.applyPoint(scanStart), matrix.applyPoint(scanStop)
		targets = filter(lambda entity: unitBB.intersectSegmentPrimaryCheck(*scanTransform(entity, scanStart, scanStop)), entities)
		return targets[0] if len(targets) == 1 else None

	@classmethod
	def getTarget(sclass, filterID=None, filterVehicle=None, maxDistance=720, scalar=1.0, skipPlayer=True):
		scanDir, scanStart = AvatarInputHandler.cameras.getWorldRayAndPoint(*BigWorld.player().inputHandler.ctrl.getAim().offset())
		scanDir.normalise()
		scanStop = scanStart + scanDir * maxDistance
		return sclass.scanTarget(scanStart, scanStop, Colliders.getVisibleVehicles(filterID, filterVehicle, skipPlayer), scalar)
