# Authors: Vladislav Ignatenko <gpcracker@mail.ru>

# ------------ #
#    Python    #
# ------------ #
import math
import itertools
import collections

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
from . import MathUtils

# -------------------- #
#    Module Content    #
# -------------------- #
class Plane(collections.namedtuple('Plane', ('point', 'normal'))):
	__slots__ = ()

	@classmethod
	def getXYPlane(cls):
		return cls(Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 0.0, 1.0))

	@classmethod
	def getXZPlane(cls):
		return cls(Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 1.0, 0.0))

	@classmethod
	def getYZPlane(cls):
		return cls(Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(1.0, 0.0, 0.0))

	@classmethod
	def getPlanePN(cls, point, normal):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		if not isinstance(normal, Math.Vector3):
			raise TypeError('normal argument must be Vector3, not {!s}'.format(type(normal).__name__))
		return cls(point, normal)

	@classmethod
	def getPlanePVV(cls, point, vector0, vector1):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		if not isinstance(vector0, Math.Vector3):
			raise TypeError('vector0 argument must be Vector3, not {!s}'.format(type(vector0).__name__))
		if not isinstance(vector1, Math.Vector3):
			raise TypeError('vector1 argument must be Vector3, not {!s}'.format(type(vector1).__name__))
		return cls(point, vector0 * vector1)

	@classmethod
	def getPlanePPP(cls, point0, point1, point2):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 argument must be Vector3, not {!s}'.format(type(point0).__name__))
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 argument must be Vector3, not {!s}'.format(type(point1).__name__))
		if not isinstance(point2, Math.Vector3):
			raise TypeError('point2 argument must be Vector3, not {!s}'.format(type(point2).__name__))
		return cls(point0, (point1 - point0) * (point2 - point0))

	def __new__(cls, point, normal):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		if not isinstance(normal, Math.Vector3):
			raise TypeError('normal argument must be Vector3, not {!s}'.format(type(normal).__name__))
		if not normal.lengthSquared:
			raise RuntimeError('normal must be a vector with non-zero length')
		return super(Plane, cls).__new__(cls, point, normal)

	def __repr__(self):
		return '{!s}(point={!r}, normal={!r})'.format(self.__class__.__name__, self.point, self.normal)

	def _isPointOnPlane(self, point):
		return not self.normal.dot(point - self.point)

	def _isVectorParallelPlane(self, vector):
		return not self.normal.dot(vector)

	def _intersectFraction(self, point, vector):
		dotnv = self.normal.dot(vector)
		return self.normal.dot(self.point - point) / dotnv if dotnv else None

	def _intersectRay(self, point, vector):
		fraction = self._intersectFraction(point, vector)
		return point + vector.scale(fraction) if fraction is not None else None

	def _intersectSegment(self, point0, point1):
		point, vector = point0, point1 - point0
		fraction = self._intersectFraction(point, vector)
		return point + vector.scale(fraction) if fraction is not None and 0.0 <= fraction <= 1.0 else None

	def _isPlaneParallel(self, plane):
		return not (self.normal * plane.normal).lengthSquared

	def _intersectPlanes(self, plane0, plane1):
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

	def _intersectPlane(self, plane):
		vector = self.normal * plane.normal
		return (self.intersectPlanes(plane, Plane(self.point, vector)), vector) if vector.lengthSquared else None

	def isPointOnPlane(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		return self._isPointOnPlane(point)

	def isVectorParallelPlane(self, vector):
		if not isinstance(vector, Math.Vector3):
			raise TypeError('vector argument must be Vector3, not {!s}'.format(type(vector).__name__))
		return self._isVectorParallelPlane(vector)

	def intersectRay(self, point, vector):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		if not isinstance(vector, Math.Vector3):
			raise TypeError('vector argument must be Vector3, not {!s}'.format(type(vector).__name__))
		return self._intersectRay(point, vector)

	def projectPoint(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		return self._intersectRay(point, self.normal)

	def intersectSegment(self, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 argument must be Vector3, not {!s}'.format(type(point0).__name__))
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 argument must be Vector3, not {!s}'.format(type(point1).__name__))
		return self._intersectSegment(point0, point1)

	def isPlaneParallel(self, plane):
		if not isinstance(plane, Plane):
			raise TypeError('plane argument must be Plane, not {!s}'.format(type(plane).__name__))
		return self._isPlaneParallel(plane)

	def intersectPlanes(self, plane0, plane1):
		if not isinstance(plane0, Plane):
			raise TypeError('plane0 argument must be Plane, not {!s}'.format(type(plane0).__name__))
		if not isinstance(plane1, Plane):
			raise TypeError('plane1 argument must be Plane, not {!s}'.format(type(plane1).__name__))
		self._intersectPlanes(plane0, plane1)

	def intersectPlane(self, plane):
		if not isinstance(plane, Plane):
			raise TypeError('plane argument must be Plane, not {!s}'.format(type(plane).__name__))
		return self._intersectPlane(plane)

class _AxisAlignedBoundingBox(collections.namedtuple('_AxisAlignedBoundingBox', ('point0', 'point1'))):
	__slots__ = ()

	def __new__(cls, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 argument must be Vector3, not {!s}'.format(type(point0).__name__))
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 argument must be Vector3, not {!s}'.format(type(point1).__name__))
		point0 = Math.Vector3(min([point0.x, point1.x]), min([point0.y, point1.y]), min([point0.z, point1.z]))
		point1 = Math.Vector3(max([point0.x, point1.x]), max([point0.y, point1.y]), max([point0.z, point1.z]))
		if not all((point1 - point0).tuple()):
			raise RuntimeError('bounding box must have non-zero volume')
		return super(_AxisAlignedBoundingBox, cls).__new__(cls, point0, point1)

	def __repr__(self):
		return '{!s}(point0={!r}, point1={!r})'.format(self.__class__.__name__, self.point0, self.point1)

	def _isPointInsideBox(self, point):
		return all((
			self.point0.x <= point.x <= self.point1.x,
			self.point0.y <= point.y <= self.point1.y,
			self.point0.z <= point.z <= self.point1.z
		))

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

	def _intersectPoints(self, point, vector, fractions, nearest=True):
		result = tuple(itertools.imap(lambda fraction: point + vector.scale(fraction), fractions))
		return min(result, key=point.distSqrTo) if nearest else result

	def _intersectRay(self, point, vector, nearest=True):
		fractions = self._intersectFractions(point, vector, within=False)
		return self._intersectPoints(point, vector, fractions, nearest=nearest) if fractions else None

	def _intersectSegment(self, point0, point1, nearest=True):
		point, vector = point0, point1 - point0
		fractions = self._intersectFractions(point, vector, within=True)
		return self._intersectPoints(point, vector, fractions, nearest=nearest) if fractions else None

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
		return self._intersectSegment((self.point0 + self.point1).scale(0.5), point) or point

	def isPointInsideBox(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		return self._isPointInsideBox(point)

	def intersectRay(self, point, vector, nearest=True):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		if not isinstance(vector, Math.Vector3):
			raise TypeError('vector argument must be Vector3, not {!s}'.format(type(vector).__name__))
		return self._intersectRay(point, vector, nearest=nearest)

	def intersectSegment(self, point0, point1, nearest=True):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 argument must be Vector3, not {!s}'.format(type(point0).__name__))
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 argument must be Vector3, not {!s}'.format(type(point1).__name__))
		return self._intersectSegment(point0, point1, nearest=nearest)

	def collisionRay(self, point, vector):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		if not isinstance(vector, Math.Vector3):
			raise TypeError('vector argument must be Vector3, not {!s}'.format(type(vector).__name__))
		return self._collisionRay(point, vector)

	def collisionSegment(self, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 argument must be Vector3, not {!s}'.format(type(point0).__name__))
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 argument must be Vector3, not {!s}'.format(type(point1).__name__))
		return self._collisionSegment(point0, point1)

	def orthClampPoint(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		return self._orthClampPoint(point)

	def projClampPoint(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		return self._projClampPoint(point)

class AxisAlignedBoundingBox(_AxisAlignedBoundingBox):
	__slots__ = ()

	@classmethod
	def construct(cls, flatBounds, heightLimits=(-500.0, 500.0)):
		return cls(
			Math.Vector3(flatBounds[0][0], heightLimits[0], flatBounds[0][1]),
			Math.Vector3(flatBounds[1][0], heightLimits[1], flatBounds[1][1])
		)

	@classmethod
	def getSpaceBoundingBox(cls):
		bounds = BigWorld.wg_getSpaceBounds().tuple()
		return cls.construct((bounds[0:2], bounds[2:4]))

	@classmethod
	def getArenaBoundingBox(cls):
		return cls.construct(BigWorld.player().arena.arenaType.boundingBox)

class UnitBoundingBox(_AxisAlignedBoundingBox):
	__slots__ = ()

	def __new__(cls):
		return super(UnitBoundingBox, cls).__new__(cls, Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(1.0, 1.0, 1.0))

	def __repr__(self):
		return '{!s}()'.format(self.__class__.__name__)

class BoundingBoxMatrixAdapter(object):
	__slots__ = ('__weakref__', 'invBounds', 'boundingBox')

	def __init__(self, invBounds=None, boundingBox=None):
		super(BoundingBoxMatrixAdapter, self).__init__()
		self.invBounds = invBounds if invBounds is not None else MathUtils.getIdentityMatrix()
		self.boundingBox = boundingBox if boundingBox is not None else UnitBoundingBox()
		return

	def __repr__(self):
		return '{!s}(invBounds={!r}, boundingBox={!r})'.format(self.__class__.__name__, self.invBounds, self.boundingBox)

	def isPointInsideBox(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		return self.boundingBox._isPointInsideBox(Math.Matrix(self.invBounds).applyPoint(point))

	def intersectRay(self, point, vector, nearest=True):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		if not isinstance(vector, Math.Vector3):
			raise TypeError('vector argument must be Vector3, not {!s}'.format(type(vector).__name__))
		srcMatrix, resMatrix = Math.Matrix(self.invBounds), MathUtils.getInvertedMatrix(self.invBounds)
		result = self.boundingBox._intersectRay(srcMatrix.applyPoint(point), srcMatrix.applyVector(vector), nearest=nearest)
		if result is not None:
			return tuple(itertools.imap(resMatrix.applyPoint, result)) if isinstance(result, (list, tuple)) else resMatrix.applyPoint(result)
		return None

	def intersectSegment(self, point0, point1, nearest=True):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 argument must be Vector3, not {!s}'.format(type(point0).__name__))
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 argument must be Vector3, not {!s}'.format(type(point1).__name__))
		srcMatrix, resMatrix = Math.Matrix(self.invBounds), MathUtils.getInvertedMatrix(self.invBounds)
		result = self.boundingBox._intersectSegment(srcMatrix.applyPoint(point0), srcMatrix.applyPoint(point1), nearest=nearest)
		if result is not None:
			return tuple(itertools.imap(resMatrix.applyPoint, result)) if isinstance(result, (list, tuple)) else resMatrix.applyPoint(result)
		return None

	def collisionRay(self, point, vector):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		if not isinstance(vector, Math.Vector3):
			raise TypeError('vector argument must be Vector3, not {!s}'.format(type(vector).__name__))
		srcMatrix = Math.Matrix(self.invBounds)
		return self.boundingBox._collisionRay(srcMatrix.applyPoint(point), srcMatrix.applyVector(vector))

	def collisionSegment(self, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 argument must be Vector3, not {!s}'.format(type(point0).__name__))
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 argument must be Vector3, not {!s}'.format(type(point1).__name__))
		srcMatrix = Math.Matrix(self.invBounds)
		return self.boundingBox._collisionSegment(srcMatrix.applyPoint(point0), srcMatrix.applyPoint(point1))

	def orthClampPoint(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		return MathUtils.getInvertedMatrix(self.invBounds).applyPoint(self.boundingBox._orthClampPoint(Math.Matrix(self.invBounds).applyPoint(point)))

	def projClampPoint(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		return MathUtils.getInvertedMatrix(self.invBounds).applyPoint(self.boundingBox._projClampPoint(Math.Matrix(self.invBounds).applyPoint(point)))

class BoundingSphere(collections.namedtuple('BoundingSphere', ('center', 'radius'))):
	__slots__ = ()

	def __new__(cls, center, radius):
		if not isinstance(center, Math.Vector3):
			raise TypeError('center argument must be Vector3, not {!s}'.format(type(center).__name__))
		if not isinstance(radius, Math.Vector3):
			raise TypeError('radius argument must be Vector3, not {!s}'.format(type(radius).__name__))
		if not radius.lengthSquared:
			raise RuntimeError('bounding sphere must have non-zero radius')
		return super(BoundingSphere, cls).__new__(cls, center, radius)

	def __repr__(self):
		return '{!s}(center={!r}, radius={!r})'.format(self.__class__.__name__, self.center, self.radius)

	def _isPointInsideSphere(self, point):
		return point.distSqrTo(self.center) <= self.radius.lengthSquared

	def _collisionRay(self, point, vector):
		return ((point - self.center) * vector).lengthSquared / vector.lengthSquared <= self.radius.lengthSquared

	def _collisionSegment(self, point0, point1):
		point, vector = point0, point1 - point0
		if self._collisionRay(point, vector):
			simple = self._isPointInsideSphere(point0), self._isPointInsideSphere(point1)
			return not all(simple) and (any(simple) or (self.center - point0).dot(vector) * (self.center - point1).dot(vector) <= 0.0)
		return False

	def isPointInsideSphere(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		return self._isPointInsideSphere(point)

	def collisionRay(self, point, vector):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		if not isinstance(vector, Math.Vector3):
			raise TypeError('vector argument must be Vector3, not {!s}'.format(type(vector).__name__))
		return self._collisionRay(point, vector)

	def collisionSegment(self, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 argument must be Vector3, not {!s}'.format(type(point0).__name__))
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 argument must be Vector3, not {!s}'.format(type(point1).__name__))
		return self._collisionSegment(point0, point1)

class UnitBoundingSphere(BoundingSphere):
	__slots__ = ()

	def __new__(cls):
		return super(UnitBoundingSphere, cls).__new__(cls, Math.Vector3(0.5, 0.5, 0.5), Math.Vector3(0.5, 0.5, 0.5))

	def __repr__(self):
		return '{!s}()'.format(self.__class__.__name__)

class BoundingSphereMatrixAdapter(object):
	__slots__ = ('__weakref__', 'invBounds', 'boundingSphere')

	def __init__(self, invBounds=None, boundingSphere=None):
		super(BoundingSphereMatrixAdapter, self).__init__()
		self.invBounds = invBounds if invBounds is not None else MathUtils.getIdentityMatrix()
		self.boundingSphere = boundingSphere if boundingSphere is not None else UnitBoundingSphere()
		return

	def __repr__(self):
		return '{!s}(invBounds={!r}, boundingSphere={!r})'.format(self.__class__.__name__, self.invBounds, self.boundingSphere)

	def isPointInsideSphere(self, point):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		return self.boundingSphere._isPointInsideSphere(Math.Matrix(self.invBounds).applyPoint(point))

	def collisionRay(self, point, vector):
		if not isinstance(point, Math.Vector3):
			raise TypeError('point argument must be Vector3, not {!s}'.format(type(point).__name__))
		if not isinstance(vector, Math.Vector3):
			raise TypeError('vector argument must be Vector3, not {!s}'.format(type(vector).__name__))
		srcMatrix = Math.Matrix(self.invBounds)
		return self.boundingSphere._collisionRay(srcMatrix.applyPoint(point), srcMatrix.applyVector(vector))

	def collisionSegment(self, point0, point1):
		if not isinstance(point0, Math.Vector3):
			raise TypeError('point0 argument must be Vector3, not {!s}'.format(type(point0).__name__))
		if not isinstance(point1, Math.Vector3):
			raise TypeError('point1 argument must be Vector3, not {!s}'.format(type(point1).__name__))
		srcMatrix = Math.Matrix(self.invBounds)
		return self.boundingSphere._collisionSegment(srcMatrix.applyPoint(point0), srcMatrix.applyPoint(point1))
