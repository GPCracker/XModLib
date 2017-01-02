# Authors: GPCracker

# *************************
# Python
# *************************
import types
import functools

# *************************
# Python backports
# *************************
import backports.enum

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
from .FuncUtils import Event as HookEvent

class HookInvoke(backports.enum.Enum):
	MASTER = 'master'
	PRIMARY = 'primary'
	SECONDARY = 'secondary'
	DEFAULT = SECONDARY

class PropertyAction(backports.enum.Enum):
	GET = 'fget'
	SET = 'fset'
	DEL = 'fdel'

class HookFunction(object):
	__slots__ = ('__weakref__', '__name__', '_hook', '_origin', '_invoke', 'active')

	def __init__(self, hook, origin, invoke=HookInvoke.DEFAULT, active=True):
		if not isinstance(hook, (types.FunctionType, types.LambdaType)):
			raise TypeError('Hook must be function or lambda.')
		self.__name__ = hook.__name__
		self._hook = hook
		self._origin = origin
		self._invoke = invoke
		self.active = active
		return

	hook = property(lambda self: self._hook)
	origin = property(lambda self: self._origin)
	invoke = property(lambda self: self._invoke)

	def __call__(self, *args, **kwargs):
		if not isinstance(self._invoke, HookInvoke):
			raise ValueError('Incorrect hook invoke type.')
		if not self.active:
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

	def __get__(self, instance, type=None):
		return types.MethodType(self, instance, type)

	@classmethod
	def doMethodAdd(sclass, target, method, hook):
		if isinstance(target, (types.TypeType, types.ClassType)):
			setattr(target, method, hook)
		else:
			setattr(target, method, hook.__get__(target, types.TypeType(target)))
		return hook

	@classmethod
	def doStaticMethodAdd(sclass, target, method, hook):
		if isinstance(target, (types.TypeType, types.ClassType)):
			setattr(target, method, staticmethod(hook))
		else:
			setattr(target, method, hook)
		return hook

	@staticmethod
	def doClassMethodAdd(sclass, target, method, hook):
		if isinstance(target, (types.TypeType, types.ClassType)):
			setattr(target, method, classmethod(hook))
		else:
			setattr(target, method, hook.__get__(types.TypeType(target), types.TypeType))
		return hook

	@classmethod
	def doMethodHook(sclass, target, method, hook, invoke=HookInvoke.DEFAULT, active=True):
		origin = getattr(target, method).__func__
		override = sclass(hook, origin, invoke, active)
		if isinstance(target, (types.TypeType, types.ClassType)):
			setattr(target, method, override)
		else:
			setattr(target, method, override.__get__(target, types.TypeType(target)))
		return hook

	@classmethod
	def doStaticMethodHook(sclass, target, method, hook, invoke=HookInvoke.DEFAULT, active=True):
		origin = getattr(target, method)
		override = sclass(hook, origin, invoke, active)
		if isinstance(target, (types.TypeType, types.ClassType)):
			setattr(target, method, staticmethod(override))
		else:
			setattr(target, method, override)
		return hook

	@classmethod
	def doClassMethodHook(sclass, target, method, hook, invoke=HookInvoke.DEFAULT, active=True):
		origin = getattr(target, method).__func__
		override = sclass(hook, origin, invoke, active)
		if isinstance(target, (types.TypeType, types.ClassType)):
			setattr(target, method, classmethod(override))
		else:
			setattr(target, method, override.__get__(types.TypeType(target), types.TypeType))
		return hook

	@classmethod
	def doPropertyHook(sclass, target, method, action, varname, hook, invoke=HookInvoke.DEFAULT, active=True):
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
		kwargs[action.value] = sclass(hook, kwargs[action.value], invoke, active)
		setattr(target, method, property(**kwargs))
		return hook

	@classmethod
	def doMethodAddExt(sclass, event, target, method, hook):
		event += functools.partial(sclass.doMethodAdd, target, method, hook)
		return hook

	@classmethod
	def doStaticMethodAddExt(sclass, event, target, method, hook):
		event += functools.partial(sclass.doStaticMethodAdd, target, method, hook)
		return hook

	@staticmethod
	def doClassMethodAddExt(sclass, event, target, method, hook):
		event += functools.partial(sclass.doClassMethodAdd, target, method, hook)
		return hook

	@classmethod
	def doMethodHookExt(sclass, event, target, method, hook, invoke=HookInvoke.DEFAULT, active=True):
		event += functools.partial(sclass.doMethodHook, target, method, hook, invoke=invoke, active=active)
		return hook

	@classmethod
	def doStaticMethodHookExt(sclass, event, target, method, hook, invoke=HookInvoke.DEFAULT, active=True):
		event += functools.partial(sclass.doStaticMethodHook, target, method, hook, invoke=invoke, active=active)
		return hook

	@classmethod
	def doClassMethodHookExt(sclass, event, target, method, hook, invoke=HookInvoke.DEFAULT, active=True):
		event += functools.partial(sclass.doClassMethodHook, target, method, hook, invoke=invoke, active=active)
		return hook

	@classmethod
	def doPropertyHookExt(sclass, event, target, method, action, varname, hook, invoke=HookInvoke.DEFAULT, active=True):
		event += functools.partial(sclass.doPropertyHook, target, method, action, varname, hook, invoke=invoke, active=active)
		return hook

	@classmethod
	def methodAdd(sclass, target, method):
		return functools.partial(sclass.doMethodAdd, target, method)

	@classmethod
	def staticMethodAdd(sclass, target, method):
		return functools.partial(sclass.doStaticMethodAdd, target, method)

	@classmethod
	def classMethodAdd(sclass, target, method):
		return functools.partial(sclass.doClassMethodAdd, target, method)

	@classmethod
	def methodHook(sclass, target, method, invoke=HookInvoke.DEFAULT, active=True):
		return functools.partial(sclass.doMethodHook, target, method, invoke=invoke, active=active)

	@classmethod
	def staticMethodHook(sclass, target, method, invoke=HookInvoke.DEFAULT, active=True):
		return functools.partial(sclass.doStaticMethodHook, target, method, invoke=invoke, active=active)

	@classmethod
	def classMethodHook(sclass, target, method, invoke=HookInvoke.DEFAULT, active=True):
		return functools.partial(sclass.doClassMethodHook, target, method, invoke=invoke, active=active)

	@classmethod
	def propertyHook(sclass, target, method, action, varname, invoke=HookInvoke.DEFAULT, active=True):
		return functools.partial(sclass.doPropertyHook, target, method, action, varname, invoke=invoke, active=active)

	@classmethod
	def methodAddExt(sclass, event, target, method):
		return functools.partial(sclass.doMethodAddExt, event, target, method)

	@classmethod
	def staticMethodAddExt(sclass, event, target, method):
		return functools.partial(sclass.doStaticMethodAddExt, event, target, method)

	@classmethod
	def classMethodAddExt(sclass, event, target, method):
		return functools.partial(sclass.doClassMethodAddExt, event, target, method)

	@classmethod
	def methodHookExt(sclass, event, target, method, invoke=HookInvoke.DEFAULT, active=True):
		return functools.partial(sclass.doMethodHookExt, event, target, method, invoke=invoke, active=active)

	@classmethod
	def staticMethodHookExt(sclass, event, target, method, invoke=HookInvoke.DEFAULT, active=True):
		return functools.partial(sclass.doStaticMethodHookExt, event, target, method, invoke=invoke, active=active)

	@classmethod
	def classMethodHookExt(sclass, event, target, method, invoke=HookInvoke.DEFAULT, active=True):
		return functools.partial(sclass.doClassMethodHookExt, event, target, method, invoke=invoke, active=active)

	@classmethod
	def propertyHookExt(sclass, event, target, method, action, varname, invoke=HookInvoke.DEFAULT, active=True):
		return functools.partial(sclass.doPropertyHookExt, event, target, method, action, varname, invoke=invoke, active=active)
