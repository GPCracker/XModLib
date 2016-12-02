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
	__slots__ = ('reader_name', 'collection_proxy')

	@classmethod
	def _construct_class(sclass, class_name, **kwargs):
		return type(class_name, (sclass, ), kwargs)

	@staticmethod
	def _iter_xml_section_items(xml_section):
		for nested_name, nested_xml_section in xml_section.items():
			if not nested_xml_section.isAttribute:
				yield nested_name, nested_xml_section
		return

	@staticmethod
	def _iter_xml_section_attributes(xml_section):
		for nested_name, nested_xml_section in xml_section.items():
			if nested_xml_section.isAttribute:
				yield nested_name, nested_xml_section
		return

	def __init__(self, reader_name, collection_proxy):
		super(XMLReaderMeta, self).__init__()
		self.reader_name = reader_name
		self.collection_proxy = collection_proxy
		return

	def _read_nested_section(self, xml_section, def_item):
		return self.collection_proxy(xml_section, def_item)

	def _read_section(self, xml_section, def_section):
		raise NotImplementedError
		return None

	def __call__(self, xml_section, def_section):
		return self._read_section(xml_section, def_section)

	def __repr__(self):
		return '{}(reader_name={!r}, collection_proxy={!r})'.format(type(self).__name__, self.reader_name, self.collection_proxy)

	def __del__(self):
		return

class InternalXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(sclass, class_name):
		return sclass._construct_class(class_name)

	def _read_section(self, xml_section, def_section):
		return def_section

class ResMgrXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(sclass, class_name):
		return sclass._construct_class(class_name)

	def _read_section(self, xml_section, def_section):
		return getattr(xml_section, 'as' + self.reader_name) if xml_section is not None else def_section

class VectorAsTupleXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(sclass, class_name, vector_type='Vector2'):
		return sclass._construct_class(class_name, vector_type=vector_type)

	def _read_section(self, xml_section, def_section):
		if getattr(self, 'vector_type', None) is None:
			raise AttributeError('Vector type is undefined or None.')
		return getattr(xml_section, 'as' + self.vector_type).tuple() if xml_section is not None else def_section

class LocalizedWideStringXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(sclass, class_name, translator=None):
		translator = staticmethod(translator if translator is not None else lambda string: string)
		return sclass._construct_class(class_name, translator=translator)

	def _read_section(self, xml_section, def_section):
		if getattr(self, 'translator', None) is None:
			raise AttributeError('Translator is undefined or None.')
		return self.translator(getattr(xml_section, 'asWideString') if xml_section is not None else def_section)

class AttributeBasedXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(sclass, class_name):
		return sclass._construct_class(class_name)

	def _read_section(self, xml_section, def_section):
		if xml_section is not None:
			reader = xml_section['reader']
			if reader is None or not reader.isAttribute:
				raise TypeError('Expected \'reader\' attribute does not exist or has invalid value.')
			return self.collection_proxy[reader.asString](xml_section, def_section)
		return def_section

class DictXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(sclass, class_name):
		return sclass._construct_class(class_name)

	def _read_section(self, xml_section, def_section):
		return {nested_name: self._read_nested_section(xml_section[nested_name] if xml_section is not None else None, def_section[nested_name]) for nested_name in def_section.iterkeys()}

class ListXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(sclass, class_name, item_name='item', item_type='String', item_default=''):
		return sclass._construct_class(class_name, item_name=item_name, item_type=item_type, item_default=item_default)

	def _read_section(self, xml_section, def_section):
		if getattr(self, 'item_name', None) is None:
			raise AttributeError('Item name is undefined or None.')
		if getattr(self, 'item_type', None) is None:
			raise AttributeError('Item type is undefined or None.')
		if getattr(self, 'item_default', None) is None:
			raise AttributeError('Item default value is undefined or None.')
		if xml_section is not None:
			return [self._read_nested_section(nested_xml_section, (self.item_type, self.item_default)) for nested_name, nested_xml_section in self._iter_xml_section_items(xml_section) if nested_name == self.item_name]
		return [self._read_nested_section(None, (self.item_type, def_item)) for def_item in def_section]

class CustomDictXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(sclass, class_name, item_type='String', item_default=''):
		return sclass._construct_class(class_name, item_type=item_type, item_default=item_default)

	def _read_section(self, xml_section, def_section):
		if getattr(self, 'item_type', None) is None:
			raise AttributeError('Item type is undefined or None.')
		if getattr(self, 'item_default', None) is None:
			raise AttributeError('Item default value is undefined or None.')
		if xml_section is not None:
			return {nested_name: self._read_nested_section(nested_xml_section, (self.item_type, self.item_default)) for nested_name, nested_xml_section in self._iter_xml_section_items(xml_section)}
		return {nested_name: self._read_nested_section(None, (self.item_type, def_item)) for nested_name, def_item in def_section.iteritems()}

class OptionalDictXMLReaderMeta(XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(sclass, class_name, required_keys=(), default_keys=()):
		return sclass._construct_class(class_name, required_keys=required_keys, default_keys=default_keys)

	def _read_section(self, xml_section, def_section):
		if getattr(self, 'required_keys', None) is None:
			raise AttributeError('Required keys are undefined or None.')
		if getattr(self, 'default_keys', None) is None:
			raise AttributeError('Default keys are undefined or None.')
		if xml_section is not None:
			return {nested_name: self._read_nested_section(xml_section[nested_name], def_section[nested_name]) for nested_name in def_section.iterkeys() if nested_name in self.required_keys or xml_section[nested_name] is not None}
		return {nested_name: self._read_nested_section(None, def_section[nested_name]) for nested_name in def_section.iterkeys() if nested_name in self.required_keys or nested_name in self.default_keys}

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
		('Internal', InternalXMLReaderMeta.construct('InternalXMLReader'))
	)

	XML_GOOD = 'good'
	XML_MISSING = 'missing'
	XML_CORRUPTED = 'corrupted'

	@classmethod
	def open_section(sclass, xml_path, skip_missing=True):
		status, breakpoint = sclass._test_xml_path(xml_path)
		if status == sclass.XML_CORRUPTED:
			raise RuntimeError('ResMgr path \'{}\' is based on corrupted data file \'{}\'.'.format(xml_path, breakpoint))
		elif status == sclass.XML_MISSING and not skip_missing:
			raise RuntimeError('ResMgr path \'{}\' is based on missing data file. Breakpoint at \'{}\'.'.format(xml_path, breakpoint))
		return ResMgr.openSection(xml_path)

	@classmethod
	def _test_xml_path(sclass, xml_path):
		if ResMgr.isFile(xml_path):
			if ResMgr.openSection(xml_path) is None:
				return sclass.XML_CORRUPTED, xml_path
			return sclass.XML_GOOD, xml_path
		if ResMgr.isDir(xml_path):
			return sclass.XML_MISSING, xml_path
		return sclass._test_xml_path(os.path.normpath(os.path.join(xml_path, '../')).replace(os.sep, '/'))

	@classmethod
	def _override_section(sclass, xml_section):
		override = xml_section['override'] if xml_section is not None else None
		if override is not None and override.isAttribute:
			xml_section = sclass._override_section(sclass.open_section(override.asString))
		return xml_section

	def __init__(self, custom_types=()):
		super(XMLReaderCollection, self).__init__()
		self.update(itertools.starmap(
			lambda reader_name, reader_class: (reader_name, reader_class(reader_name, weakref.proxy(self))),
			itertools.chain(self.RESMGR_TYPES, self.READER_TYPES, custom_types)
		))
		return

	def __new__(sclass, *args, **kwargs):
		return super(XMLReaderCollection, sclass).__new__(sclass)

	def _parse_default_item(self, def_item):
		if isinstance(def_item, dict):
			return 'Dict', def_item
		if not isinstance(def_item, (list, tuple)):
			raise TypeError('Invalid default config item type "{}".'.format(type(def_item).__name__))
		return def_item

	def __call__(self, xml_section, def_item):
		reader_name, def_section = self._parse_default_item(def_item)
		if xml_section is not None and xml_section.isAttribute:
			xml_section = None
		return self[reader_name](self._override_section(xml_section), def_section)

	def __repr__(self):
		return '{}:{}'.format(object.__repr__(self), super(XMLReaderCollection, self).__repr__())

class XMLConfigReader(XMLReaderCollection):
	pass
