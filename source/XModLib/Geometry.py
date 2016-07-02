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
# Nothing

# *************************
# X-Mod Code Library
# *************************
from .MathUtils import MathUtils

class Plane(object):
	@classmethod
	def initBy3Points(sclass, point0, point1, point2):
		normal = (point1 - point0) * (point2 - point0)
		return sclass(point0, normal)

	@classmethod
	def initByPointAnd2Vectors(sclass, point, vector1, vector2):
		normal = vector1 * vector2
		return sclass(point, normal)

	@classmethod
	def initByPointAndNormal(sclass, point, normal):
		return sclass(point, normal)

	@classmethod
	def getXYPlane(sclass):
		return sclass(Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 0.0, 1.0))

	@classmethod
	def getXZPlane(sclass):
		return sclass(Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 1.0, 0.0))

	@classmethod
	def getYZPlane(sclass):
		return sclass(Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(1.0, 0.0, 0.0))

	def __init__(self, point, normal):
		self.point = Math.Vector3(point)
		self.normal = Math.Vector3(normal)
		if not self.normal.lengthSquared:
			raise AssertionError('Zero length normal.')
		self.normal.normalise()
		return

	def isPointOnPlane(self, point):
		return not self.normal.dot(point - self.point)

	def isVectorParallelPlane(self, vector):
		return not self.normal.dot(vector)

	def intersectRay(self, point, vector):
		dot1 = self.normal.dot(vector)
		return point + vector.scale(self.normal.dot(self.point - point) / dot1) if dot1 else None

	def projectPoint(self, point):
		return self.intersectRay(point, self.normal)

	def intersectSegment(self, point0, point1):
		vector = point1 - point0
		result = self.intersectRay(point0, vector)
		return result if result is not None and result.distSqrTo(point0) < vector.lengthSquared > result.distSqrTo(point1) else None

	def isPlaneParallel(self, plane):
		return not (self.normal * plane.normal).lengthSquared

	def intersectPlanes(self, plane1, plane2):
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
		vector = self.normal * plane.normal
		if vector.lengthSquared:
			return self.intersectPlanes(plane, Plane(self.point, vector)), vector
		return None

	def __repr__(self):
		return 'Plane(point={!r}, normal={!r})'.format(self.point, self.normal)

	def __del__(self):
		return

class Parallelogram(object):
	def __init__(self, point0, point1, point2):
		self.point0 = Math.Vector3(point0)
		self.point1 = Math.Vector3(point1)
		self.point2 = Math.Vector3(point2)
		self.updateSubsidiaryAttributes()
		return

	def updateSubsidiaryAttributes(self):
		point0 = self.point0
		point1 = self.point1
		point2 = self.point2
		vector0 = point1 - point0
		vector1 = point2 - point0
		vector2 = vector0 + vector1
		point3 = point0 + vector2
		self.points = point0, point1, point2, point3
		self.center = point0 + vector2.scale(0.5)
		self.plane = Plane.initBy3Points(point0, point1, point2)
		self.basis = MathUtils.getBasisMatrix((vector0, self.plane.normal, vector1))
		return

	def scale(self, scalar):
		self.point0 = self.center + (self.point0 - self.center).scale(scalar)
		self.point1 = self.center + (self.point1 - self.center).scale(scalar)
		self.point2 = self.center + (self.point2 - self.center).scale(scalar)
		self.updateSubsidiaryAttributes()
		return

	def isPointOnParallelogram(self, point):
		vector = MathUtils.expandVectorInBasis(point - self.point0, self.basis)
		return -0.001 <= vector[0] <= +1.001 and -0.001 <= vector[1] <= +0.001 and -0.001 <= vector[2] <= +1.001

	def intersectRay(self, point, vector):
		result = self.plane.intersectRay(point, vector)
		return result if result is not None and self.isPointOnParallelogram(result) else None

	def intersectSegment(self, point0, point1):
		result = self.plane.intersectSegment(point0, point1)
		return result if result is not None and self.isPointOnParallelogram(result) else None

	def __repr__(self):
		return 'Parallelogram(point0={!r}, point1={!r}, point2={!r})'.format(self.point0, self.point1, self.point2)

	def __del__(self):
		return

