# Authors: GPCracker

# *************************
# Python
# *************************
import enum
import types
import functools
import traceback
import collections

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

class HookInvoke(enum.Enum):
	MASTER = 'master'
	PRIMARY = 'primary'
	SECONDARY = 'secondary'
	DEFAULT = SECONDARY

class PropertyAction(enum.Enum):
	GET = 'fget'
	SET = 'fset'
	DEL = 'fdel'

class HookEvent(set):
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

class HookChain(collections.deque):
	__slots__ = ()

	def __iadd__(self, delegate):
		if not callable(delegate):
			return NotImplemented
		self.appendleft(delegate)
		return self

	def __isub__(self, delegate):
		if not callable(delegate):
			return NotImplemented
		self.remove(delegate)
		return self

	def __call__(self, *args, **kwargs):
		for delegate in reversed(self):
			try:
				delegate(*args, **kwargs)
			except:
				traceback.print_exc()
		return

class HookFunction(object):
	__slots__ = ('__weakref__', '_hook', '_origin', '_invoke', 'enabled')

	def __init__(self, hook, origin, invoke=HookInvoke.DEFAULT, enabled=True):
		super(HookFunction, self).__init__()
		self._hook = hook
		self._origin = origin
		self._invoke = invoke
		self.enabled = enabled
		return

	hook = property(lambda self: self._hook)
	origin = property(lambda self: self._origin)
	invoke = property(lambda self: self._invoke)

	def __call__(self, *args, **kwargs):
		if not isinstance(self._invoke, HookInvoke):
			raise TypeError('Hook invoke must be \'HookInvoke\', not {!r}.'.format(type(self._invoke).__name__))
		if not self.enabled:
			result = self._origin(*args, **kwargs)
		elif self._invoke == HookInvoke.MASTER:
			result = self._hook(self._origin, *args, **kwargs)
		elif self._invoke == HookInvoke.PRIMARY:
			self._hook(*args, **kwargs)
			result = self._origin(*args, **kwargs)
		elif self._invoke == HookInvoke.SECONDARY:
			result = self._origin(*args, **kwargs)
			self._hook(*args, **kwargs)
		return result

	def __getattribute__(self, name):
		if name in ('__doc__', '__name__', '__module__', '__defaults__'):
			return getattr(self._origin, name)
		return super(HookFunction, self).__getattribute__(name)

	def __get__(self, instance, owner=None):
		return types.MethodType(self, instance, owner)

def doMethodAdd(target, method, hook):
	if isinstance(target, (types.TypeType, types.ClassType)):
		setattr(target, method, hook)
	else:
		setattr(target, method, hook.__get__(target, types.TypeType(target)))
	return hook

def doStaticMethodAdd(target, method, hook):
	if isinstance(target, (types.TypeType, types.ClassType)):
		setattr(target, method, staticmethod(hook))
	else:
		setattr(target, method, hook)
	return hook

def doClassMethodAdd(target, method, hook):
	if isinstance(target, (types.TypeType, types.ClassType)):
		setattr(target, method, classmethod(hook))
	else:
		setattr(target, method, hook.__get__(types.TypeType(target), types.TypeType))
	return hook

def doMethodHook(target, method, hook, invoke=HookInvoke.DEFAULT, enabled=True):
	origin = getattr(target, method).__func__
	override = HookFunction(hook, origin, invoke, enabled)
	if isinstance(target, (types.TypeType, types.ClassType)):
		setattr(target, method, override)
	else:
		setattr(target, method, override.__get__(target, types.TypeType(target)))
	return hook

def doStaticMethodHook(target, method, hook, invoke=HookInvoke.DEFAULT, enabled=True):
	origin = getattr(target, method)
	override = HookFunction(hook, origin, invoke, enabled)
	if isinstance(target, (types.TypeType, types.ClassType)):
		setattr(target, method, staticmethod(override))
	else:
		setattr(target, method, override)
	return hook

def doClassMethodHook(target, method, hook, invoke=HookInvoke.DEFAULT, enabled=True):
	origin = getattr(target, method).__func__
	override = HookFunction(hook, origin, invoke, enabled)
	if isinstance(target, (types.TypeType, types.ClassType)):
		setattr(target, method, classmethod(override))
	else:
		setattr(target, method, override.__get__(types.TypeType(target), types.TypeType))
	return hook

