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
from .MathUtils import MathUtils
from .AnalyticGeometry import MatrixBoundingBox, MatrixBoundingEllipse

class BoundingScanner(object):
	@classmethod
	def scanTargets(sclass, scanStart, scanStop, entities, scalar=1.0):
		raise NotImplementedError
		return

	@classmethod
	def getScaleMatrix(sclass, scalar=1.0):
		scaleMatrix = MathUtils.getScaleMatrix(Math.Vector3(1.0, 1.0, 1.0).scale(scalar))
		scaleMatrix.postMultiply(MathUtils.getTranslationMatrix(Math.Vector3(-0.5, -0.5, -0.5).scale(scalar - 1.0)))
		return scaleMatrix

	@classmethod
	def scanTarget(sclass, scanStart, scanStop, entities, scalar=1.0):
		targets = sclass.scanTargets(scanStart, scanStop, entities, scalar)
		return targets[0] if len(targets) == 1 else None

	@classmethod
	def getTargets(sclass, filterID=None, filterVehicle=None, maxDistance=720, scalar=1.0, skipPlayer=True):
		scanDir, scanStart = AvatarInputHandler.cameras.getWorldRayAndPoint(*BigWorld.player().inputHandler.ctrl.getAim().offset())
		scanDir.normalise()
		scanStop = scanStart + scanDir * maxDistance
		return sclass.scanTargets(scanStart, scanStop, Colliders.getVisibleVehicles(filterID, filterVehicle, skipPlayer), scalar)

	@classmethod
	def getTarget(sclass, filterID=None, filterVehicle=None, maxDistance=720, scalar=1.0, skipPlayer=True):
		targets = sclass.getTargets(filterID, filterVehicle, maxDistance, scalar, skipPlayer)
		return targets[0] if len(targets) == 1 else None

class BBoxScanner(BoundingScanner):
	@classmethod
	def scanTargets(sclass, scanStart, scanStop, entities, scalar=1.0):
		scaleMatrix = sclass.getScaleMatrix(scalar)
		matrixBoundingBox = MatrixBoundingBox.new()
		def checkEntity(entity):
			matrixBoundingBox.iBounds = Math.MatrixInverse(MathUtils.getMatrixProduct(scaleMatrix, entity.model.bounds))
			return matrixBoundingBox.collisionSegment(scanStart, scanStop)
		return filter(checkEntity, entities)

class BEllipseScanner(BoundingScanner):
	@classmethod
	def scanTargets(sclass, scanStart, scanStop, entities, scalar=1.0):
		scaleMatrix = sclass.getScaleMatrix(scalar)
		matrixBoundingEllipse = MatrixBoundingEllipse.new()
		def checkEntity(entity):
			matrixBoundingEllipse.iBounds = Math.MatrixInverse(MathUtils.getMatrixProduct(scaleMatrix, entity.model.bounds))
			return matrixBoundingEllipse.collisionSegment(scanStart, scanStop)
		return filter(checkEntity, entities)
