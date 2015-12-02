# Authors: GPCracker

import re

class MacrosFormatter(object):
	HEADER = '\{\{'
	TRAILER = '\}\}'

	def __init__(self, header = HEADER, trailer = TRAILER):
		self.header = header
		self.trailer = trailer
		return

	def __call__(self, string, *args, **kwargs):
		regex = re.compile(self.header + '(?P<macros>[^{}]*?)' + self.trailer)
		def replacement(match):
			try:
				return ('{' + match.group('macros') + '}').format(*args, **kwargs)
			except (IndexError, KeyError, ValueError):
				return match.group()
		return regex.sub(replacement, string)

	def __del__(self):
		return
