# Authors: GPCracker

# *************************
# Python
# *************************
import functools
import weakref

# *************************
# BigWorld
# *************************
import BigWorld

# *************************
# WoT Client
# *************************
# Nothing

# *************************
# X-Mod Code Library
# *************************
# Nothing

class Callback(object):
	@staticmethod
	def getMethodProxy(method):
		return functools.partial(weakref.proxy(method.im_func), weakref.proxy(method.im_self))

	@staticmethod
	def getPartial(function, *args, **kwargs):
		return functools.partial(function, *args, **kwargs)

	@staticmethod
	def getProxy(object):
		return weakref.proxy(object)

	@staticmethod
	def registerCallback(time, func):
		return BigWorld.callback(time, func)

	@staticmethod
	def cancelCallback(callbackID):
		try:
			BigWorld.cancelCallback(callbackID)
		except ValueError:
			return False
		return True

	def __init__(self, time, callback):
		self.__cbID = self.registerCallback(time, callback)
		return

	@property
	def callbackID(self):
		return self.__cbID

	def __del__(self):
		self.cancelCallback(self.__cbID)
		return
