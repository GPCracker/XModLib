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
from . import VehicleInfo
from . import VehicleBounds
from . import CollisionUtils
from . import AnalyticGeometry

def getCollidableEntities(filterID=None, filterVehicle=None, skipPlayer=True):
	return CollisionUtils.getVisibleVehicles(filterID, filterVehicle, skipPlayer)

class _TargetScanner(object):
	__slots__ = ('__weakref__', 'filterID', 'filterVehicle')

	def __init__(self, filterID=None, filterVehicle=None):
		super(_TargetScanner, self).__init__()
		self.filterID = filterID
		self.filterVehicle = filterVehicle
		return

	def __repr__(self):
		return '{}(filterID={!r}, filterVehicle={!r})'.format(self.__class__.__name__, self.filterID, self.filterVehicle)

class StandardScanner(_TargetScanner):
	__slots__ = ()

	def getTarget(self):
		target = BigWorld.target()
		if VehicleInfo.isVehicle(target):
			if self.filterID is None or self.filterID(target.id):
				if self.filterVehicle is None or self.filterVehicle(target):
					return target
		return None

class _AdvancedScanner(_TargetScanner):
	__slots__ = ('maxDistance', 'skipPlayer')

	def __init__(self, filterID=None, filterVehicle=None, maxDistance=720.0, skipPlayer=True):
		super(_AdvancedScanner, self).__init__(filterID, filterVehicle)
		self.maxDistance = maxDistance
		self.skipPlayer = skipPlayer
		return

	def __repr__(self):
		return '{}(filterID={!r}, filterVehicle={!r}, maxDistance={!r}, skipPlayer={!r})'.format(self.__class__.__name__, self.filterID, self.filterVehicle, self.maxDistance, self.skipPlayer)

	def _getScanRayAndPoint(self):
		scanDir, scanStart = AvatarInputHandler.cameras.getWorldRayAndPoint(*BigWorld.player().inputHandler.ctrl._aimOffset)
		scanStop = scanStart + MathUtils.getNormalisedVector(scanDir).scale(self.maxDistance)
		return scanStart, scanStop

	def _getCollidableEntities(self):
		return getCollidableEntities(self.filterID, self.filterVehicle, self.skipPlayer)

class XRayScanner(_AdvancedScanner):
	__slots__ = ('skipGun', )

	def __init__(self, filterID=None, filterVehicle=None, maxDistance=720.0, skipGun=False, skipPlayer=True):
		super(XRayScanner, self).__init__(filterID, filterVehicle, maxDistance, skipPlayer)
		self.skipGun = skipGun
		return

	def __repr__(self):
		return '{}(filterID={!r}, filterVehicle={!r}, maxDistance={!r}, skipGun={!r}, skipPlayer={!r})'.format(self.__class__.__name__, self.filterID, self.filterVehicle, self.maxDistance, self.skipGun, self.skipPlayer)

	def _scanTarget(self, scanStart, scanStop, entities):
		scanResult = CollisionUtils.collideVehicles(entities, scanStart, scanStop, self.skipGun)
		return scanResult[1] if scanResult is not None else None

	def getTarget(self, entities=None):
		scanStart, scanStop = self._getScanRayAndPoint()
		if entities is None:
			entities = self._getCollidableEntities()
		return self._scanTarget(scanStart, scanStop, entities)

class _BoundingScanner(_AdvancedScanner):
	__slots__ = ('boundsScalar', )

	@staticmethod
	def _getVehicleBounds(entity):
		return getattr(entity, 'collisionBounds', None) or VehicleBounds.getVehicleBoundsMatrixProvider(entity)

	def __init__(self, filterID=None, filterVehicle=None, maxDistance=720.0, boundsScalar=1.0, skipPlayer=True):
		super(_BoundingScanner, self).__init__(filterID, filterVehicle, maxDistance, skipPlayer)
		self.boundsScalar = boundsScalar
		return

	def __repr__(self):
		return '{}(filterID={!r}, filterVehicle={!r}, maxDistance={!r}, boundsScalar={!r}, skipPlayer={!r})'.format(self.__class__.__name__, self.filterID, self.filterVehicle, self.maxDistance, self.boundsScalar, self.skipPlayer)

	def _getScaleMatrix(self):
		scaleMatrix = MathUtils.getScaleMatrix(Math.Vector3(1.0, 1.0, 1.0).scale(self.boundsScalar))
		scaleMatrix.postMultiply(MathUtils.getTranslationMatrix(Math.Vector3(-0.5, -0.5, -0.5).scale(self.boundsScalar - 1.0)))
		return scaleMatrix

	def _scanTargets(self, scanStart, scanStop, entities):
		raise NotImplementedError
		return

	def _scanTarget(self, scanStart, scanStop, entities):
		targets = self._scanTargets(scanStart, scanStop, entities)
		return targets[0] if len(targets) == 1 else None

	def getTargets(self, entities=None):
		scanStart, scanStop = self._getScanRayAndPoint()
		if entities is None:
			entities = self._getCollidableEntities()
		return self._scanTargets(scanStart, scanStop, entities)

	def getTarget(self, entities=None):
		scanStart, scanStop = self._getScanRayAndPoint()
		if entities is None:
			entities = self._getCollidableEntities()
		return self._scanTarget(scanStart, scanStop, entities)

class BBoxScanner(_BoundingScanner):
	__slots__ = ()

	def _scanTargets(self, scanStart, scanStop, entities):
		scaleMatrix = self._getScaleMatrix()
		matrixAdapter = AnalyticGeometry.BoundingBoxMatrixAdapter()
		def checkEntity(entity):
			matrixAdapter.invBounds = Math.MatrixInverse(MathUtils.getMatrixProduct(scaleMatrix, self._getVehicleBounds(entity)))
			return matrixAdapter.collisionSegment(scanStart, scanStop)
		return list(itertools.ifilter(checkEntity, entities))

class BEllipseScanner(_BoundingScanner):
	__slots__ = ()

	def _scanTargets(self, scanStart, scanStop, entities):
		scaleMatrix = self._getScaleMatrix()
		matrixAdapter = AnalyticGeometry.BoundingSphereMatrixAdapter()
		def checkEntity(entity):
			matrixAdapter.invBounds = Math.MatrixInverse(MathUtils.getMatrixProduct(scaleMatrix, self._getVehicleBounds(entity)))
			return matrixAdapter.collisionSegment(scanStart, scanStop)
		return list(itertools.ifilter(checkEntity, entities))