class BoundingBox(object):
	@classmethod
	def constructBoundingBox(sclass, bounds, heightLimits):
		return sclass(
			Math.Vector3(bounds[0][0], heightLimits[0], bounds[0][1]),
			Math.Vector3(bounds[1][0], heightLimits[0], bounds[0][1]),
			Math.Vector3(bounds[0][0], heightLimits[1], bounds[0][1]),
			Math.Vector3(bounds[0][0], heightLimits[0], bounds[1][1])
		)

	@classmethod
	def getSpaceBoundingBox(sclass):
		vec4 = BigWorld.wg_getSpaceBounds()
		return sclass.constructBoundingBox(((vec4.x, vec4.y), (vec4.z, vec4.w)), (-500.0, 500.0))

	@classmethod
	def getArenaBoundingBox(sclass):
		return sclass.constructBoundingBox(BigWorld.player().arena.arenaType.boundingBox, (-500.0, 500.0))

	@classmethod
	def getUnitBoundingBox(sclass):
		return sclass(
			Math.Vector3(0.0, 0.0, 0.0),
			Math.Vector3(1.0, 0.0, 0.0),
			Math.Vector3(0.0, 1.0, 0.0),
			Math.Vector3(0.0, 0.0, 1.0)
		)

	@classmethod
	def getModelBoundingBox(sclass, model):
		matrix = Math.Matrix(model.bounds)
		return sclass(
			matrix.applyPoint(Math.Vector3(0.0, 0.0, 0.0)),
			matrix.applyPoint(Math.Vector3(1.0, 0.0, 0.0)),
			matrix.applyPoint(Math.Vector3(0.0, 1.0, 0.0)),
			matrix.applyPoint(Math.Vector3(0.0, 0.0, 1.0))
		)

	def __init__(self, point0, point1, point2, point3):
		self.point0 = Math.Vector3(point0)
		self.point1 = Math.Vector3(point1)
		self.point2 = Math.Vector3(point2)
		self.point3 = Math.Vector3(point3)
		self.updateSubsidiaryAttributes()
		return

	def updateSubsidiaryAttributes(self):
		point0 = self.point0
		point1 = self.point1
		point2 = self.point2
		point3 = self.point3
		vector0 = point1 - point0
		vector1 = point2 - point0
		vector2 = point3 - point0
		vector3 = vector0 + vector1
		vector4 = vector0 + vector2
		vector5 = vector1 + vector2
		vector6 = vector2 + vector3
		point4 = point0 + vector3
		point5 = point0 + vector4
		point6 = point0 + vector5
		point7 = point0 + vector6
		center = point0 + vector6.scale(0.5)
		self.points = point0, point1, point2, point3, point4, point5, point6, point7
		self.center = center
		self.radius = max(point0 - center, point1 - center, point2 - center, point3 - center, key=lambda vector: vector.lengthSquared).length
		self.basis = MathUtils.getBasisMatrix((vector0, vector1, vector2))
		self.faces = (
			Parallelogram(point0, point1, point2),
			Parallelogram(point0, point1, point3),
			Parallelogram(point0, point2, point3),
			Parallelogram(point1, point4, point5),
			Parallelogram(point2, point4, point6),
			Parallelogram(point3, point5, point6)
		)
		return

	def scale(self, scalar):
		self.point0 = self.center + (self.point0 - self.center).scale(scalar)
		self.point1 = self.center + (self.point1 - self.center).scale(scalar)
		self.point2 = self.center + (self.point2 - self.center).scale(scalar)
		self.point3 = self.center + (self.point3 - self.center).scale(scalar)
		self.updateSubsidiaryAttributes()
		return

	def applyMatrix(self, matrix):
		self.point0 = matrix.applyPoint(self.point0)
		self.point1 = matrix.applyPoint(self.point1)
		self.point2 = matrix.applyPoint(self.point2)
		self.point3 = matrix.applyPoint(self.point3)
		self.updateSubsidiaryAttributes()
		return

	def isPointInsideBox(self, point):
		vector = MathUtils.expandVectorInBasis(point - self.point0, self.basis)
		return -0.001 <= vector[0] <= +1.001 and -0.001 <= vector[1] <= +1.001 and -0.001 <= vector[2] <= +1.001

	def intersectRay(self, point, vector, single=True):
		result = filter(
			lambda point: point is not None and self.isPointInsideBox(point),
			map(lambda face: face.plane.intersectRay(point, vector), self.faces)
		)
		if single:
			result = min(result, key=lambda point: point.distSqrTo(point0)) if result else None
		return result

	def intersectSegment(self, point0, point1, single=True):
		result = filter(
			lambda point: point is not None and self.isPointInsideBox(point),
			map(lambda face: face.plane.intersectSegment(point0, point1), self.faces)
		)
		if single:
			result = min(result, key=lambda point: point.distSqrTo(point0)) if result else None
		return result

	def projectExternalPointOnBox(self, point):
		for plane in map(lambda face: face.plane, self.faces):
			if plane.intersectSegment(self.center, point):
				point = plane.projectPoint(point)
		return point

	def adjustExternalPointToBox(self, point):
		return self.intersectSegment(self.center, point)

	def intersectRayPreliminaryCheck(self, point, vector):
		radius = self.radius ** 2
		direct = point.distSqrTo(self.center)
		return direct < radius or direct - (self.center - point).dot(vector) ** 2 / vector.lengthSquared < radius

	def intersectSegmentPreliminaryCheck(self, point0, point1):
		radius = self.radius ** 2
		vector0 = point1 - point0
		vector1 = point0 - point1
		direct0 = point0.distSqrTo(self.center)
		direct1 = point1.distSqrTo(self.center)
		return direct0 < radius or direct1 < radius or direct0 - (self.center - point0).dot(vector0) ** 2 / vector0.lengthSquared < radius or direct1 - (self.center - point1).dot(vector1) ** 2 / vector1.lengthSquared < radius

	def intersectRayPrimaryCheck(self, point, vector):
		if not self.intersectRayPreliminaryCheck(point, vector):
			return False
		vertex = min(self.points, key=lambda vertex: vertex.distSqrTo(point))
		for face in self.faces:
			if vertex in face.points and face.intersectRay(point, vector):
				return True
		return False

	def intersectSegmentPrimaryCheck(self, point0, point1):
		if not self.intersectSegmentPreliminaryCheck(point0, point1):
			return False
		vertex0 = min(self.points, key=lambda vertex: vertex.distSqrTo(point0))
		vertex1 = min(self.points, key=lambda vertex: vertex.distSqrTo(point1))
		for face in self.faces:
			if (vertex0 in face.points or vertex1 in face.points) and face.intersectSegment(point0, point1):
				return True
		return False

	def __repr__(self):
		return 'BoundingBox(point0={!r}, point1={!r}, point2={!r}, point3={!r})'.format(self.point0, self.point1, self.point2, self.point3)

	def __del__(self):
		return
