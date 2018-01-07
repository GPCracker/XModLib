# Authors: Vladislav Ignatenko <gpcracker@mail.ru>

# ------------ #
#    Python    #
# ------------ #
import sys
import enum
import types
import os.path
import weakref
import operator
import itertools

# -------------- #
#    BigWorld    #
# -------------- #
import ResMgr

# ---------------- #
#    WoT Client    #
# ---------------- #
# nothing

# ------------------- #
#    X-Mod Library    #
# ------------------- #
from . import TextUtils
from . import EngineUtils

# -------------------- #
#    Module Content    #
# -------------------- #
class SlotsMetaclass(type):
	__slots__ = ()

	def __new__(cls, name, bases, dct):
		slots = dct.setdefault('__slots__', ())
		return super(SlotsMetaclass, cls).__new__(cls, name, bases, dct)

class FinalMetaclass(type):
	__slots__ = ()

	def __new__(cls, name, bases, dct):
		for base in bases:
			if isinstance(base, FinalMetaclass):
				raise TypeError('type {!r} is not an acceptable base type'.format(base.__name__))
		return super(FinalMetaclass, cls).__new__(cls, name, bases, dct)

class XMLReaderArgsMetaclass(SlotsMetaclass):
	__slots__ = ()

	def __new__(cls, name, bases, dct):
		if not issubclass(cls, XMLReaderArgsFinalMetaclass):
			if any(isinstance(base, XMLReaderArgsMetaclass) for base in bases):
				raise TypeError('the metaclass of a derived class must be a subclass of XMLReaderArgsFinalMetaclass')
		return super(XMLReaderArgsMetaclass, cls).__new__(cls, name, bases, dct)

class XMLReaderArgsFinalMetaclass(FinalMetaclass, XMLReaderArgsMetaclass):
	__slots__ = ()

	def __new__(cls, name, bases, dct):
		fields = dct.setdefault('_fields', ())
		if any(field.startswith('_') for field in fields):
			raise ValueError('field names can not start with an underscore')
		dct.update(itertools.starmap(lambda index, field: (field, property(operator.itemgetter(index))), enumerate(fields)))
		return super(XMLReaderArgsFinalMetaclass, cls).__new__(cls, name, bases, dct)

class XMLReaderArgs(tuple):
	__metaclass__ = XMLReaderArgsMetaclass
	__slots__ = ()

	@classmethod
	def _subclass(cls, name, **kwargs):
		return XMLReaderArgsFinalMetaclass(name, (cls, ), kwargs)

	def __new__(cls, **kwargs):
		if not isinstance(cls, XMLReaderArgsFinalMetaclass):
			cls = cls._subclass(cls.__name__, _fields=tuple(sorted(kwargs)))
		arg = next(iter(kwargs.viewkeys() - set(cls._fields)), None)
		if arg is not None:
			raise TypeError('__new__() got an unexpected keyword argument {!r}'.format(arg))
		arg = next(iter(set(cls._fields) - kwargs.viewkeys()), None)
		if arg is not None:
			raise TypeError('__new__() did not get an expected keyword argument {!r}'.format(arg))
		return super(XMLReaderArgs, cls).__new__(cls, itertools.imap(kwargs.get, cls._fields))

	def __repr__(self):
		args = itertools.imap('{!s}={!r}'.format, self._fields, self)
		return '{!s}({!s})'.format(self.__class__.__name__, ', '.join(args))

class XMLReaderMetaclass(SlotsMetaclass):
	__slots__ = ()

class XMLReaderFinalMetaclass(FinalMetaclass, XMLReaderMetaclass):
	__slots__ = ()

