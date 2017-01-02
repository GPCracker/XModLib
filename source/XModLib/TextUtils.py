# Authors: GPCracker

# *************************
# Python
# *************************
import re
import gettext

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
from . import ResMgrUtils
from . import XMLConfigReader

class MacrosFormatter(object):
	__slots__ = ('__weakref__', 'header', 'trailer')

	HEADER = r'\{\{'
	TRAILER = r'\}\}'

	def __init__(self, header=HEADER, trailer=TRAILER):
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

	def __repr__(self):
		return '{}(header={!r}, trailer={!r})'.format(self.__class__.__name__, self.header, self.trailer)

	def __del__(self):
		return

class UmlautReplace(tuple):
	__slots__ = ()

	def __new__(sclass, iterable):
		result = super(UmlautReplace, sclass).__new__(sclass, iterable)
		if len(result) != 2:
			raise ValueError('Argument must be a length of 2.')
		return result

	def __call__(self, string):
		return string.replace(*self)

	def __repr__(self):
		return '{}({})'.format(self.__class__.__name__, super(UmlautReplace, self).__repr__())

class UmlautDecoder(list):
	__slots__ = ()

	@classmethod
	def from_xml(sclass, xml):
		xml_config_reader = XMLConfigReader.XMLConfigReader((
			('UmlautReplaceList', XMLConfigReader.ListXMLReaderMeta.construct(
				'UmlautReplaceListXMLReader',
				item_name='umlaut',
				item_type='Dict',
				item_default={
					'uml': ('WideString', u''),
					'rpl': ('WideString', u'')
				}
			)),
		))
		xml_section = xml if isinstance(xml, ResMgr.DataSection) else xml_config_reader.open_section(xml)
		return sclass(map(lambda umlaut_replace: UmlautReplace((umlaut_replace['uml'], umlaut_replace['rpl'])), xml_config_reader(xml_section, ('UmlautReplaceList', []))))

	def __call__(self, string):
		for umlaut_replace in self:
			string = umlaut_replace(string)
		return string

	def __repr__(self):
		return '{}({})'.format(self.__class__.__name__, super(UmlautDecoder, self).__repr__())

class TranslatorsCache(dict):
	__slots__ = ()

	@staticmethod
	def _get_translator(domain):
		path = ResMgrUtils.basepath(ResMgrUtils.join_path('text/LC_MESSAGES', domain + '.mo'))
		return gettext.translation(domain, path, languages=['text'])

	def __missing__(self, domain):
		return self.setdefault(domain, self._get_translator(domain))

	def gettext(self, domain, message):
		return self[domain].gettext(message)

	def __repr__(self):
		return '{}({})'.format(self.__class__.__name__, super(TranslatorsCache, self).__repr__())

class TranslatorFormatter(object):
	__slots__ = ('__weakref__', 'cache', 'header', 'trailer', 'delimiter')

	HEADER = r'\#'
	TRAILER = r'\;'
	DELIMITER = r'\:'

	def __init__(self, cache, header=HEADER, trailer=TRAILER, delimiter=DELIMITER):
		self.cache = cache
		self.header = header
		self.trailer = trailer
		self.delimiter = delimiter
		return

	def __call__(self, string):
		regex = re.compile(self.header + '(?P<domain>\w+?)' + self.delimiter + '(?P<message>(?:\w+?)(?:/\w+?)*?)' + self.trailer)
		def replacement(match):
			domain, message = match.group('domain', 'message')
			text = self.cache.gettext(domain, message)
			return text if text != message else match.group()
		return regex.sub(replacement, string)

	def __repr__(self):
		return '{}(header={!r}, trailer={!r}, delimiter={!r})'.format(self.__class__.__name__, self.header, self.trailer, self.delimiter)

	def __del__(self):
		return
