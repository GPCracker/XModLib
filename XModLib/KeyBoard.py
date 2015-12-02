# Authors: GPCracker

import BigWorld
import Keys

class KeyBoard(object):
	'''
	Parsing keyboard events and hot-key sequences.
	Key modifiers flags: Shift = 1; Ctrl = 2; Alt = 4;
	'''
	MOD_KEYS = set([
		Keys.KEY_LSHIFT,
		Keys.KEY_RSHIFT,
		Keys.KEY_LCONTROL,
		Keys.KEY_RCONTROL,
		Keys.KEY_LALT,
		Keys.KEY_RALT
	])
	MOD_FLAGS = set([
		Keys.MODIFIER_SHIFT,
		Keys.MODIFIER_CTRL,
		Keys.MODIFIER_ALT
	])
	MOD_KEY2FLAG = {
		Keys.KEY_LSHIFT: Keys.MODIFIER_SHIFT,
		Keys.KEY_RSHIFT: Keys.MODIFIER_SHIFT,
		Keys.KEY_LCONTROL: Keys.MODIFIER_CTRL,
		Keys.KEY_RCONTROL: Keys.MODIFIER_CTRL,
		Keys.KEY_LALT: Keys.MODIFIER_ALT,
		Keys.KEY_RALT: Keys.MODIFIER_ALT
	}
	MOD_FLAG2KEY = {
		Keys.MODIFIER_SHIFT: (Keys.KEY_LSHIFT, Keys.KEY_RSHIFT),
		Keys.MODIFIER_CTRL: (Keys.KEY_LCONTROL, Keys.KEY_RCONTROL),
		Keys.MODIFIER_ALT: (Keys.KEY_LALT, Keys.KEY_RALT)
	}
	MOD_PAIRS = {
		Keys.KEY_LSHIFT: Keys.KEY_RSHIFT,
		Keys.KEY_RSHIFT: Keys.KEY_LSHIFT,
		Keys.KEY_LCONTROL: Keys.KEY_RCONTROL,
		Keys.KEY_RCONTROL: Keys.KEY_LCONTROL,
		Keys.KEY_LALT: Keys.KEY_RALT,
		Keys.KEY_RALT: Keys.KEY_LALT,
	}

	@staticmethod
	def keyToString(key):
		key = BigWorld.keyToString(key)
		if not key:
			raise LookupError('Key could not be recognized.')
		return 'KEY_' + key

	@classmethod
	def parseEvent(sclass, event):
		'''
		parseEvent(event) -> key, isDown, isRepeat, modifiers
		'''
		return (
			event.key,
			event.isKeyDown(),
			event.isRepeatedEvent(),
			event.modifiers & ~(sclass.MOD_KEY2FLAG[event.key] if event.key in sclass.MOD_KEYS and not BigWorld.isKeyDown(sclass.MOD_PAIRS[event.key]) else 0x0)
		)

	@classmethod
	def parseSequence(sclass, sequence):
		'''
		parseSequence(sequence) -> key, modifiers
		'''
		sequence = map(lambda key: getattr(Keys, key, None), sequence.split('+'))
		if None in sequence:
			raise LookupError('One or more keys could not be recognized.')
		key, modifiers = sequence.pop(), set(sequence)
		if modifiers - sclass.MOD_KEYS:
			raise LookupError('Only Shift, Ctrl and Alt could be modifiers.')
		return (
			key if key is not Keys.KEY_NONE else -1,
			sum(set(map(lambda modifier: sclass.MOD_KEY2FLAG[modifier], modifiers)))
		)

	@classmethod
	def buildSequence(sclass, key, modifiers):
		return '+'.join(map(sclass.keyToString, [sclass.MOD_FLAG2KEY[flag][0] for flag in sclass.MOD_FLAGS if modifiers & flag] + [key]))