class XMLReaderMeta(object):
	__metaclass__ = XMLReaderMetaclass
	__slots__ = ('_collection', '_typename')

	@classmethod
	def _subclass(cls, name, **kwargs):
		return XMLReaderFinalMetaclass(name, (cls, ), kwargs)

	@classmethod
	def construct(cls, classname):
		return cls._subclass(classname)

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

	typename = property(lambda self: self._typename)

	def __new__(cls, collection, typename):
		if not isinstance(cls, XMLReaderFinalMetaclass):
			raise TypeError('{!s} can not be instantiated'.format(cls.__name__))
		if not isinstance(collection, XMLReaderCollection):
			raise TypeError('collection argument must be XMLReaderCollection, not {!s}'.format(type(collection).__name__))
		if not isinstance(typename, basestring):
			raise TypeError('typename argument must be string, not {!s}'.format(type(typename).__name__))
		reader = super(XMLReaderMeta, cls).__new__(cls)
		reader._collection = weakref.proxy(collection)
		reader._typename = typename
		return reader

	def _readNestedSection(self, xmlSection, defItem):
		return self._collection(xmlSection, defItem)

	def _readSection(self, xmlSection, defSection, **kwargs):
		raise NotImplementedError
		return None

	def __call__(self, xmlSection, defSection, **kwargs):
		return self._readSection(xmlSection, defSection, **kwargs)

	def __repr__(self):
		return '<{!s} [collection={!r}, typename={!r}]>'.format(object.__repr__(self).strip('<>'), self._collection, self._typename)

class XMLReaderExtMetaclass(XMLReaderMetaclass):
	__slots__ = ()

class XMLReaderExtFinalMetaclass(XMLReaderFinalMetaclass, XMLReaderExtMetaclass):
	__slots__ = ()

	args = property(lambda self: self._args)

	def __new__(cls, name, bases, dct):
		args = dct.setdefault('_args', XMLReaderArgs())
		if not isinstance(args, XMLReaderArgs):
			raise TypeError('args property must be XMLReaderArgs, not {!s}'.format(type(args).__name__))
		return super(XMLReaderExtFinalMetaclass, cls).__new__(cls, name, bases, dct)

class XMLReaderExtMeta(XMLReaderMeta):
	__metaclass__ = XMLReaderExtMetaclass
	__slots__ = ()

	args = property(lambda self: self._args)

	@classmethod
	def _subclass(cls, name, **kwargs):
		return XMLReaderExtFinalMetaclass(name, (cls, ), kwargs)

	@classmethod
	def _construct(cls, classname, **kwargs):
		return cls._subclass(classname, _args=XMLReaderArgs(**kwargs))

	@classmethod
	def construct(cls, classname):
		return cls._construct(classname)

class InternalXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	def _readSection(self, xmlSection, defSection):
		return defSection

class ResMgrXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	def __init__(self, collection, typename):
		super(ResMgrXMLReaderMeta, self).__init__(collection, typename)
		if not ResMgrTypes.contains(typename):
			raise ValueError('type {!r} is not an acceptable ResMgr type'.format(typename))
		return

	def _readSection(self, xmlSection, defSection):
		return getattr(xmlSection, 'as' + self._typename) if xmlSection is not None else defSection

class VectorAsTupleXMLReaderMeta(XMLReaderExtMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, classname, vectorType='Vector2'):
		if not isinstance(vectorType, basestring):
			raise TypeError('vectorType argument must be string, not {!s}'.format(type(vectorType).__name__))
		if not ResMgrVectorTypes.contains(vectorType):
			raise ValueError('type {!r} is not an acceptable ResMgrVector type'.format(vectorType))
		return cls._construct(classname, vectorType=vectorType)

	def _readSection(self, xmlSection, defSection):
		return getattr(xmlSection, 'as' + self.args.vectorType).tuple() if xmlSection is not None else defSection

class FormattedWideStringXMLReaderMeta(XMLReaderExtMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, classname, formatter=lambda string: string):
		if not callable(formatter):
			raise TypeError('formatter argument must be callable, not {!s}'.format(type(formatter).__name__))
		return cls._construct(classname, formatter=formatter)

	def _readSection(self, xmlSection, defSection):
		return self.args.formatter(xmlSection.asWideString if xmlSection is not None else defSection)

class LocalizedWideStringXMLReaderMeta(XMLReaderExtMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, classname, translator=lambda string: string):
		if not callable(translator):
			raise TypeError('translator argument must be callable, not {!s}'.format(type(translator).__name__))
		return cls._construct(classname, translator=translator)

	def _readSection(self, xmlSection, defSection):
		return self.args.translator(xmlSection.asWideString if xmlSection is not None else defSection)

class AttributeBasedXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	def _readSection(self, xmlSection, defSection):
		if xmlSection is not None:
			reader = xmlSection['reader']
			if reader is None or not reader.isAttribute:
				raise TypeError('Expected \'reader\' attribute does not exist or has invalid value')
			return self._collection[reader.asString](xmlSection, defSection)
		return defSection

class DictXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	def _readSection(self, xmlSection, defSection):
		return {nestedName: self._readNestedSection(xmlSection[nestedName] if xmlSection is not None else None, defSection[nestedName]) for nestedName in defSection.viewkeys()}

class ListXMLReaderMeta(XMLReaderExtMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, classname, itemName='item', itemType='String', itemDefault=''):
		if not isinstance(itemName, basestring):
			raise TypeError('itemName argument must be string, not {!s}'.format(type(itemName).__name__))
		if not isinstance(itemType, basestring):
			raise TypeError('itemType argument must be string, not {!s}'.format(type(itemType).__name__))
		if not isinstance(itemDefault, basestring):
			raise TypeError('itemDefault argument must be string, not {!s}'.format(type(itemDefault).__name__))
		return cls._construct(classname, itemName=itemName, itemType=itemType, itemDefault=itemDefault)

	def _readSection(self, xmlSection, defSection):
		if xmlSection is not None:
			return [self._readNestedSection(nestedXmlSection, (self.args.itemType, self.args.itemDefault)) for nestedName, nestedXmlSection in self._iterXmlSectionItems(xmlSection) if nestedName == self.args.itemName]
		return [self._readNestedSection(None, (self.args.itemType, defItem)) for defItem in defSection]

class CustomDictXMLReaderMeta(XMLReaderExtMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, classname, itemType='String', itemDefault=''):
		if not isinstance(itemType, basestring):
			raise TypeError('itemType argument must be string, not {!s}'.format(type(itemType).__name__))
		if not isinstance(itemDefault, basestring):
			raise TypeError('itemDefault argument must be string, not {!s}'.format(type(itemDefault).__name__))
		return cls._construct(classname, itemType=itemType, itemDefault=itemDefault)

	def _readSection(self, xmlSection, defSection):
		if xmlSection is not None:
			return {nestedName: self._readNestedSection(nestedXmlSection, (self.args.itemType, self.args.itemDefault)) for nestedName, nestedXmlSection in self._iterXmlSectionItems(xmlSection)}
		return {nestedName: self._readNestedSection(None, (self.args.itemType, defItem)) for nestedName, defItem in defSection.viewitems()}

class OptionalDictXMLReaderMeta(XMLReaderExtMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, classname, requiredKeys=(), defaultKeys=()):
		if not isinstance(requiredKeys, (tuple, frozenset)):
			raise TypeError('requiredKeys argument must be tuple, not {!s}'.format(type(requiredKeys).__name__))
		if not isinstance(defaultKeys, (tuple, frozenset)):
			raise TypeError('defaultKeys argument must be tuple, not {!s}'.format(type(defaultKeys).__name__))
		return cls._construct(classname, requiredKeys=requiredKeys, defaultKeys=defaultKeys)

	def _readSection(self, xmlSection, defSection):
		if xmlSection is not None:
			return {nestedName: self._readNestedSection(xmlSection[nestedName], defSection[nestedName]) for nestedName in defSection.viewkeys() if nestedName in self.args.requiredKeys or xmlSection[nestedName] is not None}
		return {nestedName: self._readNestedSection(None, defSection[nestedName]) for nestedName in defSection.viewkeys() if nestedName in itertools.chain(self.args.requiredKeys, self.args.defaultKeys)}

class StringEnumXMLReaderMeta(XMLReaderExtMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, classname, enumeration=lambda string: string):
		if not callable(enumeration):
			raise TypeError('enumeration argument must be callable, not {!s}'.format(type(enumeration).__name__))
		return cls._construct(classname, enumeration=enumeration)

	def _readSection(self, xmlSection, defSection):
		return self.args.enumeration(xmlSection.asString if xmlSection is not None else defSection)

class DataObjectXMLReaderMeta(XMLReaderExtMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, classname, constructor=lambda data: data, sectionType='String'):
		if not callable(constructor):
			raise TypeError('constructor argument must be callable, not {!s}'.format(type(constructor).__name__))
		if not isinstance(sectionType, basestring):
			raise TypeError('sectionType argument must be string, not {!s}'.format(type(sectionType).__name__))
		return cls._construct(classname, constructor=constructor, sectionType=sectionType)

	def _readSection(self, xmlSection, defSection, **kwargs):
		return self.args.constructor(self._readNestedSection(xmlSection, (self.args.sectionType, defSection)), **kwargs)