def doPropertyHook(target, method, action, varname, hook, invoke=HookInvoke.DEFAULT, enabled=True):
	if not isinstance(target, (types.TypeType, types.ClassType)):
		raise TypeError('Property hook may be used only on classes, not on instances.')
	if hasattr(target, method):
		iproperty = getattr(target, method)
		if not isinstance(iproperty, property):
			raise TypeError('This class variable is already defined and is not a property.')
	else:
		iproperty = property(
			functools.partial(lambda instance, varname: getattr(instance, varname), varname=varname),
			functools.partial(lambda instance, value, varname: setattr(instance, varname, value), varname=varname),
			functools.partial(lambda instance, varname: delattr(instance, varname), varname=varname)
		)
		setattr(target, method, iproperty)
	if not isinstance(action, PropertyAction):
		raise ValueError('Incorrect property action.')
	kwargs = {
		'fget': iproperty.fget,
		'fset': iproperty.fset,
		'fdel': iproperty.fdel,
		'doc': iproperty.__doc__
	}
	kwargs[action.value] = HookFunction(hook, kwargs[action.value], invoke, enabled)
	setattr(target, method, property(**kwargs))
	return hook

def doMethodAddExt(event, target, method, hook):
	event += functools.partial(doMethodAdd, target, method, hook)
	return hook

def doStaticMethodAddExt(event, target, method, hook):
	event += functools.partial(doStaticMethodAdd, target, method, hook)
	return hook

def doClassMethodAddExt(event, target, method, hook):
	event += functools.partial(doClassMethodAdd, target, method, hook)
	return hook

def doMethodHookExt(event, target, method, hook, invoke=HookInvoke.DEFAULT, enabled=True):
	event += functools.partial(doMethodHook, target, method, hook, invoke=invoke, enabled=enabled)
	return hook

def doStaticMethodHookExt(event, target, method, hook, invoke=HookInvoke.DEFAULT, enabled=True):
	event += functools.partial(doStaticMethodHook, target, method, hook, invoke=invoke, enabled=enabled)
	return hook

def doClassMethodHookExt(event, target, method, hook, invoke=HookInvoke.DEFAULT, enabled=True):
	event += functools.partial(doClassMethodHook, target, method, hook, invoke=invoke, enabled=enabled)
	return hook

def doPropertyHookExt(event, target, method, action, varname, hook, invoke=HookInvoke.DEFAULT, enabled=True):
	event += functools.partial(doPropertyHook, target, method, action, varname, hook, invoke=invoke, enabled=enabled)
	return hook

def methodAdd(target, method):
	return functools.partial(doMethodAdd, target, method)

def staticMethodAdd(target, method):
	return functools.partial(doStaticMethodAdd, target, method)

def classMethodAdd(target, method):
	return functools.partial(doClassMethodAdd, target, method)

def methodHook(target, method, invoke=HookInvoke.DEFAULT, enabled=True):
	return functools.partial(doMethodHook, target, method, invoke=invoke, enabled=enabled)

def staticMethodHook(target, method, invoke=HookInvoke.DEFAULT, enabled=True):
	return functools.partial(doStaticMethodHook, target, method, invoke=invoke, enabled=enabled)

def classMethodHook(target, method, invoke=HookInvoke.DEFAULT, enabled=True):
	return functools.partial(doClassMethodHook, target, method, invoke=invoke, enabled=enabled)

def propertyHook(target, method, action, varname, invoke=HookInvoke.DEFAULT, enabled=True):
	return functools.partial(doPropertyHook, target, method, action, varname, invoke=invoke, enabled=enabled)

def methodAddExt(event, target, method):
	return functools.partial(doMethodAddExt, event, target, method)

def staticMethodAddExt(event, target, method):
	return functools.partial(doStaticMethodAddExt, event, target, method)

def classMethodAddExt(event, target, method):
	return functools.partial(doClassMethodAddExt, event, target, method)

def methodHookExt(event, target, method, invoke=HookInvoke.DEFAULT, enabled=True):
	return functools.partial(doMethodHookExt, event, target, method, invoke=invoke, enabled=enabled)

def staticMethodHookExt(event, target, method, invoke=HookInvoke.DEFAULT, enabled=True):
	return functools.partial(doStaticMethodHookExt, event, target, method, invoke=invoke, enabled=enabled)

def classMethodHookExt(event, target, method, invoke=HookInvoke.DEFAULT, enabled=True):
	return functools.partial(doClassMethodHookExt, event, target, method, invoke=invoke, enabled=enabled)

def propertyHookExt(event, target, method, action, varname, invoke=HookInvoke.DEFAULT, enabled=True):
	return functools.partial(doPropertyHookExt, event, target, method, action, varname, invoke=invoke, enabled=enabled)
