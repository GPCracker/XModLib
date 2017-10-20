# Authors: GPCracker

# *************************
# Python
# *************************
import operator
import functools
import itertools
import collections

# *************************
# BigWorld
# *************************
import Keys
import BigWorld

# *************************
# WoT Client
# *************************
# Nothing

# *************************
# X-Mod Library
# *************************
# Nothing

MODIFIER_KEYS = frozenset({
	Keys.KEY_LSHIFT,
	Keys.KEY_RSHIFT,
	Keys.KEY_LCONTROL,
	Keys.KEY_RCONTROL,
	Keys.KEY_LALT,
	Keys.KEY_RALT
})
MODIFIER_FLAGS = frozenset({
	Keys.MODIFIER_SHIFT,
	Keys.MODIFIER_CTRL,
	Keys.MODIFIER_ALT
})
MODIFIER_KEY2FLAG = {
	Keys.KEY_LSHIFT: Keys.MODIFIER_SHIFT,
	Keys.KEY_RSHIFT: Keys.MODIFIER_SHIFT,
	Keys.KEY_LCONTROL: Keys.MODIFIER_CTRL,
	Keys.KEY_RCONTROL: Keys.MODIFIER_CTRL,
	Keys.KEY_LALT: Keys.MODIFIER_ALT,
	Keys.KEY_RALT: Keys.MODIFIER_ALT
}
MODIFIER_FLAG2KEY = {
	Keys.MODIFIER_SHIFT: (Keys.KEY_LSHIFT, Keys.KEY_RSHIFT),
	Keys.MODIFIER_CTRL: (Keys.KEY_LCONTROL, Keys.KEY_RCONTROL),
	Keys.MODIFIER_ALT: (Keys.KEY_LALT, Keys.KEY_RALT)
}
MODIFIER_PAIRS = {
	Keys.KEY_LSHIFT: Keys.KEY_RSHIFT,
	Keys.KEY_RSHIFT: Keys.KEY_LSHIFT,
	Keys.KEY_LCONTROL: Keys.KEY_RCONTROL,
	Keys.KEY_RCONTROL: Keys.KEY_LCONTROL,
	Keys.KEY_LALT: Keys.KEY_RALT,
	Keys.KEY_RALT: Keys.KEY_LALT,
}

class KeyboardEvent(collections.namedtuple('KeyboardEvent', ('key', 'modifiers', 'down', 'repeat'))):
	__slots__ = ()

	@staticmethod
	def _parseEvent(event):
		cmask = ~(MODIFIER_KEY2FLAG[event.key] if event.key in MODIFIER_KEYS and not BigWorld.isKeyDown(MODIFIER_PAIRS[event.key]) else 0x0)
		return event.key, event.modifiers & cmask, event.isKeyDown(), event.isRepeatedEvent()

	def __new__(cls, event):
		return super(KeyboardEvent, cls).__new__(cls, *cls._parseEvent(event))

class ShortcutHandle(collections.namedtuple('ShortcutHandle', ('switch', 'pushed'))):
	__slots__ = ()

	def __new__(cls, switch, pushed):
		return super(ShortcutHandle, cls).__new__(cls, switch, pushed)

	def __call__(self, value):
		return bool(value) != bool(self.pushed) if self.switch else bool(self.pushed)

class Shortcut(collections.namedtuple('Shortcut', ('key', 'modifiers', 'switch', 'invert', 'repeat'))):
	__slots__ = ()

	sequence = property(lambda self: self._buildSequence(self.key, self.modifiers))

	@staticmethod
	def _buildSequence(key, modifiers):
		def _getAlias(key):
			alias = 'KEY_' + BigWorld.keyToString(key)
			if getattr(Keys, alias, None) is None:
				raise LookupError('Key could not be recognized.')
			return alias
		return '+'.join(itertools.imap(_getAlias, itertools.chain(
			(MODIFIER_FLAG2KEY[flag][0] for flag in MODIFIER_FLAGS if modifiers & flag), (key, )
		)))

	@staticmethod
	def _parseSequence(sequence):
		sequence = map(lambda alias: getattr(Keys, alias, None), sequence.split('+'))
		if None in sequence:
			raise LookupError('One or more keys could not be recognized.')
		key, modifiers = sequence.pop(), set(sequence)
		if modifiers.difference(MODIFIER_KEYS):
			raise LookupError('Only Shift, Ctrl and Alt could be modifiers.')
		return (
			key if key is not Keys.KEY_NONE else -1,
			functools.reduce(operator.or_, itertools.imap(functools.partial(operator.getitem, MODIFIER_KEY2FLAG), modifiers), 0x0)
		)

	def __new__(cls, sequence, switch=True, invert=False, repeat=False):
		return super(Shortcut, cls).__new__(cls, *cls._parseSequence(sequence), switch=switch, invert=invert, repeat=repeat)

	def __call__(self, kbevent):
		if kbevent.key == self.key and kbevent.modifiers == self.modifiers and (not kbevent.repeat or self.repeat):
			return ShortcutHandle(self.switch, bool(kbevent.down) != bool(self.invert))
		return None
