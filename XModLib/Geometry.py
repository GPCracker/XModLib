# Authors: GPCracker

import Math

class Plane(object):
	@classmethod
	def initBy3Points(sclass, point1, point2, point3):
		normal = (point2 - point1) * (point3 - point1)
		return sclass(point1, normal)

	@classmethod
	def initByPointAnd2Vectors(sclass, point, vector1, vector2):
		normal = vector1 * vector2
		return sclass(point, normal)

	@classmethod
	def initByPointAndNormal(sclass, point, normal):
		return sclass(point, normal)

	@classmethod
	def getXYPlane(sclass):
		return sclass(Math.Vector3(0, 0, 0), Math.Vector3(0, 0, 1))

	@classmethod
	def getXZPlane(sclass):
		return sclass(Math.Vector3(0, 0, 0), Math.Vector3(0, 1, 0))

	@classmethod
	def getYZPlane(sclass):
		return sclass(Math.Vector3(0, 0, 0), Math.Vector3(1, 0, 0))

	def __init__(self, point, normal):
		self.point = Math.Vector3(point)
		self.normal = Math.Vector3(normal)
		self.normal.normalise()
		assert self.normal.length
		return

	def isPointOnPlane(self, point):
		return not self.normal.dot(point - self.point)

	def isVectorParallelPlane(self, vector):
		return not self.normal.dot(vector)

	def intersectRay(self, point, vector):
		dot1 = self.normal.dot(vector)
		dot2 = self.normal.dot(self.point - point)
		return point + vector.scale(dot2 / dot1) if dot1 else None

	def projectPoint(self, point):
		return self.intersectRay(point, self.normal)

	def intersectSegment(self, point1, point2):
		vector = point2 - point1
		point3 = self.intersectRay(point1, vector)
		if point3 is not None:
			return point3 if (point3 - point1).length <= vector.length and (point3 - point2).length <= vector.length else None
		return None

	def isPlaneParallel(self, plane):
		return not (self.normal * plane.normal).length

	def intersectPlane(self, plane):
		vector = self.normal * plane.normal
		vector.normalise()
		if not vector.length:
			return None
		A = Math.Matrix()
		A.setElement(0, 0, self.normal[0])
		A.setElement(0, 1, self.normal[1])
		A.setElement(0, 2, self.normal[2])
		A.setElement(1, 0, plane.normal[0])
		A.setElement(1, 1, plane.normal[1])
		A.setElement(1, 2, plane.normal[2])
		A.setElement(2, 0, vector[0])
		A.setElement(2, 1, vector[1])
		A.setElement(2, 2, vector[2])
		A.invert()
		B = Math.Matrix()
		B.setElement(0, 0, -self.normal.dot(self.point))
		B.setElement(1, 0, -plane.normal.dot(plane.point))
		B.setElement(2, 0, -vector.dot(self.point))
		A.postMultiply(B)
		point = Math.Vector3(A.get(0, 0), A.get(1, 0), A.get(2, 0))
		return (point, vector)

	def __repr__(self):
		return 'Plane(point = {}, normal = {})'.format(repr(self.point), repr(self.normal))

	def __del__(self):
		return

class BoundingBox(object):
	@classmethod
	def getSpaceBoundingBox(sclass):
		vec4 = BigWorld.wg_getSpaceBounds()
		return sclass.constructBoundingBox(((vec4.x, vec4.y), (vec4.z, vec4.w)), (-500.0, 500.0))

	@classmethod
	def getArenaBoundingBox(sclass):
		return sclass.constructBoundingBox(BigWorld.player().arena.arenaType.boundingBox, (-500.0, 500.0))

	@classmethod
	def constructBoundingBox(sclass, bounds, heightLimits):
		planes = [
			Plane(Math.Vector3(bounds[0][0], 0, 0), Math.Vector3(-1, 0, 0)),
			Plane(Math.Vector3(0, 0, bounds[0][1]), Math.Vector3(0, 0, -1)),
			Plane(Math.Vector3(bounds[1][0], 0, 0), Math.Vector3(+1, 0, 0)),
			Plane(Math.Vector3(0, 0, bounds[1][1]), Math.Vector3(0, 0, +1)),
			Plane(Math.Vector3(0, heightLimits[0], 0), Math.Vector3(0, -1, 0)),
			Plane(Math.Vector3(0, heightLimits[1], 0), Math.Vector3(0, +1, 0))
		]
		center = Math.Vector3(bounds[0][0] + (bounds[1][0] - bounds[0][0]) / 2.0, heightLimits[0] + (heightLimits[1] - heightLimits[0]) / 2.0, bounds[0][1] + (bounds[1][1] - bounds[0][1]) / 2.0)
		return sclass(planes, center)

	@classmethod
	def getModelBoundingBox(sclass, model):
		matrix = Math.Matrix(model.bounds)
		planes = map(lambda (point, normal): Plane(matrix.applyPoint(point), matrix.applyVector(normal)), [
			(Math.Vector3(0, 0, 0), Math.Vector3(-1, +0, +0)),
			(Math.Vector3(0, 0, 0), Math.Vector3(+0, -1, +0)),
			(Math.Vector3(0, 0, 0), Math.Vector3(+0, +0, -1)),
			(Math.Vector3(1, 1, 1), Math.Vector3(+1, +0, +0)),
			(Math.Vector3(1, 1, 1), Math.Vector3(+0, +1, +0)),
			(Math.Vector3(1, 1, 1), Math.Vector3(+0, +0, +1))
		])
		center = matrix.applyPoint(Math.Vector3(0.5, 0.5, 0.5))
		return sclass(planes, center)

	def __init__(self, planes, center):
		self.planes = planes
		self.center = center
		return

	def intersectSegment(self, point1, point2):
		dots = []
		for plane in self.planes:
			dot = plane.intersectSegment(point1, point2)
			if dot is not None and all([not testPlane.intersectSegment(self.center, dot) for testPlane in self.planes if testPlane is not plane]):
				dots.append(dot)
		return tuple(dots)

	def isPointInsideBox(self, point):
		return not self.intersectSegment(self.center, point)

	def adjustPointToBox(self, point):
		for plane in self.planes:
			if plane.intersectSegment(self.center, point):
				point = plane.projectPoint(point)
		return point

	def scale(self, scalar):
		for plane in self.planes:
			plane.point = self.center + (plane.point - self.center).scale(scalar)
		return

	def __repr__(self):
		return 'BoundingBox(planes = {}, center = {})'.format(repr(self.planes), repr(self.center))

	def __del__(self):
		return
