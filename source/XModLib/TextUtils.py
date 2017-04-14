# Authors: GPCracker

# *************************
# Python
# *************************
import io
import re
import errno
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

class TranslationFile(io.BytesIO):
	__slots__ = ('_filename', )

	name = property(lambda self: self._filename)

	def __new__(sclass, content=b'', filename='<string>'):
		return super(TranslationFile, sclass).__new__(sclass, content)

	def __init__(self, content=b'', filename='<string>'):
		super(TranslationFile, self).__init__(content)
		self._filename = filename
		return

class TranslatorsCache(dict):
	__slots__ = ()

	@staticmethod
	def _getTranslator(domain):
		content = EngineUtils.getResMgrBinaryFileContent(EngineUtils.joinResMgrPath('text/lc_messages', domain + '.mo'))
		if content is None:
			raise IOError(errno.ENOENT, 'No translation file found for domain', domain)
		with TranslationFile(content) as fakefile:
			translation = gettext.GNUTranslations(fakefile)
		return translation

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
