# Authors: GPCracker

# *************************
# Python
# *************************
import os.path
import weakref
import itertools

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
# Nothing

class XMLReaderMeta(object):
	__slots__ = ('readerName', 'collectionProxy')

	@classmethod
	def _constructClass(cls, className, **kwargs):
		return type(className, (cls, ), kwargs)

	@staticmethod
	def _iterXmlSectionItems(xmlSection):
		for nestedName, nestedXmlSection in xmlSection.items():
			if not nestedXmlSection.isAttribute:
				yield nestedName, nestedXmlSection
		return

	@staticmethod
	def _iterXmlSectionAttributes(xmlSection):
		for nestedName, nestedXmlSection in xmlSection.items():
			if nestedXmlSection.isAttribute:
				yield nestedName, nestedXmlSection
		return

	def __init__(self, readerName, collectionProxy):
		super(XMLReaderMeta, self).__init__()
		self.readerName = readerName
		self.collectionProxy = collectionProxy
		return

	def _readNestedSection(self, xmlSection, defItem):
		return self.collectionProxy(xmlSection, defItem)

	def _readSection(self, xmlSection, defSection, **kwargs):
		raise NotImplementedError
		return None

	def __call__(self, xmlSection, defSection, **kwargs):
		return self._readSection(xmlSection, defSection, **kwargs)

	def __repr__(self):
		return '{}(readerName={!r}, collectionProxy={!r})'.format(self.__class__.__name__, self.readerName, self.collectionProxy)

	def __del__(self):
		return

class InternalXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, className):
		return cls._constructClass(className)

	def _readSection(self, xmlSection, defSection):
		return defSection

class ResMgrXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, className):
		return cls._constructClass(className)

	def _readSection(self, xmlSection, defSection):
		return getattr(xmlSection, 'as' + self.readerName) if xmlSection is not None else defSection

class VectorAsTupleXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, className, vectorType='Vector2'):
		return cls._constructClass(className, vectorType=vectorType)

	def _readSection(self, xmlSection, defSection):
		if getattr(self, 'vectorType', None) is None:
			raise AttributeError('Vector type is undefined or None.')
		return getattr(xmlSection, 'as' + self.vectorType).tuple() if xmlSection is not None else defSection

class LocalizedWideStringXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, className, translator=None):
		translator = staticmethod(translator if translator is not None else lambda string: string)
		return cls._constructClass(className, translator=translator)

	def _readSection(self, xmlSection, defSection):
		if getattr(self, 'translator', None) is None:
			raise AttributeError('Translator is undefined or None.')
		return self.translator(getattr(xmlSection, 'asWideString') if xmlSection is not None else defSection)

class AttributeBasedXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, className):
		return cls._constructClass(className)

	def _readSection(self, xmlSection, defSection):
		if xmlSection is not None:
			reader = xmlSection['reader']
			if reader is None or not reader.isAttribute:
				raise TypeError('Expected \'reader\' attribute does not exist or has invalid value.')
			return self.collectionProxy[reader.asString](xmlSection, defSection)
		return defSection

class DictXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, className):
		return cls._constructClass(className)

	def _readSection(self, xmlSection, defSection):
		return {nestedName: self._readNestedSection(xmlSection[nestedName] if xmlSection is not None else None, defSection[nestedName]) for nestedName in defSection.iterkeys()}

class ListXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, className, itemName='item', itemType='String', itemDefault=''):
		return cls._constructClass(className, itemName=itemName, itemType=itemType, itemDefault=itemDefault)

	def _readSection(self, xmlSection, defSection):
		if getattr(self, 'itemName', None) is None:
			raise AttributeError('Item name is undefined or None.')
		if getattr(self, 'itemType', None) is None:
			raise AttributeError('Item type is undefined or None.')
		if getattr(self, 'itemDefault', None) is None:
			raise AttributeError('Item default value is undefined or None.')
		if xmlSection is not None:
			return [self._readNestedSection(nestedXmlSection, (self.itemType, self.itemDefault)) for nestedName, nestedXmlSection in self._iterXmlSectionItems(xmlSection) if nestedName == self.itemName]
		return [self._readNestedSection(None, (self.itemType, defItem)) for defItem in defSection]

class CustomDictXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, className, itemType='String', itemDefault=''):
		return cls._constructClass(className, itemType=itemType, itemDefault=itemDefault)

	def _readSection(self, xmlSection, defSection):
		if getattr(self, 'itemType', None) is None:
			raise AttributeError('Item type is undefined or None.')
		if getattr(self, 'itemDefault', None) is None:
			raise AttributeError('Item default value is undefined or None.')
		if xmlSection is not None:
			return {nestedName: self._readNestedSection(nestedXmlSection, (self.itemType, self.itemDefault)) for nestedName, nestedXmlSection in self._iterXmlSectionItems(xmlSection)}
		return {nestedName: self._readNestedSection(None, (self.itemType, defItem)) for nestedName, defItem in defSection.iteritems()}

class OptionalDictXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, className, requiredKeys=(), defaultKeys=()):
		return cls._constructClass(className, requiredKeys=requiredKeys, defaultKeys=defaultKeys)

	def _readSection(self, xmlSection, defSection):
		if getattr(self, 'requiredKeys', None) is None:
			raise AttributeError('Required keys are undefined or None.')
		if getattr(self, 'defaultKeys', None) is None:
			raise AttributeError('Default keys are undefined or None.')
		if xmlSection is not None:
			return {nestedName: self._readNestedSection(xmlSection[nestedName], defSection[nestedName]) for nestedName in defSection.iterkeys() if nestedName in self.requiredKeys or xmlSection[nestedName] is not None}
		return {nestedName: self._readNestedSection(None, defSection[nestedName]) for nestedName in defSection.iterkeys() if nestedName in self.requiredKeys or nestedName in self.defaultKeys}

class DataObjectXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, className, constructor=None, sectionType='String'):
		constructor = staticmethod(constructor if constructor is not None else lambda data: data)
		return cls._constructClass(className, constructor=constructor, sectionType=sectionType)

	def _readSection(self, xmlSection, defSection, **kwargs):
		if getattr(self, 'constructor', None) is None:
			raise AttributeError('Constructor is undefined or None.')
		if getattr(self, 'sectionType', None) is None:
			raise AttributeError('Section type is undefined or None.')
		return self.constructor(self._readNestedSection(xmlSection, (self.sectionType, defSection)), **kwargs)

class XMLReaderCollection(dict):
	__slots__ = ('__weakref__', )

	RESMGR_TYPES = (
		('Binary', ResMgrXMLReaderMeta.construct('BinaryXMLReader')),
		('Blob', ResMgrXMLReaderMeta.construct('BlobXMLReader')),
		('Bool', ResMgrXMLReaderMeta.construct('BoolXMLReader')),
		('Float', ResMgrXMLReaderMeta.construct('FloatXMLReader')),
		('Int', ResMgrXMLReaderMeta.construct('IntXMLReader')),
		('Int64', ResMgrXMLReaderMeta.construct('Int64XMLReader')),
		('Matrix', ResMgrXMLReaderMeta.construct('MatrixXMLReader')),
		('String', ResMgrXMLReaderMeta.construct('StringXMLReader')),
		('Vector2', ResMgrXMLReaderMeta.construct('Vector2XMLReader')),
		('Vector3', ResMgrXMLReaderMeta.construct('Vector3XMLReader')),
		('Vector4', ResMgrXMLReaderMeta.construct('Vector4XMLReader')),
		('WideString', ResMgrXMLReaderMeta.construct('WideStringXMLReader'))
	)
	READER_TYPES = (
		('Dict', DictXMLReaderMeta.construct('DictXMLReader')),
		('Internal', InternalXMLReaderMeta.construct('InternalXMLReader')),
		('Vector2AsTuple', VectorAsTupleXMLReaderMeta.construct('Vector2AsTupleXMLReader', 'Vector2')),
		('Vector3AsTuple', VectorAsTupleXMLReaderMeta.construct('Vector3AsTupleXMLReader', 'Vector3')),
		('Vector4AsTuple', VectorAsTupleXMLReaderMeta.construct('Vector4AsTupleXMLReader', 'Vector4'))
	)

	XML_GOOD = 'good'
	XML_MISSING = 'missing'
	XML_CORRUPTED = 'corrupted'

	@classmethod
	def openSection(cls, xmlPath, skipMissing=True):
		status, breakpoint = cls._testXmlPath(xmlPath)
		if status == cls.XML_CORRUPTED:
			raise RuntimeError('ResMgr path \'{}\' is based on corrupted data file \'{}\'.'.format(xmlPath, breakpoint))
		elif status == cls.XML_MISSING and not skipMissing:
			raise RuntimeError('ResMgr path \'{}\' is based on missing data file. Breakpoint at \'{}\'.'.format(xmlPath, breakpoint))
		return ResMgr.openSection(xmlPath)

	@classmethod
	def _testXmlPath(cls, xmlPath):
		if ResMgr.isFile(xmlPath):
			if ResMgr.openSection(xmlPath) is None:
				return cls.XML_CORRUPTED, xmlPath
			return cls.XML_GOOD, xmlPath
		if ResMgr.isDir(xmlPath):
			return cls.XML_MISSING, xmlPath
		return cls._testXmlPath(os.path.normpath(os.path.join(xmlPath, '../')).replace(os.sep, '/'))

	@classmethod
	def _overrideSection(cls, xmlSection):
		override = xmlSection['override'] if xmlSection is not None else None
		if override is not None and override.isAttribute:
			xmlSection = cls._overrideSection(cls.openSection(override.asString))
		return xmlSection

	def __init__(self, customTypes=()):
		super(XMLReaderCollection, self).__init__()
		self.update(itertools.starmap(
			lambda readerName, readerClass: (readerName, readerClass(readerName, weakref.proxy(self))),
			itertools.chain(self.RESMGR_TYPES, self.READER_TYPES, customTypes)
		))
		return

	def __new__(cls, *args, **kwargs):
		return super(XMLReaderCollection, cls).__new__(cls)

	def _parseDefaultItem(self, defItem):
		if isinstance(defItem, dict):
			return 'Dict', defItem, dict()
		if not isinstance(defItem, (list, tuple)):
			raise TypeError('Invalid default config item type.')
		if len(defItem) == 3:
			readerName, defSection, kwargs = defItem
		elif len(defItem) == 2:
			(readerName, defSection), kwargs = defItem, dict()
		else:
			raise ValueError('Invalid default config item length.')
		return readerName, defSection, kwargs

	def __call__(self, xmlSection, defItem):
		readerName, defSection, kwargs = self._parseDefaultItem(defItem)
		if xmlSection is not None and xmlSection.isAttribute:
			xmlSection = None
		return self[readerName](self._overrideSection(xmlSection), defSection, **kwargs)

	def __repr__(self):
		return '{}:{}'.format(object.__repr__(self), super(XMLReaderCollection, self).__repr__())

class XMLConfigReader(XMLReaderCollection):
	pass
