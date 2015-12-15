# Authors: GPCracker

# *************************
# Python
# *************************
# Nothing

# *************************
# BigWorld
# *************************
import Math

# *************************
# WoT Client
# *************************
# Nothing

# *************************
# X-Mod Code Library
# *************************
# Nothing

class ExtraMath(object):
	@staticmethod
	def rotationMatrix(yaw, pitch, roll):
		result = Math.Matrix()
		result.setRotateYPR((yaw, pitch, roll))
		return result

	@staticmethod
	def normalisedVector(vector):
		return vector.scale(1.0 / vector.length)

	@staticmethod
	def getBasisMatrix(basis):
		matrix = Math.Matrix()
		matrix.setElement(0, 0, basis[0][0])
		matrix.setElement(1, 0, basis[0][1])
		matrix.setElement(2, 0, basis[0][2])
		matrix.setElement(0, 1, basis[1][0])
		matrix.setElement(1, 1, basis[1][1])
		matrix.setElement(2, 1, basis[1][2])
		matrix.setElement(0, 2, basis[2][0])
		matrix.setElement(1, 2, basis[2][1])
		matrix.setElement(2, 2, basis[2][2])
		if matrix.determinant != 0.0:
			matrix.invert()
			return matrix
		return None

	@classmethod
	def expandVectorInBasis(sclass, vector, basis):
		if isinstance(basis, (list, tuple)):
			basis = sclass.getBasisMatrix(basis)
		matrix = Math.Matrix()
		matrix.setElement(0, 0, vector[0])
		matrix.setElement(1, 0, vector[1])
		matrix.setElement(2, 0, vector[2])
		matrix.preMultiply(basis)
		return Math.Vector3(matrix.get(0, 0), matrix.get(1, 0), matrix.get(2, 0))