class ExternalSectionXMLReaderMeta(XMLReaderExtMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, classname, externalSection=None, sectionType='String'):
		if not isinstance(externalSection, (ResMgr.DataSection, types.NoneType)):
			raise TypeError('externalSection argument must be DataSection, not {!s}'.format(type(externalSection).__name__))
		if not isinstance(sectionType, basestring):
			raise TypeError('sectionType argument must be string, not {!s}'.format(type(sectionType).__name__))
		return cls._construct(classname, externalSection=externalSection, sectionType=sectionType)

	def _readSection(self, xmlSection, defSection):
		return self._collection[self.args.sectionType](self.args.externalSection, defSection)

class ResMgrTypesEnum(enum.Enum):
	@classmethod
	def contains(cls, value):
		return value in (item.value for item in cls)

class ResMgrTypes(ResMgrTypesEnum):
	BINARY = 'Binary'
	BLOB = 'Blob'
	BOOL = 'Bool'
	FLOAT = 'Float'
	INT = 'Int'
	INT64 = 'Int64'
	MATRIX = 'Matrix'
	STRING = 'String'
	VECTOR2 = 'Vector2'
	VECTOR3 = 'Vector3'
	VECTOR4 = 'Vector4'
	WIDESTRING = 'WideString'

class ResMgrVectorTypes(ResMgrTypesEnum):
	VECTOR2 = 'Vector2'
	VECTOR3 = 'Vector3'
	VECTOR4 = 'Vector4'

class XMLSectionStatus(enum.Enum):
	DIRECTORY = 'directory'
	CORRUPTED = 'corrupted'
	MISSING = 'missing'
	NORMAL = 'normal'

class XMLSectionError(enum.Enum):
	STRICT = 'strict'
	NOTICE = 'notice'
	IGNORE = 'ignore'

def testXmlPath(xmlPath):
	if ResMgr.isFile(xmlPath):
		if ResMgr.openSection(xmlPath) is None:
			return XMLSectionStatus.CORRUPTED, xmlPath
		return XMLSectionStatus.NORMAL, xmlPath
	elif ResMgr.isDir(xmlPath):
		return XMLSectionStatus.DIRECTORY, xmlPath
	xmlDirname = EngineUtils.joinResMgrPath(xmlPath, os.pardir)
	if ResMgr.isDir(xmlDirname):
		return XMLSectionStatus.MISSING, xmlPath
	return testXmlPath(xmlDirname)

def openSection(xmlPath, missing=XMLSectionError.NOTICE, corrupted=XMLSectionError.STRICT):
	status, breakpoint = testXmlPath(xmlPath)
	if status == XMLSectionStatus.CORRUPTED:
		if not isinstance(corrupted, XMLSectionError):
			raise TypeError('corrupted argument must be XMLSectionError, not {!s}'.format(type(corrupted).__name__))
		if corrupted == XMLSectionError.STRICT:
			raise RuntimeError('ResMgr path {!r} is based on a corrupted data file {!r}'.format(xmlPath, breakpoint))
		elif corrupted == XMLSectionError.NOTICE:
			print >> sys.stderr, '{!s}: ResMgr path {!r} is based on a corrupted data file {!r}'.format(__name__, xmlPath, breakpoint)
	elif status == XMLSectionStatus.MISSING:
		if not isinstance(missing, XMLSectionError):
			raise TypeError('missing argument must be XMLSectionError, not {!s}'.format(type(missing).__name__))
		if missing == XMLSectionError.STRICT:
			raise RuntimeError('ResMgr path {!r} is based on a missing data file {!r}'.format(xmlPath, breakpoint))
		elif missing == XMLSectionError.NOTICE:
			print >> sys.stderr, '{!s}: ResMgr path {!r} is based on a missing data file {!r}'.format(__name__, xmlPath, breakpoint)
	return ResMgr.openSection(xmlPath)

