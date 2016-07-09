# Authors: GPCracker

# *************************
# Python
# *************************
import math

# *************************
# BigWorld
# *************************
import BigWorld
import Math

# *************************
# WoT Client
# *************************
# Nothing

# *************************
# X-Mod Code Library
# *************************
from .MathUtils import MathUtils

class Plane(object):
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
	def new_a(sclass, point0, normal0):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('"point0" must be an instance of Math.Vector3 class.')
		if not isinstance(normal0, Math.Vector3):
			raise TypeError('"normal0" must be an instance of Math.Vector3 class.')
		return sclass(point0, normal0)

	@classmethod
	def new_b(sclass, point0, vector0, vector1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('"point0" must be an instance of Math.Vector3 class.')
		if not isinstance(vector0, Math.Vector3):
			raise TypeError('"vector0" must be an instance of Math.Vector3 class.')
		if not isinstance(vector1, Math.Vector3):
			raise TypeError('"vector1" must be an instance of Math.Vector3 class.')
		return sclass(point0, vector0 * vector1)

	@classmethod
	def new_c(sclass, point0, point1, point2):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('"point0" must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('"point1" must be an instance of Math.Vector3 class.')
		if not isinstance(point2, Math.Vector3):
			raise TypeError('"point2" must be an instance of Math.Vector3 class.')
		return sclass(point0, (point1 - point0) * (point2 - point0))

	def __init__(self, point, normal):
		self.point = Math.Vector3(point)
		self.normal = Math.Vector3(normal)
		if not self.normal.lengthSquared:
			raise RuntimeError('Normal must be non-zero length.')
		self.normal.normalise()
		return

	def isPointOnPlane(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('"point" must be an instance of Math.Vector3 class.')
		return not self.normal.dot(point - self.point)

	def isVectorParallelPlane(self, vector):
		if not isinstance(vector, Math.Vector3):
			raise TypeError('"vector" must be an instance of Math.Vector3 class.')
		return not self.normal.dot(vector)

	def intersectRay(self, point, vector):
		if not isinstance(point, Math.Vector3):
			raise TypeError('"point" must be an instance of Math.Vector3 class.')
		if not isinstance(vector, Math.Vector3):
			raise TypeError('"vector" must be an instance of Math.Vector3 class.')
		dot1 = self.normal.dot(vector)
		return point + vector.scale(self.normal.dot(self.point - point) / dot1) if dot1 else None

	def projectPoint(self, point):
		return self.intersectRay(point, self.normal)

	def intersectSegment(self, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('"point0" must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('"point1" must be an instance of Math.Vector3 class.')
		vector = point1 - point0
		result = self.intersectRay(point0, vector)
		return result if result is not None and result.distSqrTo(point0) <= vector.lengthSquared >= result.distSqrTo(point1) else None

	def isPlaneParallel(self, plane):
		if not isinstance(plane, Plane):
			raise TypeError('"plane" must be an instance of Plane class.')
		return not (self.normal * plane.normal).lengthSquared

	def intersectPlanes(self, plane0, plane1):
		if not isinstance(plane0, Plane):
			raise TypeError('"plane0" must be an instance of Plane class.')
		if not isinstance(plane1, Plane):
			raise TypeError('"plane1" must be an instance of Plane class.')
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
		if not isinstance(plane, Plane):
			raise TypeError('"plane" must be an instance of Plane class.')
		vector = self.normal * plane.normal
		if vector.lengthSquared:
			return self.intersectPlanes(plane, Plane(self.point, vector)), vector
		return None

	def __repr__(self):
		return 'Plane(point={!r}, normal={!r})'.format(self.point, self.normal)

	def __del__(self):
		return

class BaseBoundingBox(object):
	def __init__(self, point0, point1):
		self._point0 = Math.Vector3(min([point0.x, point1.x]), min([point0.y, point1.y]), min([point0.z, point1.z]))
		self._point1 = Math.Vector3(max([point0.x, point1.x]), max([point0.y, point1.y]), max([point0.z, point1.z]))
		size = self._point1 - self._point0
		if size.x == 0 or size.y == 0 or size.z == 0:
			raise RuntimeError('Box must be non-zero volume.')
		return

	def _isPointInsideBox(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('"point" must be an instance of Math.Vector3 class.')
		return self._point0.x <= point.x <= self._point1.x and self._point0.y <= point.y <= self._point1.y and self._point0.z <= point.z <= self._point1.z

	def _intersectFractions(self, point, vector):
		## Warning!!! ZeroDivizion, 'inf', NaN and other divide shit should be fixed before real usage!
		copysign = lambda target, dividend, divider: math.copysign(target, dividend) * math.copysign(1.0, divider)
		fx0 = (self._point0.x - point.x) / vector.x if vector.x != 0.0 else copysign(float('inf'), self._point0.x - point.x, vector.x)
		fx1 = (self._point1.x - point.x) / vector.x if vector.x != 0.0 else copysign(float('inf'), self._point1.x - point.x, vector.x)
		fy0 = (self._point0.y - point.y) / vector.y if vector.y != 0.0 else copysign(float('inf'), self._point0.y - point.y, vector.y)
		fy1 = (self._point1.y - point.y) / vector.y if vector.y != 0.0 else copysign(float('inf'), self._point1.y - point.y, vector.y)
		fz0 = (self._point0.z - point.z) / vector.z if vector.z != 0.0 else copysign(float('inf'), self._point0.z - point.z, vector.z)
		fz1 = (self._point1.z - point.z) / vector.z if vector.z != 0.0 else copysign(float('inf'), self._point1.z - point.z, vector.z)
		fx, fy, fz = [fx0, fx1], [fy0, fy1], [fz0, fz1]
		fl = max([min(fx), min(fy), min(fz)])
		fh = min([max(fx), max(fy), max(fz)])
		return fl, fh

	def _intersectRay(self, point, vector, nearest=True):
		if not isinstance(point, Math.Vector3):
			raise TypeError('"point" must be an instance of Math.Vector3 class.')
		if not isinstance(vector, Math.Vector3):
			raise TypeError('"vector" must be an instance of Math.Vector3 class.')
		fl, fh = self._intersectFractions(point, vector)
		if fl <= fh:
			result = [point + vector * fl, point + vector * fh]
			return min(result, key=lambda ipoint: ipoint.distSqrTo(point)) if nearest else result
		return None

	def _intersectSegment(self, point0, point1, nearest=True):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('"point0" must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('"point1" must be an instance of Math.Vector3 class.')
		vector = point1 - point0
		fl, fh = self._intersectFractions(point0, vector)
		if fl <= fh:
			result = filter(lambda ipoint: ipoint.distSqrTo(point0) < vector.lengthSquared > ipoint.distSqrTo(point1), [point0 + vector * fl, point0 + vector * fh])
			if result:
				return min(result, key=lambda ipoint: ipoint.distSqrTo(point0)) if nearest else result
		return None

	def _collisionRay(self, point, vector):
		if not isinstance(point, Math.Vector3):
			raise TypeError('"point" must be an instance of Math.Vector3 class.')
		if not isinstance(vector, Math.Vector3):
			raise TypeError('"vector" must be an instance of Math.Vector3 class.')
		fl, fh = self._intersectFractions(point, vector)
		return fl <= fh

	def _collisionSegment(self, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('"point0" must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('"point1" must be an instance of Math.Vector3 class.')
		vector = point1 - point0
		fl, fh = self._intersectFractions(point0, vector)
		return fl <= fh and (0.0 <= fl <= 1.0 or 0.0 <= fh <= 1.0)

	def _orthClampPoint(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('"point" must be an instance of Math.Vector3 class.')
		return Math.Vector3(min(self._point1.x, max(self._point0.x, point.x)), min(self._point1.y, max(self._point0.y, point.y)), min(self._point1.z, max(self._point0.z, point.z)))

	def _projClampPoint(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('"point" must be an instance of Math.Vector3 class.')
		return self._intersectSegment(self._point0 + (self._point1 - self._point0).scale(0.5), point) or point

	def __repr__(self):
		return 'BaseBoundingBox(point0={!r}, point1={!r})'.format(self._point0, self._point1)

	def __del__(self):
		return

class AxisAlignedBoundingBox(BaseBoundingBox):
	@classmethod
	def constructBoundingBox(sclass, bounds, heightLimits):
		return sclass(Math.Vector3(bounds[0][0], heightLimits[0], bounds[0][1]), Math.Vector3(bounds[1][0], heightLimits[1], bounds[1][1]))

	@classmethod
	def getSpaceBoundingBox(sclass):
		spaceBounds = BigWorld.wg_getSpaceBounds()
		return sclass.constructBoundingBox(((vspaceBounds.x, spaceBounds.y), (spaceBounds.z, spaceBounds.w)), (-500.0, 500.0))

	@classmethod
	def getArenaBoundingBox(sclass):
		return sclass.constructBoundingBox(BigWorld.player().arena.arenaType.boundingBox, (-500.0, 500.0))

	@classmethod
	def new(sclass, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('"point0" must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('"point1" must be an instance of Math.Vector3 class.')
		return sclass(point0, point1)

	@property
	def point0(self):
		return self._point0

	@property
	def point1(self):
		return self._point1

	def isPointInsideBox(self, point):
		return self._isPointInsideBox(point)

	def intersectRay(self, point, vector, nearest=True):
		return self._intersectRay(point, vector, nearest)

	def intersectSegment(self, point0, point1, nearest=True):
		return self._intersectSegment(point0, point1, nearest)

	def collisionRay(self, point, vector):
		return self._collisionRay(point, vector)

	def collisionSegment(self, point0, point1):
		return self._collisionSegment(point0, point1)

	def orthClampPoint(self, point):
		return self._orthClampPoint(point)

	def projClampPoint(self, point):
		return self._projClampPoint(point)

	def __repr__(self):
		return 'AxisAlignedBoundingBox(point0={!r}, point1={!r})'.format(self._point0, self._point1)

class UnitBoundingBox(BaseBoundingBox):
	POINT_0 = Math.Vector3(0.0, 0.0, 0.0)
	POINT_1 = Math.Vector3(1.0, 1.0, 1.0)

	def __init__(self):
		super(UnitBoundingBox, self).__init__(self.POINT_0, self.POINT_1)
		return

	def isPointInsideBox(self, point):
		return self._isPointInsideBox(point)

	def intersectRay(self, point, vector, nearest=True):
		return self._intersectRay(point, vector, nearest)

	def intersectSegment(self, point0, point1, nearest=True):
		return self._intersectSegment(point0, point1, nearest)

	def collisionRay(self, point, vector):
		return self._collisionRay(point, vector)

	def collisionSegment(self, point0, point1):
		return self._collisionSegment(point0, point1)

	def orthClampPoint(self, point):
		return self._orthClampPoint(point)

	def projClampPoint(self, point):
		return self._projClampPoint(point)

	def __repr__(self):
		return 'UnitBoundingBox()'

class MatrixBoundingBox(UnitBoundingBox):
	@classmethod
	def new(sclass, iBounds=None):
		return sclass(iBounds if iBounds is not None else MathUtils.getIdentityMatrix())

	def __init__(self, iBounds):
		super(MatrixBoundingBox, self).__init__()
		self.iBounds = iBounds
		return

	def isPointInsideBox(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('"point" must be an instance of Math.Vector3 class.')
		return super(MatrixBoundingBox, self).isPointInsideBox(Math.Matrix(self.iBounds).applyPoint(point))

	def intersectRay(self, point, vector, nearest=True):
		if not isinstance(point, Math.Vector3):
			raise TypeError('"point" must be an instance of Math.Vector3 class.')
		if not isinstance(vector, Math.Vector3):
			raise TypeError('"vector" must be an instance of Math.Vector3 class.')
		iMatrix = Math.Matrix(self.iBounds)
		nMatrix = MathUtils.getInvertedMatrix(iMatrix)
		result = super(MatrixBoundingBox, self).intersectRay(iMatrix.applyPoint(point), iMatrix.applyVector(vector), nearest=nearest)
		if result is not None:
			return nMatrix.applyPoint(result) if nearest else map(nMatrix.applyPoint, result)
		return None

	def intersectSegment(self, point0, point1, nearest=True):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('"point0" must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('"point1" must be an instance of Math.Vector3 class.')
		iMatrix = Math.Matrix(self.iBounds)
		nMatrix = MathUtils.getInvertedMatrix(iMatrix)
		result = super(MatrixBoundingBox, self).intersectSegment(iMatrix.applyPoint(point0), iMatrix.applyPoint(point1), nearest=nearest)
		if result is not None:
			return nMatrix.applyPoint(result) if nearest else map(nMatrix.applyPoint, result)
		return None

	def collisionRay(self, point, vector):
		if not isinstance(point, Math.Vector3):
			raise TypeError('"point" must be an instance of Math.Vector3 class.')
		if not isinstance(vector, Math.Vector3):
			raise TypeError('"vector" must be an instance of Math.Vector3 class.')
		iMatrix = Math.Matrix(self.iBounds)
		return super(MatrixBoundingBox, self).collisionRay(iMatrix.applyPoint(point), iMatrix.applyVector(vector))

	def collisionSegment(self, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('"point0" must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('"point1" must be an instance of Math.Vector3 class.')
		iMatrix = Math.Matrix(self.iBounds)
		return super(MatrixBoundingBox, self).collisionSegment(iMatrix.applyPoint(point0), iMatrix.applyPoint(point1))

	def orthClampPoint(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('"point" must be an instance of Math.Vector3 class.')
		iMatrix = Math.Matrix(self.iBounds)
		nMatrix = MathUtils.getInvertedMatrix(iMatrix)
		return nMatrix.applyPoint(super(MatrixBoundingBox, self).orthClampPoint(iMatrix.applyPoint(point)))

	def projClampPoint(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('"point" must be an instance of Math.Vector3 class.')
		iMatrix = Math.Matrix(self.iBounds)
		nMatrix = MathUtils.getInvertedMatrix(iMatrix)
		return nMatrix.applyPoint(super(MatrixBoundingBox, self).projClampPoint(iMatrix.applyPoint(point)))

	def __repr__(self):
		return 'MatrixBoundingBox(iBounds={!r})'.format(self.iBounds)

class BaseBoundingSphere(object):
	def __init__(self, center, radius):
		self._center = center
		self._radius = radius
		if not self._radius.lengthSquared:
			raise ValueError('Radius must be non-zero length.')
		return

	def _isPointInsideSphere(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('"point" must be an instance of Math.Vector3 class.')
		return point.distSqrTo(self._center) <= self._radius.lengthSquared

	def _collisionRay(self, point, vector):
		if not isinstance(point, Math.Vector3):
			raise TypeError('"point" must be an instance of Math.Vector3 class.')
		if not isinstance(vector, Math.Vector3):
			raise TypeError('"vector" must be an instance of Math.Vector3 class.')
		return ((point - self._center) * vector).lengthSquared / vector.lengthSquared <= self._radius.lengthSquared

	def _collisionSegment(self, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('"point0" must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('"point1" must be an instance of Math.Vector3 class.')
		vector = point1 - point0
		if self._collisionRay(point0, vector):
			simple = self._isPointInsideSphere(point0), self._isPointInsideSphere(point1)
			return not all(simple) and (any(simple) or (self._center - point0).dot(vector) * (self._center - point1).dot(vector) <= 0.0)
		return False

	def __repr__(self):
		return 'BaseBoundingSphere(center={!r}, radius={!r})'.format(self._center, self._radius)

	def __del__(self):
		return

class AxisAlignedBoundingSphere(BaseBoundingSphere):
	@classmethod
	def new(sclass, center, radius):
		if not isinstance(center, Math.Vector3):
			raise TypeError('"center" must be an instance of Math.Vector3 class.')
		if not isinstance(radius, Math.Vector3):
			raise TypeError('"radius" must be an instance of Math.Vector3 class.')
		return sclass(center, radius)

	@property
	def center(self):
		return self._center

	@property
	def radius(self):
		return self._radius

	def isPointInsideSphere(self, point):
		return self._isPointInsideSphere(point)

	def collisionRay(self, point, vector):
		return self._collisionRay(point, vector)

	def collisionSegment(self, point0, point1):
		return self._collisionSegment(point0, point1)

	def __repr__(self):
		return 'AxisAlignedBoundingSphere(center={!r}, radius={!r})'.format(self._center, self._radius)

class UnitBoundingSphere(BaseBoundingSphere):
	CENTER = Math.Vector3(0.5, 0.5, 0.5)
	RADIUS = Math.Vector3(0.5, 0.5, 0.5)

	def __init__(self):
		super(UnitBoundingSphere, self).__init__(self.CENTER, self.RADIUS)
		return

	def isPointInsideSphere(self, point):
		return self._isPointInsideSphere(point)

	def collisionRay(self, point, vector):
		return self._collisionRay(point, vector)

	def collisionSegment(self, point0, point1):
		return self._collisionSegment(point0, point1)

	def __repr__(self):
		return 'UnitBoundingSphere()'

class MatrixBoundingSphere(UnitBoundingSphere):
	@classmethod
	def new(sclass, iBounds=None):
		return sclass(iBounds if iBounds is not None else MathUtils.getIdentityMatrix())

	def __init__(self, iBounds):
		super(MatrixBoundingSphere, self).__init__()
		self.iBounds = iBounds
		return

	def isPointInsideSphere(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('"point" must be an instance of Math.Vector3 class.')
		return super(MatrixBoundingSphere, self).isPointInsideSphere(Math.Matrix(self.iBounds).applyPoint(point))

	def collisionRay(self, point, vector):
		if not isinstance(point, Math.Vector3):
			raise TypeError('"point" must be an instance of Math.Vector3 class.')
		if not isinstance(vector, Math.Vector3):
			raise TypeError('"vector" must be an instance of Math.Vector3 class.')
		iMatrix = Math.Matrix(self.iBounds)
		return super(MatrixBoundingSphere, self).collisionRay(iMatrix.applyPoint(point), iMatrix.applyVector(vector))

	def collisionSegment(self, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('"point0" must be an instance of Math.Vector3 class.')
		if not isinstance(point1, Math.Vector3):
			raise TypeError('"point1" must be an instance of Math.Vector3 class.')
		iMatrix = Math.Matrix(self.iBounds)
		return super(MatrixBoundingSphere, self).collisionSegment(iMatrix.applyPoint(point0), iMatrix.applyPoint(point1))

	def __repr__(self):
		return 'MatrixBoundingSphere(iBounds={!r})'.format(self.iBounds)
