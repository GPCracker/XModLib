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
# X-Mod Code Library
# *************************
from .ResMgrUtils import ResMgrUtils
from .XMLConfigReader import XMLConfigReader, ListXMLReader

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

class UmlautReplace(tuple):
	def __new__(sclass, iterable):
		result = super(UmlautReplace, sclass).__new__(sclass, iterable)
		if len(result) != 2:
			raise ValueError('Argument must be a length of 2.')
		return result

	def __call__(self, string):
		return string.replace(*self)

	def __repr__(self):
		return 'UmlautReplace({})'.format(super(UmlautReplace, self).__repr__())

class UmlautDecoder(list):
	@classmethod
	def from_xml(sclass, xml):
		xml_config_reader = XMLConfigReader.new({
			'UmlautReplaceList': ListXMLReader.new_class(
				'UmlautReplaceListReader',
				ITEM_NAME = 'umlaut',
				ITEM_TYPE = 'Dict',
				ITEM_DEFAULT = {
					'uml': ('WideString', u''),
					'rpl': ('WideString', u'')
				}
			)
		})
		xml_section = xml if isinstance(xml, ResMgr.DataSection) else xml_config_reader.open_section(xml)
		return sclass(map(lambda umlaut_replace: UmlautReplace((umlaut_replace['uml'], umlaut_replace['rpl'])), xml_config_reader(xml_section, ('UmlautReplaceList', []))))

	def __call__(self, string):
		for umlaut_replace in self:
			string = umlaut_replace(string)
		return string

	def __repr__(self):
		return 'UmlautDecoder({})'.format(super(UmlautDecoder, self).__repr__())

class TranslatorsCache(dict):
	@staticmethod
	def _get_translator(domain):
		path = ResMgrUtils.basepath(ResMgrUtils.join_path('text/LC_MESSAGES', domain + '.mo'))
		return gettext.translation(domain, path, languages=['text'])

	def __missing__(self, domain):
		return self.setdefault(domain, self._get_translator(domain))

	def gettext(self, domain, message):
		return self[domain].gettext(message)

	def __repr__(self):
		return 'TranslatorsCache({})'.format(super(TranslatorsCache, self).__repr__())