def overrideSection(xmlSection, missing=XMLSectionError.NOTICE, corrupted=XMLSectionError.STRICT):
	override = xmlSection['override'] if xmlSection is not None else None
	if override is not None and override.isAttribute:
		xmlSection = openSection(override.asString, missing=missing, corrupted=corrupted)
		xmlSection = overrideSection(xmlSection, missing=missing, corrupted=corrupted)
	return xmlSection

class XMLReaderCollectionMetaclass(SlotsMetaclass):
	__slots__ = ()

class XMLReaderCollection(dict):
	__metaclass__ = XMLReaderCollectionMetaclass
	__slots__ = ('__weakref__', '_missingSections', '_corruptedSections')

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
		('Vector2AsTuple', VectorAsTupleXMLReaderMeta.construct('Vector2AsTupleXMLReader', vectorType='Vector2')),
		('Vector3AsTuple', VectorAsTupleXMLReaderMeta.construct('Vector3AsTupleXMLReader', vectorType='Vector3')),
		('Vector4AsTuple', VectorAsTupleXMLReaderMeta.construct('Vector4AsTupleXMLReader', vectorType='Vector4')),
		('LocalizedWideString', LocalizedWideStringXMLReaderMeta.construct(
			'LocalizedWideStringXMLReader',
			translator=TextUtils.getDefaultTranslationFormatter()
		))
	)

	@classmethod
	def basetypes(cls):
		return tuple(itertools.chain(cls.RESMGR_TYPES, cls.READER_TYPES))

	@classmethod
	def __newobj__(cls, *args, **kwargs):
		base = next((base for base in cls.__mro__ if '__getnewargs__' in base.__dict__), cls)
		obj = base.__new__(cls, *args, **kwargs)
		base.__init__(obj, *args, **kwargs)
		return obj

	missingSections = property(lambda self: self._missingSections)
	corruptedSections = property(lambda self: self._corruptedSections)

	def __init__(self, customTypes=(), missingSections=XMLSectionError.NOTICE, corruptedSections=XMLSectionError.STRICT):
		super(XMLReaderCollection, self).__init__()
		self.extend(itertools.chain(self.basetypes(), customTypes))
		self._missingSections = missingSections
		self._corruptedSections = corruptedSections
		return

	def types(self):
		return tuple((typename, type(reader)) for typename, reader in self.viewitems())

	def extend(self, types):
		self.update((typename, subclass(self, typename)) for typename, subclass in types)
		return

	def extensions(self):
		return tuple(set(self.types()).difference(self.basetypes()))

	def customize(self, extraTypes=()):
		collection = copy.copy(self)
		collection.extend(extraTypes)
		return collection

	def copy(self):
		return copy.copy(self)

	def __getnewargs__(self):
		return self.extensions(), self._missingSections, self._corruptedSections

	def __reduce_ex__(self, protocol=0):
		if protocol < 2:
			raise TypeError('can\'t pickle {!s} objects'.format(type(self).__name__))
		return self.__newobj__, self.__getnewargs__()

	def _parseDefaultItem(self, defItem):
		if isinstance(defItem, dict):
			return 'Dict', defItem, dict()
		if not isinstance(defItem, (list, tuple)):
			raise TypeError('invalid default config item type: {!r}'.format(type(defItem).__name__))
		if len(defItem) == 3:
			typename, defSection, kwargs = defItem
		elif len(defItem) == 2:
			(typename, defSection), kwargs = defItem, dict()
		else:
			raise ValueError('invalid default config item length: {!r}'.format(len(defItem)))
		return typename, defSection, kwargs

	def __missing__(self, typename):
		subclass = dict(self.basetypes())[typename]
		return self.setdefault(typename, subclass(self, typename))

	def __call__(self, xmlSection, defItem):
		typename, defSection, kwargs = self._parseDefaultItem(defItem)
		xmlSection = xmlSection if xmlSection is not None and not xmlSection.isAttribute else None
		xmlSection = overrideSection(xmlSection, missing=self._missingSections, corrupted=self._corruptedSections)
		return self[typename](xmlSection, defSection, **kwargs)

	def __repr__(self):
		return '{!s}(customTypes={!r}, missingSections={!r}, corruptedSections={!r})'.format(
			self.__class__.__name__,
			self.extensions(),
			self._missingSections,
			self._corruptedSections
		)

class XMLConfigReader(XMLReaderCollection):
	__slots__ = ()
