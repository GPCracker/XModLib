# Authors: GPCracker

# *************************
# Python
# *************************
# Nothing

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
from .XMLConfigReader import XMLConfigReader, ListXMLReader

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
