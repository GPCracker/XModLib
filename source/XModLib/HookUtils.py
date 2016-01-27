# Authors: GPCracker

# *************************
# Python
# *************************
import types
import functools

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
from .Helpers import ReleaseEvent as HookEvent

class HookFunction(object):
	PROPERTY_ACTION_GET = 'fget'
	PROPERTY_ACTION_SET = 'fset'
	PROPERTY_ACTION_DEL = 'fdel'
	CALL_ORIGIN_BEFORE_HOOK = 0x0
	CALL_HOOK_BEFORE_ORIGIN = 0x1
	CALL_ORIGIN_INSIDE_HOOK = 0x2

	def __init__(self, origin, hook, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
		if not isinstance(hook, (types.FunctionType, types.LambdaType)):
			raise TypeError('Hook must be function or lambda')
		self.__name__ = hook.__name__
		self.origin = origin
		self.hook = hook
		self.calltype = calltype
		self.active = active
		return

	def __call__(self, *args, **kwargs):
		if self.active and self.calltype == self.CALL_ORIGIN_BEFORE_HOOK:
			result = self.origin(*args, **kwargs)
			self.hook(*args, **kwargs)
		elif self.active and self.calltype == self.CALL_HOOK_BEFORE_ORIGIN:
			self.hook(*args, **kwargs)
			result = self.origin(*args, **kwargs)
		elif self.active and self.calltype == self.CALL_ORIGIN_INSIDE_HOOK:
			result = self.hook(self.origin, *args, **kwargs)
		else:
			result = self.origin(*args, **kwargs)
		return result

	def __get__(self, instance, type=None):
		return types.MethodType(self, instance, type)

	@classmethod
	def makeMethodHook(sclass, target, method, hook, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
		origin = getattr(target, method).__func__
		override = sclass(origin, hook, calltype, active)
		if isinstance(target, (types.TypeType, types.ClassType)):
			setattr(target, method, override)
		else:
			setattr(target, method, override.__get__(target, types.TypeType(target)))
		return hook

	@classmethod
	def makeStaticMethodHook(sclass, target, method, hook, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
		origin = getattr(target, method)
		override = sclass(origin, hook, calltype, active)
		if isinstance(target, (types.TypeType, types.ClassType)):
			setattr(target, method, staticmethod(override))
		else:
			setattr(target, method, override)
		return hook

	@classmethod
	def makeClassMethodHook(sclass, target, method, hook, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
		origin = getattr(target, method).__func__
		override = sclass(origin, hook, calltype, active)
		if isinstance(target, (types.TypeType, types.ClassType)):
			setattr(target, method, classmethod(override))
		else:
			setattr(target, method, override.__get__(types.TypeType(target), types.TypeType))
		return hook

	@classmethod
	def makePropertyHook(sclass, target, method, varname, hook, action=PROPERTY_ACTION_SET, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
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
		if action not in (sclass.PROPERTY_ACTION_GET, sclass.PROPERTY_ACTION_SET, sclass.PROPERTY_ACTION_DEL):
			raise ValueError('Incorrect action value.')
		kwargs = {
			'fget': iproperty.fget,
			'fset': iproperty.fset,
			'fdel': iproperty.fdel,
			'doc': iproperty.__doc__
		}
		kwargs[action] = sclass(kwargs[action], hook, calltype, active)
		setattr(target, method, property(**kwargs))
		return hook

	@classmethod
	def makeMethodHookOnEvent(sclass, event, target, method, hook, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
		event += functools.partial(sclass.makeMethodHook, target, method, hook, calltype=calltype, active=active)
		return hook

	@classmethod
	def makeStaticMethodHookOnEvent(sclass, event, target, method, hook, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
		event += functools.partial(sclass.makeStaticMethodHook, target, method, hook, calltype=calltype, active=active)
		return hook

	@classmethod
	def makeClassMethodHookOnEvent(sclass, event, target, method, hook, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
		event += functools.partial(sclass.makeClassMethodHook, target, method, hook, calltype=calltype, active=active)
		return hook

	@classmethod
	def makePropertyHookOnEvent(sclass, event, target, method, varname, hook, action=PROPERTY_ACTION_SET, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
		event += functools.partial(sclass.makePropertyHook, target, method, varname, hook, action=action, calltype=calltype, active=active)
		return hook

	@classmethod
	def methodHook(sclass, target, method, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
		return functools.partial(sclass.makeMethodHook, target, method, calltype=calltype, active=active)

	@classmethod
	def staticMethodHook(sclass, target, method, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
		return functools.partial(sclass.makeStaticMethodHook, target, method, calltype=calltype, active=active)

	@classmethod
	def classMethodHook(sclass, target, method, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
		return functools.partial(sclass.makeClassMethodHook, target, method, calltype=calltype, active=active)

	@classmethod
	def propertyHook(sclass, target, method, varname, action=PROPERTY_ACTION_SET, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
		return functools.partial(sclass.makePropertyHook, target, method, varname, action=action, calltype=calltype, active=active)

	@classmethod
	def methodHookOnEvent(sclass, event, target, method, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
		return functools.partial(sclass.makeMethodHookOnEvent, event, target, method, calltype=calltype, active=active)

	@classmethod
	def staticMethodHookOnEvent(sclass, event, target, method, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
		return functools.partial(sclass.makeStaticMethodHookOnEvent, event, target, method, calltype=calltype, active=active)

	@classmethod
	def classMethodHookOnEvent(sclass, event, target, method, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
		return functools.partial(sclass.makeClassMethodHookOnEvent, event, target, method, calltype=calltype, active=active)

	@classmethod
	def propertyHookOnEvent(sclass, event, target, method, varname, action=PROPERTY_ACTION_SET, calltype=CALL_ORIGIN_BEFORE_HOOK, active=True):
		return functools.partial(sclass.makePropertyHookOnEvent, event, target, method, varname, action=action, calltype=calltype, active=active)
