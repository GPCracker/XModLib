# Authors: GPCracker

import BigWorld

class Colliders(object):
	@staticmethod
	def collideStatic(startPoint, endPoint, collisionFlags = 128):
		collisionPoints = BigWorld.wg_collideSegment(BigWorld.player().spaceID, startPoint, endPoint, collisionFlags)
		return collisionPoints[0] if collisionPoints is not None else None
