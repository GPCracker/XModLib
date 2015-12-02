# Authors: GPCracker

from .Helpers import Event, Queue, ThreeStateTrigger
from .Callback import Callback

class DelayTrigger(ThreeStateTrigger):
	def __init__(self, dynamicStatus = None, status = None, activateDelay = 0.0, deactivateDelay = 0.0, resetDelay = 0.0, onActivate = None, onDeactivate = None, onReset = None, onChange = None):
		self.__dynamicStatus = dynamicStatus
		self.__activateDelay = activateDelay
		self.__deactivateDelay = deactivateDelay
		self.__resetDelay = resetDelay
		self.__callback = None
		return super(DelayTrigger, self).__init__(status, onActivate, onDeactivate, onReset, onChange)

	@property
	def dynamicStatus(self):
		return self.__dynamicStatus

	@dynamicStatus.setter
	def dynamicStatus(self, value):
		if value != self.__dynamicStatus:
			if value not in [True, False, None]:
				raise TypeError()
			self.__callback = None
			self.__dynamicStatus = value
			if value == True:
				delay = self.__activateDelay
			elif value == False:
				delay = self.__deactivateDelay
			elif value == None:
				delay = self.__resetDelay
			else:
				raise TypeError()
			self.__callback = Callback(delay, Callback.getMethodProxy(self.updateStatus))
		return

	def setDynamicStatus(self, value):
		self.dynamicStatus = value
		return

	def dynamicEnable(self):
		self.dynamicStatus = True
		return

	def dynamicDisable(self):
		self.dynamicStatus = False
		return

	def dynamicReset(self):
		self.dynamicStatus = None
		return

	def updateStatus(self):
		self.status = self.__dynamicStatus
		return

	def __repr__(self):
		return 'DelayTrigger(dynamicStatus = {!r}, status = {!r}, activateDelay = {!r}, deactivateDelay = {!r}, resetDelay = {!r}, onActivate = {!r}, onDeactivate = {!r}, onReset = {!r}, onChange = {!r})'.format(
			self.dynamicStatus,
			self.status,
			self.__activateDelay,
			self.__deactivateDelay,
			self.__resetDelay,
			self.onActivate,
			self.onDeactivate,
			self.onReset,
			self.onChange
		)

class DelayQueue(Queue):
	def __init__(self, dequeueDelay = 0.0, onDequeue = None):
		self.__dequeueDelay = dequeueDelay
		self.onDequeue = onDequeue if onDequeue is not None else Event()
		self.__callback = None
		super(DelayQueue, self).__init__()
		return

	def dequeueCallback(self):
		if self:
			self.onDequeue(self.dequeue())
			self.__callback = Callback(self.__dequeueDelay, Callback.getMethodProxy(self.dequeueCallback))
		else:
			self.__callback = None
		return

	def enqueue(self, item):
		super(DelayQueue, self).enqueue(item)
		if self.__callback is None:
			self.__callback = Callback(self.__dequeueDelay, Callback.getMethodProxy(self.dequeueCallback))
		return

	def __repr__(self):
		return 'DelayQueue({}):{}'.format(len(self), super(Queue, self).__repr__())
