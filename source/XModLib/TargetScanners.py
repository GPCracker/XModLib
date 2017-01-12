# Authors: GPCracker

# *************************
# Python
# *************************
import itertools

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
from . import MathUtils
from . import VehicleBounds
from . import CollisionUtils
from . import AnalyticGeometry

class _TargetScanner(object):
	__slots__ = ('__weakref__', )

	@staticmethod
	def _getScanRayAndPoint(maxDistance):
		scanDir, scanStart = AvatarInputHandler.cameras.getWorldRayAndPoint(*BigWorld.player().inputHandler.ctrl._aimOffset)
		scanStop = scanStart + MathUtils.getNormalisedVector(scanDir).scale(maxDistance)
		return scanStart, scanStop

class XRayScanner(_TargetScanner):
	__slots__ = ()

	def scanTarget(self, scanStart, scanStop, entities, skipGun=False):
		scanResult = CollisionUtils.collideVehicles(entities, scanStart, scanStop, skipGun)
		return scanResult[1] if scanResult is not None else None

	def getTarget(self, filterID=None, filterVehicle=None, maxDistance=720.0, skipGun=False, skipPlayer=True, entities=None):
		scanStart, scanStop = self._getScanRayAndPoint(maxDistance)
		if entities is None:
			entities = CollisionUtils.getVisibleVehicles(filterID, filterVehicle, skipPlayer)
		return self.scanTarget(scanStart, scanStop, entities, skipGun)

class _BoundingScanner(_TargetScanner):
	__slots__ = ()

	@staticmethod
	def _getVehicleBounds(entity):
		return getattr(entity, 'collisionBounds', None) or VehicleBounds.getVehicleBoundsMatrixProvider(entity)

	@staticmethod
	def _getScaleMatrix(scalar=1.0):
		scaleMatrix = MathUtils.getScaleMatrix(Math.Vector3(1.0, 1.0, 1.0).scale(scalar))
		scaleMatrix.postMultiply(MathUtils.getTranslationMatrix(Math.Vector3(-0.5, -0.5, -0.5).scale(scalar - 1.0)))
		return scaleMatrix

	def scanTargets(self, scanStart, scanStop, entities, scalar=1.0):
		raise NotImplementedError
		return

	def scanTarget(self, scanStart, scanStop, entities, scalar=1.0):
		targets = self.scanTargets(scanStart, scanStop, entities, scalar)
		return targets[0] if len(targets) == 1 else None

	def getTargets(self, filterID=None, filterVehicle=None, maxDistance=720.0, scalar=1.0, skipPlayer=True, entities=None):
		scanStart, scanStop = self._getScanRayAndPoint(maxDistance)
		if entities is None:
			entities = CollisionUtils.getVisibleVehicles(filterID, filterVehicle, skipPlayer)
		return self.scanTargets(scanStart, scanStop, entities, scalar)

	def getTarget(self, filterID=None, filterVehicle=None, maxDistance=720.0, scalar=1.0, skipPlayer=True, entities=None):
		targets = self.getTargets(filterID, filterVehicle, maxDistance, scalar, skipPlayer, entities)
		return targets[0] if len(targets) == 1 else None

class BBoxScanner(_BoundingScanner):
	__slots__ = ()

	def scanTargets(self, scanStart, scanStop, entities, scalar=1.0):
		scaleMatrix = self._getScaleMatrix(scalar)
		matrixAdapter = AnalyticGeometry.BoundingBoxMatrixAdapter()
		def checkEntity(entity):
			matrixAdapter.invBounds = Math.MatrixInverse(MathUtils.getMatrixProduct(scaleMatrix, self._getVehicleBounds(entity)))
			return matrixAdapter.collisionSegment(scanStart, scanStop)
		return list(itertools.ifilter(checkEntity, entities))

class BEllipseScanner(_BoundingScanner):
	__slots__ = ()

	def scanTargets(self, scanStart, scanStop, entities, scalar=1.0):
		scaleMatrix = self._getScaleMatrix(scalar)
		matrixAdapter = AnalyticGeometry.BoundingSphereMatrixAdapter()
		def checkEntity(entity):
			matrixAdapter.invBounds = Math.MatrixInverse(MathUtils.getMatrixProduct(scaleMatrix, self._getVehicleBounds(entity)))
			return matrixAdapter.collisionSegment(scanStart, scanStop)
		return list(itertools.ifilter(checkEntity, entities))
