# Authors: Vladislav Ignatenko <gpcracker@mail.ru>

# ------------ #
#    Python    #
# ------------ #
import functools
import itertools

# -------------- #
#    BigWorld    #
# -------------- #
import Math

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
def _getUnitCornerMatricesIter():
	return itertools.imap(MathUtils.getTranslationMatrix, itertools.starmap(Math.Vector3, itertools.product(xrange(2), repeat=3)))

def _getComponentLocalCornerPointsIter(componentBoundingBox, componentMatrixProvider, unitCornerMatrices):
	def _getComponentStaticBoundsMatrix(componentBoundingBox):
		matrix = MathUtils.getScaleMatrix(componentBoundingBox[1] - componentBoundingBox[0])
		matrix.translation = componentBoundingBox[0]
		return matrix
	def _getComponentLocalBoundsMatrixProvider(componentStaticBoundsMatrix, componentMatrixProvider):
		return MathUtils.getMatrixProduct(componentStaticBoundsMatrix, componentMatrixProvider)
	def _getComponentLocalCornerPointProvider(unitCornerMatrix, componentLocalBoundsMatrixProvider):
		return Math.Vector4Translation(MathUtils.getMatrixProduct(unitCornerMatrix, componentLocalBoundsMatrixProvider))
	localBounds = _getComponentLocalBoundsMatrixProvider(_getComponentStaticBoundsMatrix(componentBoundingBox), componentMatrixProvider)
	getLocalCornerPointProvider = lambda unitCornerMatrix: _getComponentLocalCornerPointProvider(unitCornerMatrix, localBounds)
	return itertools.imap(getLocalCornerPointProvider, unitCornerMatrices)

def _getLocalBoundsMatrixProvider(localCornerPoints):
	minPoint = functools.reduce(lambda pointA, pointB: MathUtils.getVector4Combiner(pointA, pointB, 'MIN'), localCornerPoints)
	maxPoint = functools.reduce(lambda pointA, pointB: MathUtils.getVector4Combiner(pointA, pointB, 'MAX'), localCornerPoints)
	return MathUtils.getVector4MatrixAdaptor(minPoint, MathUtils.getVector4Combiner(maxPoint, minPoint, 'SUBTRACT'), 'XYZ_SCALE')

def getVehicleBoundsMatrixProvider(vehicle):
	# Calculating vehicle component matrices: component offsets.
	chassisOffsetMatrix = MathUtils.getIdentityMatrix()
	hullOffsetMatrix = MathUtils.getTranslationMatrix(vehicle.typeDescriptor.chassis.hullPosition)
	turretOffsetMatrix = MathUtils.getTranslationMatrix(vehicle.typeDescriptor.hull.turretPositions[0])
	gunOffsetMatrix = MathUtils.getTranslationMatrix(vehicle.typeDescriptor.turret.gunPosition)
	# Calculating vehicle component matrices: component transforms.
	chassisTransformMatrixProvider = MathUtils.getMatrixProduct(MathUtils.getIdentityMatrix(), chassisOffsetMatrix)
	hullTransformMatrixProvider = MathUtils.getMatrixProduct(MathUtils.getIdentityMatrix(), hullOffsetMatrix)
	turretTransformMatrixProvider = MathUtils.getMatrixProduct(vehicle.appearance.turretMatrix, turretOffsetMatrix)
	gunTransformMatrixProvider = MathUtils.getMatrixProduct(vehicle.appearance.gunMatrix, gunOffsetMatrix)
	# Calculating vehicle component matrices: component local transforms.
	chassisLocalMatrixProvider = MathUtils.getMatrixProduct(chassisTransformMatrixProvider, MathUtils.getIdentityMatrix())
	hullLocalMatrixProvider = MathUtils.getMatrixProduct(hullTransformMatrixProvider, chassisLocalMatrixProvider)
	turretLocalMatrixProvider = MathUtils.getMatrixProduct(turretTransformMatrixProvider, hullLocalMatrixProvider)
	gunLocalMatrixProvider = MathUtils.getMatrixProduct(gunTransformMatrixProvider, turretLocalMatrixProvider)
	# Getting vehicle component bounding boxes.
	chassisBoundingBox = vehicle.typeDescriptor.chassis.hitTester.bbox
	hullBoundingBox = vehicle.typeDescriptor.hull.hitTester.bbox
	turretBoundingBox = vehicle.typeDescriptor.turret.hitTester.bbox
	gunBoundingBox = vehicle.typeDescriptor.gun.hitTester.bbox
	# Getting vehicle component unit corner matrices.
	unitCornerMatrices = list(_getUnitCornerMatricesIter())
	# Getting vehicle local corner points for all components.
	localCornerPoints = list(itertools.chain(
		_getComponentLocalCornerPointsIter(chassisBoundingBox, chassisLocalMatrixProvider, unitCornerMatrices),
		_getComponentLocalCornerPointsIter(hullBoundingBox, hullLocalMatrixProvider, unitCornerMatrices),
		_getComponentLocalCornerPointsIter(turretBoundingBox, turretLocalMatrixProvider, unitCornerMatrices),
		_getComponentLocalCornerPointsIter(gunBoundingBox, gunLocalMatrixProvider, unitCornerMatrices)
	))
	# Returning vehicle resulting bounds matrix.
	return MathUtils.getMatrixProduct(_getLocalBoundsMatrixProvider(localCornerPoints), vehicle.matrix)
