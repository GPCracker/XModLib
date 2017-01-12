# Authors: GPCracker

# *************************
# Python
# *************************
import re
import gettext
import collections

# *************************
# BigWorld
# *************************
import ResMgr

# *************************
# WoT Client
# *************************
# Nothing

# *************************
# X-Mod Library
# *************************
from . import EngineUtils

class MacrosFormatter(collections.namedtuple('MacrosFormatter', ('header', 'trailer'))):
	__slots__ = ()

	def __new__(sclass, header='{{', trailer='}}'):
		return super(MacrosFormatter, sclass).__new__(sclass, header, trailer)

	def __call__(self, string, *args, **kwargs):
		header, trailer = re.escape(self.header), re.escape(self.trailer)
		regex = re.compile(header + '(?P<macros>[^{}]*?)' + trailer)
		def replacement(match):
			try:
				return ('{' + match.group('macros') + '}').format(*args, **kwargs)
			except (IndexError, KeyError, ValueError):
				return match.group()
		return regex.sub(replacement, string)

class TranslatorsCache(dict):
	__slots__ = ()

	@staticmethod
	def _getTranslator(domain):
		path = EngineUtils.getResMgrBasePath(EngineUtils.joinResMgrPath('text/LC_MESSAGES', domain + '.mo'))
		return gettext.translation(domain, path, languages=['text'])

	def __missing__(self, domain):
		return self.setdefault(domain, self._getTranslator(domain))

	def gettext(self, domain, message):
		return self[domain].gettext(message)

	def __repr__(self):
		return '{}({})'.format(self.__class__.__name__, super(TranslatorsCache, self).__repr__())

class TranslatorFormatter(collections.namedtuple('TranslatorFormatter', ('cache', 'header', 'delimiter', 'trailer'))):
	__slots__ = ()

	def __new__(sclass, cache, header='#', delimiter=':', trailer=';'):
		return super(TranslatorFormatter, sclass).__new__(sclass, cache, header, delimiter, trailer)

	def __call__(self, string):
		header, delimiter, trailer = re.escape(self.header), re.escape(self.delimiter), re.escape(self.trailer)
		regex = re.compile(header + '(?P<domain>\w+?)' + delimiter + '(?P<message>(?:\w+?)(?:/\w+?)*?)' + trailer)
		def replacement(match):
			domain, message = match.group('domain', 'message')
			text = self.cache.gettext(domain, message)
			return text if text != message else match.group()
		return regex.sub(replacement, string)
