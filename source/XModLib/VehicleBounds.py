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
from .MathUtils import MathUtils

class VehicleBounds(object):
	@staticmethod
	def getComponentBoundsMatrix(bbox):
		componentBoundsMatrix = MathUtils.getScaleMatrix(bbox[1] - bbox[0])
		componentBoundsMatrix.translation = bbox[0]
		return componentBoundsMatrix

	@staticmethod
	def getUnitBoundingPoints():
		return (
			Math.Vector3(0, 0, 0),
			Math.Vector3(0, 0, 1),
			Math.Vector3(0, 1, 0),
			Math.Vector3(0, 1, 1),
			Math.Vector3(1, 0, 0),
			Math.Vector3(1, 0, 1),
			Math.Vector3(1, 1, 0),
			Math.Vector3(1, 1, 1)
		)

	@classmethod
	def getComponentBoundingPoints(sclass, componentBoundsMatrix, componentMatrixProvider):
		return [Math.Vector4Translation(MathUtils.getMatrixProduct(MathUtils.getMatrixProduct(MathUtils.getTranslationMatrix(unitBoundingPoint), componentBoundsMatrix), componentMatrixProvider)) for unitBoundingPoint in sclass.getUnitBoundingPoints()]

	@staticmethod
	def getBoundsMatrixProvider(boundingPoints):
		min_corner = list(boundingPoints)
		while len(min_corner) > 1:
			min_corner.append(MathUtils.getVector4Combiner(min_corner.pop(0), min_corner.pop(0), 'MIN'))
		min_corner = min_corner.pop(0)
		max_corner = list(boundingPoints)
		while len(max_corner) > 1:
			max_corner.append(MathUtils.getVector4Combiner(max_corner.pop(0), max_corner.pop(0), 'MAX'))
		max_corner = max_corner.pop(0)
		return MathUtils.getVector4MatrixAdaptor(min_corner, MathUtils.getVector4Combiner(max_corner, min_corner, 'SUBTRACT'), 'XYZ_SCALE')

	@classmethod
	def getVehicleBoundsMatrixProvider(sclass, vehicle):
		chassis_offset_matrix = MathUtils.getIdentityMatrix()
		hull_offset_matrix = MathUtils.getTranslationMatrix(vehicle.typeDescriptor.chassis['hullPosition'])
		turret_offset_matrix = MathUtils.getTranslationMatrix(vehicle.typeDescriptor.hull['turretPositions'][0])
		gun_offset_matrix = MathUtils.getTranslationMatrix(vehicle.typeDescriptor.turret['gunPosition'])
		chassis_local_mprov = MathUtils.getMatrixProduct(MathUtils.getIdentityMatrix(), chassis_offset_matrix)
		hull_local_mprov = MathUtils.getMatrixProduct(MathUtils.getIdentityMatrix(), hull_offset_matrix)
		turret_local_mprov = MathUtils.getMatrixProduct(vehicle.appearance.turretMatrix, turret_offset_matrix)
		gun_local_mprov = MathUtils.getMatrixProduct(vehicle.appearance.gunMatrix, gun_offset_matrix)
		chassis_r2v_mprov = MathUtils.getMatrixProduct(chassis_local_mprov, MathUtils.getIdentityMatrix())
		hull_r2v_mprov = MathUtils.getMatrixProduct(hull_local_mprov, chassis_r2v_mprov)
		turret_r2v_mprov = MathUtils.getMatrixProduct(turret_local_mprov, hull_r2v_mprov)
		gun_r2v_mprov = MathUtils.getMatrixProduct(gun_local_mprov, turret_r2v_mprov)
		return MathUtils.getMatrixProduct(
			sclass.getBoundsMatrixProvider(
				sclass.getComponentBoundingPoints(
					sclass.getComponentBoundsMatrix(vehicle.typeDescriptor.chassis['hitTester'].bbox),
					chassis_r2v_mprov
				) + sclass.getComponentBoundingPoints(
					sclass.getComponentBoundsMatrix(vehicle.typeDescriptor.hull['hitTester'].bbox),
					hull_r2v_mprov
				) + sclass.getComponentBoundingPoints(
					sclass.getComponentBoundsMatrix(vehicle.typeDescriptor.turret['hitTester'].bbox),
					turret_r2v_mprov
				) + sclass.getComponentBoundingPoints(
					sclass.getComponentBoundsMatrix(vehicle.typeDescriptor.gun['hitTester'].bbox),
					gun_r2v_mprov
				)
			),
			vehicle.matrix
		)
