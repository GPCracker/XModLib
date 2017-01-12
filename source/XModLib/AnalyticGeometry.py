# Authors: GPCracker

# *************************
# Python
# *************************
import math
import operator
import itertools

# *************************
# BigWorld
# *************************
import Math
import BigWorld

# *************************
# WoT Client
# *************************
# Nothing

# *************************
# X-Mod Library
# *************************
from . import MathUtils

class Plane(tuple):
	__slots__ = ()

	@classmethod
	def getXYPlane(sclass):
		return sclass(Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 0.0, 1.0))

	@classmethod
	def getXZPlane(sclass):
		return sclass(Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 1.0, 0.0))

	@classmethod
	def getYZPlane(sclass):
		return sclass(Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(1.0, 0.0, 0.0))

	@classmethod
	def newA(sclass, point0, normal0):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 must be an instance of Math.Vector3 class.')
		if not isinstance(normal0, Math.Vector3):
			raise TypeError('normal0 must be an instance of Math.Vector3 class.')
		return sclass(point0, normal0)

	@classmethod
	def newB(sclass, point0, vector0, vector1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 must be an instance of Math.Vector3 class.')
		if not isinstance(vector0, Math.Vector3):
			raise TypeError('vector0 must be an instance of Math.Vector3 class.')
		if not isinstance(vector1, Math.Vector3):
			raise TypeError('vector1 must be an instance of Math.Vector3 class.')
		return sclass(point0, vector0 * vector1)

	@classmethod
	def newC(sclass, point0, point1, point2):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 must be an instance of Math.Vector3 class.')
		if not isinstance(point2, Math.Vector3):
			raise TypeError('point2 must be an instance of Math.Vector3 class.')
		return sclass(point0, (point1 - point0) * (point2 - point0))

	def __new__(sclass, point, normal):
		if not normal.lengthSquared:
			raise RuntimeError('normal must be a vector with non-zero length.')
		return super(Plane, sclass).__new__(sclass, (Math.Vector3(point), MathUtils.getNormalisedVector(normal)))

	point = property(operator.itemgetter(0))
	normal = property(operator.itemgetter(1))

	def __repr__(self):
		return '{}(point={!r}, normal={!r})'.format(self.__class__.__name__, self.point, self.normal)

	def isPointOnPlane(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point must be an instance of Math.Vector3 class.')
		return not self.normal.dot(point - self.point)

	def isVectorParallelPlane(self, vector):
		if not isinstance(vector, Math.Vector3):
			raise TypeError('vector must be an instance of Math.Vector3 class.')
		return not self.normal.dot(vector)

	def intersectRay(self, point, vector):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point must be an instance of Math.Vector3 class.')
		if not isinstance(vector, Math.Vector3):
			raise TypeError('vector must be an instance of Math.Vector3 class.')
		dotnv = self.normal.dot(vector)
		return point + vector.scale(self.normal.dot(self.point - point) / dotnv) if dotnv else None

	def projectPoint(self, point):
		return self.intersectRay(point, self.normal)

	def intersectSegment(self, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 must be an instance of Math.Vector3 class.')
		vector = point1 - point0
		result = self.intersectRay(point0, vector)
		return result if result is not None and result.distSqrTo(point0) <= vector.lengthSquared >= result.distSqrTo(point1) else None

	def isPlaneParallel(self, plane):
		if not isinstance(plane, self.__class__):
			raise TypeError('plane must be an instance of {} class.'.format(self.__class__.__name__))
		return not (self.normal * plane.normal).lengthSquared

	def intersectPlanes(self, plane0, plane1):
		if not isinstance(plane0, self.__class__):
			raise TypeError('plane0 must be an instance of {} class.'.format(self.__class__.__name__))
		if not isinstance(plane1, self.__class__):
			raise TypeError('plane1 must be an instance of {} class.'.format(self.__class__.__name__))
		A = Math.Matrix()
		A.setElement(0, 0, self.normal[0])
		A.setElement(0, 1, self.normal[1])
		A.setElement(0, 2, self.normal[2])
		A.setElement(1, 0, plane1.normal[0])
		A.setElement(1, 1, plane1.normal[1])
		A.setElement(1, 2, plane1.normal[2])
		A.setElement(2, 0, plane2.normal[0])
		A.setElement(2, 1, plane2.normal[1])
		A.setElement(2, 2, plane2.normal[2])
		if A.determinant == 0.0:
			return None
		A.invert()
		B = Math.Matrix()
		B.setElement(0, 0, self.normal.dot(self.point))
		B.setElement(1, 0, plane1.normal.dot(plane1.point))
		B.setElement(2, 0, plane2.normal.dot(plane2.point))
		A.postMultiply(B)
		return Math.Vector3(A.get(0, 0), A.get(1, 0), A.get(2, 0))

	def intersectPlane(self, plane):
		if not isinstance(plane, self.__class__):
			raise TypeError('plane must be an instance of {} class.'.format(self.__class__.__name__))
		vector = self.normal * plane.normal
		return (self.intersectPlanes(plane, self.__class__(self.point, vector)), vector) if vector.lengthSquared else None

class _AxisAlignedBoundingBox(tuple):
	__slots__ = ()

	def __new__(sclass, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 must be an instance of Math.Vector3 class.')
		point0 = Math.Vector3(min([point0.x, point1.x]), min([point0.y, point1.y]), min([point0.z, point1.z]))
		point1 = Math.Vector3(max([point0.x, point1.x]), max([point0.y, point1.y]), max([point0.z, point1.z]))
		if not all((point1 - point0).tuple()):
			raise RuntimeError('BoundingBox must have non-zero volume.')
		return super(_AxisAlignedBoundingBox, sclass).__new__(sclass, (point0, point1))

	point0 = property(operator.itemgetter(0))
	point1 = property(operator.itemgetter(1))

	def __repr__(self):
		return '{}(point0={!r}, point1={!r})'.format(self.__class__.__name__, self.point0, self.point1)

	def _isPointInsideBox(self, point):
		return all(
			self.point0.x <= point.x <= self.point1.x,
			self.point0.y <= point.y <= self.point1.y,
			self.point0.z <= point.z <= self.point1.z
		)

	def _intersectFractions(self, point, vector, within):
		copysign = lambda target, dividend, divider: math.copysign(target, math.copysign(1.0, dividend) * math.copysign(1.0, divider))
		fx0 = (self.point0.x - point.x) / vector.x if vector.x != 0.0 else copysign(float('inf'), self.point0.x - point.x, vector.x)
		fx1 = (self.point1.x - point.x) / vector.x if vector.x != 0.0 else copysign(float('inf'), self.point1.x - point.x, vector.x)
		fy0 = (self.point0.y - point.y) / vector.y if vector.y != 0.0 else copysign(float('inf'), self.point0.y - point.y, vector.y)
		fy1 = (self.point1.y - point.y) / vector.y if vector.y != 0.0 else copysign(float('inf'), self.point1.y - point.y, vector.y)
		fz0 = (self.point0.z - point.z) / vector.z if vector.z != 0.0 else copysign(float('inf'), self.point0.z - point.z, vector.z)
		fz1 = (self.point1.z - point.z) / vector.z if vector.z != 0.0 else copysign(float('inf'), self.point1.z - point.z, vector.z)
		fx, fy, fz = (fx0, fx1), (fy0, fy1), (fz0, fz1)
		frlow, frhigh = max(min(fx), min(fy), min(fz)), min(max(fx), max(fy), max(fz))
		if frlow <= frhigh:
			return tuple(fraction for fraction in (frlow, frhigh) if 0.0 <= fraction <= 1.0) if within else (frlow, frhigh)
		return None

	def _intersectRay(self, point, vector, nearest=True):
		fractions = self._intersectFractions(point, vector, within=False)
		if fractions:
			result = tuple(itertools.imap(lambda fraction: point + vector.scale(fraction), fractions))
			return min(result, key=point.distSqrTo) if nearest else result
		return None

	def _intersectSegment(self, point0, point1, nearest=True):
		vector = point1 - point0
		fractions = self._intersectFractions(point0, vector, within=True)
		if fractions:
			result = tuple(itertools.imap(lambda fraction: point0 + vector.scale(fraction), fractions))
			return min(result, key=point0.distSqrTo) if nearest else result
		return None

	def _collisionRay(self, point, vector):
		return bool(self._intersectFractions(point, vector, within=False))

	def _collisionSegment(self, point0, point1):
		return bool(self._intersectFractions(point0, point1 - point0, within=True))

	def _orthClampPoint(self, point):
		return Math.Vector3(
			min(max(self.point0.x, point.x), self.point1.x),
			min(max(self.point0.y, point.y), self.point1.y),
			min(max(self.point0.z, point.z), self.point1.z)
		)

	def _projClampPoint(self, point):
		return self._intersectSegment(self.point0 + (self.point1 - self.point0).scale(0.5), point) or point

	def isPointInsideBox(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point must be an instance of Math.Vector3 class.')
		return self._isPointInsideBox(point)

	def intersectRay(self, point, vector, nearest=True):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point must be an instance of Math.Vector3 class.')
		if not isinstance(vector, Math.Vector3):
			raise TypeError('vector must be an instance of Math.Vector3 class.')
		return self._intersectRay(point, vector, nearest)

	def intersectSegment(self, point0, point1, nearest=True):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 must be an instance of Math.Vector3 class.')
		return self._intersectSegment(point0, point1, nearest)

	def collisionRay(self, point, vector):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point must be an instance of Math.Vector3 class.')
		if not isinstance(vector, Math.Vector3):
			raise TypeError('vector must be an instance of Math.Vector3 class.')
		return self._collisionRay(point, vector)

	def collisionSegment(self, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 must be an instance of Math.Vector3 class.')
		return self._collisionSegment(point0, point1)

	def orthClampPoint(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point must be an instance of Math.Vector3 class.')
		return self._orthClampPoint(point)

	def projClampPoint(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point must be an instance of Math.Vector3 class.')
		return self._projClampPoint(point)

class AxisAlignedBoundingBox(_AxisAlignedBoundingBox):
	__slots__ = ()

	@classmethod
	def construct(sclass, flatBounds, heightLimits=(-500.0, 500.0)):
		return sclass(
			Math.Vector3(flatBounds[0][0], heightLimits[0], flatBounds[0][1]),
			Math.Vector3(flatBounds[1][0], heightLimits[1], flatBounds[1][1])
		)

	@classmethod
	def getSpaceBoundingBox(sclass):
		bounds = BigWorld.wg_getSpaceBounds().tuple()
		return sclass.construct((bounds[0:2], bounds[2:4]))

	@classmethod
	def getArenaBoundingBox(sclass):
		return sclass.construct(BigWorld.player().arena.arenaType.boundingBox)

class UnitBoundingBox(_AxisAlignedBoundingBox):
	__slots__ = ()

	def __new__(sclass):
		return super(UnitBoundingBox, sclass).__new__(sclass, Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(1.0, 1.0, 1.0))

	def __repr__(self):
		return '{}()'.format(self.__class__.__name__)

class BoundingBoxMatrixAdapter(object):
	__slots__ = ('__weakref__', 'invBounds', 'boundingBox')

	def __init__(self, invBounds=None, boundingBox=None):
		super(BoundingBoxMatrixAdapter, self).__init__()
		self.invBounds = invBounds if invBounds is not None else MathUtils.getIdentityMatrix()
		self.boundingBox = boundingBox if boundingBox is not None else UnitBoundingBox()
		return

	def __repr__(self):
		return '{}(invBounds={!r}, boundingBox={!r})'.format(self.__class__.__name__, self.invBounds, self.boundingBox)

	def isPointInsideBox(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point must be an instance of Math.Vector3 class.')
		return self.boundingBox._isPointInsideBox(Math.Matrix(self.invBounds).applyPoint(point))

	def intersectRay(self, point, vector, nearest=True):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point must be an instance of Math.Vector3 class.')
		if not isinstance(vector, Math.Vector3):
			raise TypeError('vector must be an instance of Math.Vector3 class.')
		srcMatrix = Math.Matrix(self.invBounds)
		result = self.boundingBox._intersectRay(srcMatrix.applyPoint(point), srcMatrix.applyVector(vector), nearest)
		if result is not None:
			resMatrix = MathUtils.getInvertedMatrix(srcMatrix)
			return resMatrix.applyPoint(result) if nearest else tuple(itertools.imap(resMatrix.applyPoint, result))
		return None

	def intersectSegment(self, point0, point1, nearest=True):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 must be an instance of Math.Vector3 class.')
		srcMatrix = Math.Matrix(self.invBounds)
		result = self.boundingBox._intersectSegment(srcMatrix.applyPoint(point0), srcMatrix.applyPoint(point1), nearest)
		if result is not None:
			resMatrix = MathUtils.getInvertedMatrix(srcMatrix)
			return resMatrix.applyPoint(result) if nearest else tuple(itertools.imap(resMatrix.applyPoint, result))
		return None

	def collisionRay(self, point, vector):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point must be an instance of Math.Vector3 class.')
		if not isinstance(vector, Math.Vector3):
			raise TypeError('vector must be an instance of Math.Vector3 class.')
		srcMatrix = Math.Matrix(self.invBounds)
		return self.boundingBox._collisionRay(srcMatrix.applyPoint(point), srcMatrix.applyVector(vector))

	def collisionSegment(self, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 must be an instance of Math.Vector3 class.')
		srcMatrix = Math.Matrix(self.invBounds)
		return self.boundingBox._collisionSegment(srcMatrix.applyPoint(point0), srcMatrix.applyPoint(point1))

	def orthClampPoint(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point must be an instance of Math.Vector3 class.')
		srcMatrix = Math.Matrix(self.invBounds)
		resMatrix = MathUtils.getInvertedMatrix(srcMatrix)
		return resMatrix.applyPoint(self.boundingBox._orthClampPoint(srcMatrix.applyPoint(point)))

	def projClampPoint(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point must be an instance of Math.Vector3 class.')
		srcMatrix = Math.Matrix(self.invBounds)
		resMatrix = MathUtils.getInvertedMatrix(srcMatrix)
		return resMatrix.applyPoint(self.boundingBox._projClampPoint(srcMatrix.applyPoint(point)))

class BoundingSphere(tuple):
	__slots__ = ()

	def __new__(sclass, center, radius):
		if not isinstance(center, Math.Vector3):
			raise TypeError('center must be an instance of Math.Vector3 class.')
		if not isinstance(radius, Math.Vector3):
			raise TypeError('radius must be an instance of Math.Vector3 class.')
		if not radius.lengthSquared:
			raise RuntimeError('BoundingSphere must have non-zero radius.')
		return super(BoundingSphere, sclass).__new__(sclass, (center, radius))

	center = property(operator.itemgetter(0))
	radius = property(operator.itemgetter(1))

	def __repr__(self):
		return '{}(center={!r}, radius={!r})'.format(self.__class__.__name__, self.center, self.radius)

	def _isPointInsideSphere(self, point):
		return point.distSqrTo(self.center) <= self.radius.lengthSquared

	def _collisionRay(self, point, vector):
		return ((point - self.center) * vector).lengthSquared / vector.lengthSquared <= self.radius.lengthSquared

	def _collisionSegment(self, point0, point1):
		vector = point1 - point0
		if self._collisionRay(point0, vector):
			simple = self._isPointInsideSphere(point0), self._isPointInsideSphere(point1)
			return not all(simple) and (any(simple) or (self.center - point0).dot(vector) * (self.center - point1).dot(vector) <= 0.0)
		return False

	def isPointInsideSphere(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point must be an instance of Math.Vector3 class.')
		return self._isPointInsideSphere(point)

	def collisionRay(self, point, vector):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point must be an instance of Math.Vector3 class.')
		if not isinstance(vector, Math.Vector3):
			raise TypeError('vector must be an instance of Math.Vector3 class.')
		return self._collisionRay(point, vector)

	def collisionSegment(self, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 must be an instance of Math.Vector3 class.')
		return self._collisionSegment(point0, point1)

class UnitBoundingSphere(BoundingSphere):
	__slots__ = ()

	def __new__(sclass):
		return super(UnitBoundingSphere, sclass).__new__(sclass, Math.Vector3(0.5, 0.5, 0.5), Math.Vector3(0.5, 0.5, 0.5))

	def __repr__(self):
		return '{}()'.format(self.__class__.__name__)

class BoundingSphereMatrixAdapter(object):
	__slots__ = ('__weakref__', 'invBounds', 'boundingSphere')

	def __init__(self, invBounds=None, boundingSphere=None):
		super(BoundingSphereMatrixAdapter, self).__init__()
		self.invBounds = invBounds if invBounds is not None else MathUtils.getIdentityMatrix()
		self.boundingSphere = boundingSphere if boundingSphere is not None else UnitBoundingBox()
		return

	def __repr__(self):
		return '{}(invBounds={!r}, boundingSphere={!r})'.format(self.__class__.__name__, self.invBounds, self.boundingSphere)

	def isPointInsideSphere(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point must be an instance of Math.Vector3 class.')
		return self.boundingSphere._isPointInsideSphere(Math.Matrix(self.invBounds).applyPoint(point))

	def collisionRay(self, point, vector):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point must be an instance of Math.Vector3 class.')
		if not isinstance(vector, Math.Vector3):
			raise TypeError('vector must be an instance of Math.Vector3 class.')
		srcMatrix = Math.Matrix(self.invBounds)
		return self.boundingSphere._collisionRay(srcMatrix.applyPoint(point), srcMatrix.applyVector(vector))

	def collisionSegment(self, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 must be an instance of Math.Vector3 class.')
		srcMatrix = Math.Matrix(self.invBounds)
		return self.boundingSphere._collisionSegment(srcMatrix.applyPoint(point0), srcMatrix.applyPoint(point1))
