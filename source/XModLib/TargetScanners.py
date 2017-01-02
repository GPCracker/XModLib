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
# X-Mod Library
# *************************
from .Colliders import Colliders
from .MathUtils import MathUtils
from .VehicleBounds import VehicleBounds
from .AnalyticGeometry import MatrixBoundingBox, MatrixBoundingEllipse

class XRayScanner(object):
	@classmethod
	def scanTarget(sclass, scanStart, scanStop, entities, skipGun=False):
		scanResult = Colliders.collideVehicles(entities, scanStart, scanStop, skipGun)
		return scanResult[1] if scanResult is not None else None

	@classmethod
	def getTarget(sclass, filterID=None, filterVehicle=None, maxDistance=720.0, skipGun=False, skipPlayer=True, entities=None):
		scanDir, scanStart = AvatarInputHandler.cameras.getWorldRayAndPoint(*BigWorld.player().inputHandler.ctrl._aimOffset)
		scanDir.normalise()
		scanStop = scanStart + scanDir * maxDistance
		return sclass.scanTarget(
			scanStart,
			scanStop,
			Colliders.getVisibleVehicles(filterID, filterVehicle, skipPlayer) if entities is None else entities,
			skipGun
		)

class BoundingScanner(object):
	@staticmethod
	def getVehicleBounds(entity):
		return getattr(entity, 'collisionBounds', None) or VehicleBounds.getVehicleBoundsMatrixProvider(entity)

	@staticmethod
	def getScaleMatrix(scalar=1.0):
		scaleMatrix = MathUtils.getScaleMatrix(Math.Vector3(1.0, 1.0, 1.0).scale(scalar))
		scaleMatrix.postMultiply(MathUtils.getTranslationMatrix(Math.Vector3(-0.5, -0.5, -0.5).scale(scalar - 1.0)))
		return scaleMatrix

	@classmethod
	def scanTargets(sclass, scanStart, scanStop, entities, scalar=1.0):
		raise NotImplementedError
		return

	@classmethod
	def scanTarget(sclass, scanStart, scanStop, entities, scalar=1.0):
		targets = sclass.scanTargets(scanStart, scanStop, entities, scalar)
		return targets[0] if len(targets) == 1 else None

	@classmethod
	def getTargets(sclass, filterID=None, filterVehicle=None, maxDistance=720.0, scalar=1.0, skipPlayer=True, entities=None):
		scanDir, scanStart = AvatarInputHandler.cameras.getWorldRayAndPoint(*BigWorld.player().inputHandler.ctrl._aimOffset)
		scanDir.normalise()
		scanStop = scanStart + scanDir * maxDistance
		return sclass.scanTargets(
			scanStart,
			scanStop,
			Colliders.getVisibleVehicles(filterID, filterVehicle, skipPlayer) if entities is None else entities,
			scalar
		)

	@classmethod
	def getTarget(sclass, filterID=None, filterVehicle=None, maxDistance=720.0, scalar=1.0, skipPlayer=True, entities=None):
		targets = sclass.getTargets(filterID, filterVehicle, maxDistance, scalar, skipPlayer, entities)
		return targets[0] if len(targets) == 1 else None

class BBoxScanner(BoundingScanner):
	@classmethod
	def scanTargets(sclass, scanStart, scanStop, entities, scalar=1.0):
		scaleMatrix = sclass.getScaleMatrix(scalar)
		matrixBoundingBox = MatrixBoundingBox.new()
		def checkEntity(entity):
			matrixBoundingBox.iBounds = Math.MatrixInverse(MathUtils.getMatrixProduct(scaleMatrix, sclass.getVehicleBounds(entity)))
			return matrixBoundingBox.collisionSegment(scanStart, scanStop)
		return filter(checkEntity, entities)

class BEllipseScanner(BoundingScanner):
	@classmethod
	def scanTargets(sclass, scanStart, scanStop, entities, scalar=1.0):
		scaleMatrix = sclass.getScaleMatrix(scalar)
		matrixBoundingEllipse = MatrixBoundingEllipse.new()
		def checkEntity(entity):
			matrixBoundingEllipse.iBounds = Math.MatrixInverse(MathUtils.getMatrixProduct(scaleMatrix, sclass.getVehicleBounds(entity)))
			return matrixBoundingEllipse.collisionSegment(scanStart, scanStop)
		return filter(checkEntity, entities)
