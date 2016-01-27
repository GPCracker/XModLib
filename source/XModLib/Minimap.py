# Authors: GPCracker

# *************************
# Python
# *************************
# Nothing

# *************************
# BigWorld
# *************************
# Nothing

# *************************
# WoT Client
# *************************
# Nothing

# *************************
# X-Mod Code Library
# *************************
from .AppLoader import AppLoader

class MinimapEntry(object):
	@staticmethod
	def getMinimapOwnUI():
		return AppLoader.getBattleApp().minimap._Minimap__ownUI

	def __init__(self, matrixProvider, zIndex):
		self.__handle = self.getMinimapOwnUI().addEntry(matrixProvider, zIndex)
		return

	@property
	def handle(self):
		return self.__handle

	def invoke(self, funcName, argsList = None):
		return self.getMinimapOwnUI().entryInvoke(self.__handle, (funcName, argsList))

	def setMatrixProvider(self, matrixProvider):
		return self.getMinimapOwnUI().entrySetMatrix(self.__handle, matrixProvider)

	def __del__(self):
		self.getMinimapOwnUI().delEntry(self.__handle)
		return

class MinimapEntryManager(dict):
	def __init__(self, *args, **kwargs):
		super(MinimapEntryManager, self).__init__(*args, **kwargs)
		return

	def createEntry(self, key, matrixProvider, zIndex):
		minimapEntry = MinimapEntry(matrixProvider, zIndex)
		self[key] = minimapEntry
		return minimapEntry

	def addEntry(self, key, minimapEntry):
		self[key] = minimapEntry
		return minimapEntry

	def delEntry(self, key):
		minimapEntry = self[key]
		del self[key]
		return minimapEntry

	def getEntry(self, key):
		return self.get(key, None)

	def hasEntry(self, key):
		return self.getEntry(key) is not None

	def __repr__(self):
		return 'MinimapEntryManager({})'.format(super(MinimapEntryManager, self).__repr__())
