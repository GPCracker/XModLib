# Authors: GPCracker

# *************************
# Python
# *************************
import weakref
import functools
import traceback

# *************************
# BigWorld
# *************************
# Nothing

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

class Event(set):
	__slots__ = ()

	def __iadd__(self, delegate):
		if not callable(delegate):
			return NotImplemented
		self.add(delegate)
		return self

	def __isub__(self, delegate):
		if not callable(delegate):
			return NotImplemented
		self.remove(delegate)
		return self

	def __call__(self, *args, **kwargs):
		for delegate in self:
			try:
				delegate(*args, **kwargs)
			except:
				traceback.print_exc()
		return
