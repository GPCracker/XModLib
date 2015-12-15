# Authors: GPCracker

# *************************
# Python
# *************************
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
# X-Mod Code Library
# *************************
# Nothing

class Event(object):
	def __init__(self):
		self.__delegates = []
		return

	def __iadd__(self, delegate):
		if delegate not in self.__delegates:
			self.__delegates.append(delegate)
		return self

	def __isub__(self, delegate):
		if delegate in self.__delegates:
			self.__delegates.remove(delegate)
		return self

	def register(self, delegate):
		self.__iadd__(delegate)
		return

	def unregister(self, delegate):
		self.__isub__(delegate)
		return

	def __call__(self, *args, **kwargs):
		for delegate in self.__delegates:
			try:
				delegate(*args, **kwargs)
			except:
				traceback.print_exc()
		return

	def clearDelegates(self):
		del self.__delegates[:]
		return

	def __repr__(self):
		return 'Event({}):{!r}'.format(len(self.__delegates), self.__delegates)

class ReleaseEvent(Event):
	def __call__(self, *args, **kwargs):
		super(ReleaseEvent, self).__call__(*args, **kwargs)
		super(ReleaseEvent, self).clearDelegates()
		return

class Trigger(object):
	def __init__(self, status = False, onActivate = None, onDeactivate = None, onChange = None):
		self.__status = status
		self.onActivate = onActivate if onActivate is not None else Event()
		self.onDeactivate = onDeactivate if onDeactivate is not None else Event()
		self.onChange = onChange if onChange is not None else Event()
		return

	@property
	def status(self):
		return self.__status

	@status.setter
	def status(self, value):
		if value != self.__status:
			if value not in [True, False]:
				raise TypeError()
			self.__status = value
			if value == True:
				self.onActivate()
			elif value == False:
				self.onDeactivate()
			else:
				raise TypeError()
			self.onChange(value)
		return

	def setStatus(self, value):
		self.status = value
		return

	def enable(self):
		self.status = True
		return

	def disable(self):
		self.status = False
		return

	def __repr__(self):
		return 'Trigger(status = {!r}, onActivate = {!r}, onDeactivate = {!r}, onChange = {!r})'.format(
			self.status,
			self.onActivate,
			self.onDeactivate,
			self.onChange
		)

class ThreeStateTrigger(object):
	def __init__(self, status = None, onActivate = None, onDeactivate = None, onReset = None, onChange = None):
		self.__status = status
		self.onActivate = onActivate if onActivate is not None else Event()
		self.onDeactivate = onDeactivate if onDeactivate is not None else Event()
		self.onReset = onReset if onReset is not None else Event()
		self.onChange = onChange if onChange is not None else Event()
		return

	@property
	def status(self):
		return self.__status

	@status.setter
	def status(self, value):
		if value != self.__status:
			if value not in [True, False, None]:
				raise TypeError()
			self.__status = value
			if value == True:
				self.onActivate()
			elif value == False:
				self.onDeactivate()
			elif value == None:
				self.onReset()
			else:
				raise TypeError()
			self.onChange(value)
		return

	def setStatus(self, value):
		self.status = value
		return

	def enable(self):
		self.status = True
		return

	def disable(self):
		self.status = False
		return

	def reset(self):
		self.status = None
		return

	def __repr__(self):
		return 'ThreeStateTrigger(status = {!r}, onActivate = {!r}, onDeactivate = {!r}, onReset = {!r}, onChange = {!r})'.format(
			self.status,
			self.onActivate,
			self.onDeactivate,
			self.onReset,
			self.onChange
		)

class ConditionTrigger(ThreeStateTrigger):
	def __init__(self, variable = None, comparator = lambda variable: None, onActivate = None, onDeactivate = None, onReset = None, onChange = None):
		self.__variable = variable
		self.__comparator = comparator
		return super(ConditionTrigger, self).__init__(comparator(variable), onActivate, onDeactivate, onReset, onChange)

	@property
	def comparator(self):
		return self.__comparator

	@comparator.setter
	def comparator(self, value):
		self.__comparator = value
		self.status = self.__comparator(self.__variable)
		return

	@property
	def variable(self):
		return self.__variable

	@variable.setter
	def variable(self, value):
		self.__variable = value
		self.status = self.__comparator(self.__variable)
		return

	def __repr__(self):
		return 'ConditionTrigger(variable = {!r}, comparator = {!r}, onActivate = {!r}, onDeactivate = {!r}, onReset = {!r}, onChange = {!r})'.format(
			self.__variable,
			self.__comparator,
			self.onActivate,
			self.onDeactivate,
			self.onReset,
			self.onChange
		)

class Queue(list):
	def enqueue(self, item):
		return self.append(item)

	def dequeue(self):
		return self.pop(0)

	def cancel(self, item):
		return self.remove(item)

	def clear(self):
		del self[:]
		return

	def __repr__(self):
		return 'Queue({}):{}'.format(len(self), super(Queue, self).__repr__())
