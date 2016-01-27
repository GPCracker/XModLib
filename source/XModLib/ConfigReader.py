# Authors: GPCracker

# *************************
# Python
# *************************
import functools
import weakref

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
# Nothing

class XMLReader(object):
	@staticmethod
	def getMethodProxy(method):
		return functools.partial(weakref.proxy(method.im_func), weakref.proxy(method.im_self))

	@classmethod
	def customize(sclass, customXMLReaderName, **kwargs):
		return type(customXMLReaderName, (sclass, ), kwargs)

	def __init__(self, typeName, callback):
		self.typeName = typeName
		self.callback = self.getMethodProxy(callback)
		return

	def __call__(self, xml, default):
		return None

	def __del__(self):
		return

class BasicXMLReader(XMLReader):
	def __init__(self, typeName, callback):
		super(BasicXMLReader, self).__init__(typeName, callback)
		return

	def __call__(self, xml, default):
		return getattr(xml, 'as' + self.typeName) if xml is not None else default

class DictXMLReader(XMLReader):
	def __init__(self, typeName, callback):
		super(DictXMLReader, self).__init__(typeName, callback)
		return

	def __call__(self, xml, default):
		getNestedXML = lambda nestedXMLName: xml[nestedXMLName] if xml is not None else None
		return dict([(nestedXMLName, self.callback(getNestedXML(nestedXMLName), default[nestedXMLName])) for nestedXMLName in default.keys()])

class ListXMLReader(XMLReader):
	ITEM_NAME = 'item'
	ITEM_TYPE = 'String'
	ITEM_DEFAULT = ''

	def __init__(self, typeName, callback):
		super(ListXMLReader, self).__init__(typeName, callback)
		return

	def __call__(self, xml, default):
		if xml is not None:
			return [self.callback(nestedXML, (self.ITEM_TYPE, self.ITEM_DEFAULT)) for nestedXMLName, nestedXML in xml.items() if nestedXMLName == self.ITEM_NAME]
		return [self.callback(None, (self.ITEM_TYPE, defaultItem)) for defaultItem in default]

class CustomDictXMLReader(XMLReader):
	ITEM_TYPE = 'String'
	ITEM_DEFAULT = ''

	def __init__(self, typeName, callback):
		super(CustomDictXMLReader, self).__init__(typeName, callback)
		return

	def __call__(self, xml, default):
		if xml is not None:
			return dict([(nestedXMLName, self.callback(nestedXML, (self.ITEM_TYPE, self.ITEM_DEFAULT))) for nestedXMLName, nestedXML in xml.items()])
		return dict([(nestedXMLName, self.callback(None, (self.ITEM_TYPE, defaultItem))) for nestedXMLName, defaultItem in default.items()])

class ConfigReader(object):
	INITIAL_TYPES = {
		'Binary': BasicXMLReader,
		'Blob': BasicXMLReader,
		'Bool': BasicXMLReader,
		'Float': BasicXMLReader,
		'Int': BasicXMLReader,
		'Int64': BasicXMLReader,
		'Matrix': BasicXMLReader,
		'String': BasicXMLReader,
		'Vector2': BasicXMLReader,
		'Vector3': BasicXMLReader,
		'Vector4': BasicXMLReader,
		'WideString': BasicXMLReader,
		'Dict': DictXMLReader
	}

	def __init__(self, extTypes = {}):
		self.__xmlReaders = dict([(typeName, xmlReaderClass(typeName, self.readSection)) for typeName, xmlReaderClass in self.INITIAL_TYPES.items()])
		self.__xmlReaders.update(dict([(typeName, xmlReaderClass(typeName, self.readSection)) for typeName, xmlReaderClass in extTypes.items()]))
		return

	@property
	def xmlReaders(self):
		return self.__xmlReaders

	def readSection(self, xmlSection, defSection):
		if isinstance(defSection, (list, tuple)):
			sectionType, sectionDefault = defSection
			return self.__xmlReaders[sectionType](xmlSection, sectionDefault)
		elif isinstance(defSection, dict):
			return self.__xmlReaders['Dict'](xmlSection, defSection)
		else:
			raise IOError('Invalid config parameter type "{}".'.format(type(defSection).__name__))
		return None

	def readConfig(self, xmlPath, defConfig):
		return self.readSection(ResMgr.openSection(xmlPath), defConfig)

	def __del__(self):
		return
