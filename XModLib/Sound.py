# Authors: GPCracker

import FMOD

from .Helpers import Callback

class DummySound(object):
	duration = 0.0
	pitch = 0.0
	volume = 1.0
	isPlaying = True
	isStolen = False
	muted = False
	paused = False
	name = ''
	state = 'playing'
	dummyMethod = lambda self, *args, **kwargs: None
	getParentCategory = dummyMethod
	getParentGroup = dummyMethod
	getParentGroup = dummyMethod
	getParentProject = dummyMethod
	listParams = dummyMethod
	param = dummyMethod
	play = dummyMethod
	setCallback = dummyMethod
	stop = dummyMethod
	stopAndUnload = dummyMethod

class Sound(object):
	def __init__(self, soundName, autoPlay = False, useDummy = True):
		self.__fmodSound = FMOD.playSound(soundName)
		if not self.__fmodSound and useDummy:
			self.__fmodSound = DummySound()
		if not autoPlay:
			self.__fmodSound.stop()
		return

	@property
	def fmodSound(self):
		return self.__fmodSound

	def __repr__(self):
		return 'Sound(soundName={})'.format(repr(self.__fmodSound.name))

	def __del__(self):
		self.__fmodSound.stop()
		return

class SoundEvent(object):
	def __init__(self, sound, priority = 0):
		self.sound = sound
		self.priority = priority
		return

	def __call__(self):
		return self.sound.fmodSound.play()

	def __repr__(self):
		return 'SoundEvent(sound={}, priority={})'.format(repr(self.sound), repr(self.priority))

	def __del__(self):
		return

class QueuedSoundEvent(object):
	def __init__(self, soundEvent, timestamp):
		self.soundEvent = soundEvent
		self.timestamp = timestamp
		return

	@property
	def sound(self):
		return self.soundEvent.sound

	@property
	def priority(self):
		return self.soundEvent.priority

	def __call__(self):
		return self.soundEvent()

	def __repr__(self):
		return 'QueuedSoundEvent(sound={}, timestamp={}, priority={})'.format(repr(self.sound), repr(self.timestamp), repr(self.priority))

	def __del__(self):
		return

class SoundEventQueue(list):
	def __init__(self, maxlen = 10, maxDelay = 2.0):
		super(SoundEventQueue, self).__init__()
		self.maxlen = maxlen
		self.maxDelay = maxDelay
		return

	def update(self, timestamp = None):
		if len(self) > self.maxlen:
			self.remove(min(self, key=lambda queuedSoundEvent: queuedSoundEvent.timestamp))
		if timestamp is not None:
			for queuedSoundEvent in filter(lambda queuedSoundEvent: queuedSoundEvent.timestamp + self.maxDelay < timestamp, self):
				self.remove(queuedSoundEvent)
		self.sort(key=lambda queuedSoundEvent: queuedSoundEvent.priority)
		return

	def popItem(self, timestamp = None):
		self.update(timestamp)
		return self.pop() if self else None

	def appendItem(self, queuedSoundEvent):
		self.append(queuedSoundEvent)
		self.update()
		return

	def __repr__(self):
		return 'SoundEventQueue({}):{}'.format(len(self), super(SoundEventQueue, self).__repr__())

	def __del__(self):
		return

class SoundEventQueueManager(object):
	@staticmethod
	def getCurrentTimestamp():
		return BigWorld.time()

	def __init__(self, maxQueueLength = 10, maxDelay = 2.0, eventDelay = 0.5):
		self.__queue = SoundEventQueue(maxQueueLength, maxDelay)
		self.__eventDelay = eventDelay
		self.__queueCallback = None
		return

	def playSoundEvent(self, soundEvent):
		self.__queue.appendItem(QueuedSoundEvent(soundEvent, self.getCurrentTimestamp()))
		if self.__queueCallback is None:
			self.__queueCallback = Callback(0.0, self.__queueCallbackFunc.im_func, self.__queueCallbackFunc.im_self)
		return

	def __handleQueue(self):
		if self.__queue:
			soundEvent = self.__queue.popItem(self.getCurrentTimestamp())
			if soundEvent is not None:
				soundEvent()
				return soundEvent.sound.fmodSound.duration
		return None

	def __queueCallbackFunc(self):
		duration = self.__handleQueue()
		self.__queueCallback = Callback(duration + self.__eventDelay, self.__queueCallbackFunc.im_func, self.__queueCallbackFunc.im_self) if duration else None
		return

	def __repr__(self):
		return super(SoundEventQueueManager, self).__repr__()

	def __del__(self):
		self.__queueCallback = None
		return

class SoundEventManager(object):
	def __init__(self):
		self.__events = {}
		self.__sounds = {}
		self.__queues = {}
		return None

	def addSoundEvent(self, soundEventName, soundEvent):
		self.__events[soundEventName] = soundEvent
		return None

	def removeSoundEvent(self, soundEventName):
		del self.__events[soundEventName]
		return None

	def addQueue(self, queueName, maxQueueLength = 10, maxDelay = 2.0, eventDelay = 0.5):
		self.__queues[queueName] = SoundEventQueueManager(maxQueueLength, maxDelay, eventDelay)
		return None

	def removeQueue(self, queueName):
		del self.__queues[queueName]
		return None

	def playAsyncSoundEvent(self, soundEventName):
		return self.__events[soundEventName]()

	def playQueuedSoundEvent(self, soundEventName, queueName):
		return self.__queues[queueName].playSoundEvent(self.__events[soundEventName])

	def addAsyncSound(self, soundName, sound):
		self.__sounds[soundName] = sound
		return None

	def removeAsyncSound(self, soundName):
		del self.__sounds[soundName]
		return None

	def playAsyncSound(self, soundName):
		self.__sounds[soundName].fmodSound.play()
		return None

	def stopAsyncSound(self, soundName):
		self.__sounds[soundName].fmodSound.stop()

	def getAsyncSoundVolume(self, soundName):
		return self.__sounds[soundName].fmodSound.volume

	def setAsyncSoundVolume(self, soundName, volume):
		self.__sounds[soundName].fmodSound.volume = volume
		return None

	def __repr__(self):
		return super(SoundEventManager, self).__repr__()

	def __del__(self):
		return
