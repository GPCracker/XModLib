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
from .ConfigReader import ConfigReader, ListXMLReader

class UmlautReplace(object):
	@classmethod
	def fromDict(sclass, umlautReplace):
		return sclass(**umlautReplace)

	def __init__(self, uml, rpl):
		self.uml = uml
		self.rpl = rpl
		return

	def __call__(self, string):
		return string.replace(self.uml, self.rpl)

	def __del__(self):
		return

class UmlautDecoder(object):
	@classmethod
	def fromXML(sclass, xml):
		xml = xml if isinstance(xml, ResMgr.DataSection) else ResMgr.openSection(xml)
		configReader = ConfigReader({
			'UmlautReplaceList': ListXMLReader.customize(
				'UmlautReplaceListReader',
				ITEM_NAME = 'umlaut',
				ITEM_TYPE = 'Dict',
				ITEM_DEFAULT = {
					'uml': ('WideString', u''),
					'rpl': ('WideString', u'')
				}
			)
		})
		return sclass(map(UmlautReplace.fromDict, configReader.readSection(xml, ('UmlautReplaceList', []))))

	def __init__(self, umlautReplaces = []):
		self.umlautReplaces = umlautReplaces
		return

	def __call__(self, string):
		for umlautReplace in self.umlautReplaces:
			string = umlautReplace(string)
		return string

	def __del__(self):
		return
