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
	def scanTarget(sclass, scanStart, scanDir, entities, scalar=1.0):
		unitBB = BoundingBox.getUnitBoundingBox()
		unitBB.scale(scalar)
		def scanTransform(entity, scanStart, scanDir):
			matrix = Math.Matrix(Math.MatrixInverse(entity.model.bounds))
			return matrix.applyPoint(scanStart), matrix.applyVector(scanDir)
		targets = filter(lambda entity: unitBB.intersectRayPrimaryCheck(*scanTransform(entity, scanStart, scanDir)), entities)
		return targets[0] if len(targets) == 1 else None

	@classmethod
	def getTarget(sclass, filterID=None, filterVehicle=None, scalar=1.0):
		scanDir, scanStart = AvatarInputHandler.cameras.getWorldRayAndPoint(*BigWorld.player().inputHandler.ctrl.getAim().offset())
		scanDir.normalise()
		return sclass.scanTarget(scanStart, scanDir, Colliders.getVisibleVehicles(filterID, filterVehicle), scalar)
