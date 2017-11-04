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

	__repr__ = object.__repr__
	__str__ = object.__str__

	def __del__(self):
		self._cancel(self)
		return

class CallbackLoopType(enum.Enum):
	SINGLE = 'single'
	STATIC = 'static'
	DYNAMIC = 'dynamic'
	DEFAULT = STATIC

class CallbackLoop(object):
	__slots__ = ('__weakref__', '_interval', '_function', '_calltype', '_callback')

	def __init__(self, interval, function, calltype=CallbackLoopType.DEFAULT):
		if not isinstance(interval, (int, float)):
			raise TypeError('interval argument must be int or float, not {}'.format(type(interval).__name__))
		if not isinstance(calltype, CallbackLoopType):
			raise TypeError('calltype argument must be CallbackLoopType, not {}'.format(type(calltype).__name__))
		self._interval = interval
		self._function = function
		self._calltype = calltype
		self._callback = None
		return

	interval = property(lambda self: self._interval)
	function = property(lambda self: self._function)
	calltype = property(lambda self: self._calltype)

	@property
	def isActive(self):
		return self._callback is not None

	def _schedule(self, delay):
		return Callback(delay, getMethodProxy(self._cbmethod))

	def _cbmethod(self):
		if self._callback is not None:
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
		if self._callback is not None:
			raise RuntimeError('callback loop is already started')
		self._callback = self._schedule(delay if delay is not None else self._interval)
		return

	def stop(self):
		if self._callback is None:
			raise RuntimeError('callback loop is not active')
		self._callback = None
		return

	def __repr__(self):
		return '{}(interval={!r}, function={!r}, calltype={!r})'.format(self.__class__.__name__, self._interval, self._function, self._calltype)

	def __del__(self):
		self._callback = None
		return
