# Authors: GPCracker

# *************************
# Python
# *************************
import enum
import weakref
import functools

# *************************
# BigWorld
# *************************
import BigWorld

# *************************
# WoT Client
# *************************
# Nothing

# *************************
# X-Mod Library
# *************************
# Nothing

def getMethodProxy(method, *args, **kwargs):
	return functools.partial(weakref.proxy(method.im_func), weakref.proxy(method.im_self), *args, **kwargs)

class Callback(int):
	__slots__ = ()

	@staticmethod
	def _register(time, func):
		return BigWorld.callback(time, func)

	@staticmethod
	def _cancel(callbackID):
		try:
			BigWorld.cancelCallback(callbackID)
		except ValueError:
			return False
		return True

	def __new__(cls, time, callback):
		return super(Callback, cls).__new__(cls, cls._register(time, callback))

	def __repr__(self):
		return '{}({})'.format(self.__class__.__name__, super(Callback, self).__repr__())

	def __del__(self):
		self._cancel(self)
		return

class CallbackLoopType(enum.Enum):
	SINGLE = 'single'
	STATIC = 'static'
	DYNAMIC = 'dynamic'

class CallbackLoop(object):
	__slots__ = ('__weakref__', '_interval', '_function', '_calltype', '_callback')

	def __init__(self, interval, function, calltype=CallbackLoopType.STATIC):
		self._interval = interval
		self._function = function
		self._calltype = calltype
		self._callback = None
		return

	@property
	def isActive(self):
		return self._callback is not None

	def _schedule(self, interval):
		return Callback(interval, getMethodProxy(self._callloop))

	def _callloop(self):
		if not isinstance(self._calltype, CallbackLoopType):
			raise ValueError('Incorrect callback loop type.')
		if self.isActive:
			if self._calltype == CallbackLoopType.SINGLE:
				self._callback = None
				self._function()
			elif self._calltype == CallbackLoopType.STATIC:
				self._callback = self._schedule(self._interval)
				self._function()
			elif self._calltype == CallbackLoopType.DYNAMIC:
				self._function()
				self._callback = self._schedule(self._interval)
		return

	def start(self, delay=None):
		if self.isActive:
			raise RuntimeError('Callback loop is already started.')
		self._callback = self._schedule(delay if delay is not None else self._interval)
		return

	def stop(self):
		if not self.isActive:
			raise RuntimeError('Callback loop is not active.')
		self._callback = None
		return

	def __repr__(self):
		return '{}(interval={!r}, function={!r}, calltype={!r})'.format(self.__class__.__name__, self._interval, self._function, self._calltype)

	def __del__(self):
		self._callback = None
		return
