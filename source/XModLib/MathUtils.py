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
# X-Mod Library
# *************************
# Nothing

def getRotationMatrix(ypr):
	result = Math.Matrix()
	result.setRotateYPR(ypr)
	return result

def getScaleMatrix(scales):
	result = Math.Matrix()
	result.setScale(scales)
	return result

def getTranslationMatrix(translation):
	result = Math.Matrix()
	result.setTranslate(translation)
	return result

def getIdentityMatrix():
	result = Math.Matrix()
	result.setIdentity()
	return result

def getInvertedMatrix(matrix):
	result = Math.Matrix(matrix)
	result.invert()
	return result

def getMatrixProduct(matrixProviderA, matrixProviderB):
	result = Math.MatrixProduct()
	result.a = matrixProviderA
	result.b = matrixProviderB
	return result

def getCombinedMatrixProvider(translationMatrixProvider, rotationMatrixProvider):
	result = Math.WGCombinedMP()
	result.translationSrc = translationMatrixProvider
	result.rotationSrc = rotationMatrixProvider
	return result

def getVector4Combiner(vector4ProviderA, vector4ProviderB, function):
	result = Math.Vector4Combiner()
	result.a = vector4ProviderA
	result.b = vector4ProviderB
	result.fn = function
	return result

def getVector4MatrixAdaptor(position, source, style):
	result = Math.Vector4MatrixAdaptor()
	result.position = position
	result.source = source
	result.style = style
	return result

def getNormalisedVector(vector):
	return vector.scale(1.0 / vector.length)

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

def expandVectorInBasis(vector, basis):
	if isinstance(basis, (list, tuple)):
		basis = getBasisMatrix(basis)
	matrix = Math.Matrix()
	matrix.setElement(0, 0, vector[0])
	matrix.setElement(1, 0, vector[1])
	matrix.setElement(2, 0, vector[2])
	matrix.preMultiply(basis)
	return Math.Vector3(matrix.get(0, 0), matrix.get(1, 0), matrix.get(2, 0))
