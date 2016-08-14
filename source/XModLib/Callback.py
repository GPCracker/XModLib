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
	def getMethodProxy(method, *args, **kwargs):
		return functools.partial(weakref.proxy(method.im_func), weakref.proxy(method.im_self), *args, **kwargs)

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

class CallbackLoop(object):
	CALLBACK_FIRST = 0x0
	CALL_FIRST = 0x1
	CALL_ONLY = 0x2

	def __init__(self, interval, function, calltype=CALLBACK_FIRST):
		self._interval = interval
		self._function = function
		self._calltype = calltype
		self._callback = None
		return

	@property
	def isActive(self):
		return self._callback is not None

	def _callloop(self):
		if self._calltype == self.CALLBACK_FIRST:
			self._callback = Callback(self._interval, Callback.getMethodProxy(self._callloop)) if self.isActive else None
			if self.isActive:
				self._function()
		elif self._calltype == self.CALL_FIRST:
			if self.isActive:
				self._function()
			self._callback = Callback(self._interval, Callback.getMethodProxy(self._callloop)) if self.isActive else None
		elif self._calltype == self.CALL_ONLY:
			if self.isActive:
				self._function()
			self._callback = None
		else:
			raise ValueError('Incorrect call type.')
		return

	def start(self, delay=None):
		if self.isActive:
			raise RuntimeError('Callback loop is already started.')
		self._callback = Callback(delay if delay is not None else self._interval, Callback.getMethodProxy(self._callloop))
		return

	def stop(self):
		if not self.isActive:
			raise RuntimeError('Callback loop is not active.')
		self._callback = None
		return

	def __repr__(self):
		return 'CallbackLoop(interval={!r}, function={!r}, calltype={!r})'.format(self._interval, self._function, self._calltype)

	def __del__(self):
		self._callback = None
		return
