# Authors: GPCracker

# *************************
# Python
# *************************
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
	@classmethod
	def new_class(sclass, class_name, **kwargs):
		return type(class_name, (sclass, ), kwargs)

	def __init__(self, type_name, reader_collection_proxy):
		self.type_name = type_name
		self.reader_collection_proxy = reader_collection_proxy
		return

	def _override_section(self, xml_section):
		override = xml_section['override'] if xml_section is not None else None
		return self._override_section(self.reader_collection_proxy.open_section(override.asString)) if override is not None and override.isAttribute else xml_section

	def _read_nested_section(self, xml_section, def_item):
		reader_type_name, def_section = self.reader_collection_proxy.parse_default_item(def_item)
		return self.reader_collection_proxy[reader_type_name](xml_section, def_section)

	def _read_section(self, xml_section, def_section):
		raise NotImplementedError
		return None

	def __call__(self, xml_section, def_section):
		return self._read_section(self._override_section(xml_section), def_section)

	def __repr__(self):
		return '{}(type_name={!r}, reader_collection_proxy={!r})'.format(type(self).__name__, self.type_name, self.reader_collection_proxy)

	def __del__(self):
		return

class ResMgrXMLReader(XMLReader):
	def _read_section(self, xml_section, def_section):
		return getattr(xml_section, 'as' + self.type_name) if xml_section is not None else def_section

class DictXMLReader(XMLReader):
	def _read_section(self, xml_section, def_section):
		return {nested_name: self._read_nested_section(xml_section[nested_name] if xml_section is not None else None, def_section[nested_name]) for nested_name in def_section.keys()}

class ListXMLReader(XMLReader):
	ITEM_NAME = 'item'
	ITEM_TYPE = 'String'
	ITEM_DEFAULT = ''

	def _read_section(self, xml_section, def_section):
		return [self._read_nested_section(nested_xml_section, (self.ITEM_TYPE, self.ITEM_DEFAULT)) for nested_name, nested_xml_section in xml_section.items() if nested_name == self.ITEM_NAME] if xml_section is not None else [self._read_nested_section(None, (self.ITEM_TYPE, def_item)) for def_item in def_section]

class CustomDictXMLReader(XMLReader):
	ITEM_TYPE = 'String'
	ITEM_DEFAULT = ''

	def _read_section(self, xml_section, def_section):
		return {nested_name: self._read_nested_section(nested_xml_section, (self.ITEM_TYPE, self.ITEM_DEFAULT)) for nested_name, nested_xml_section in xml_section.items()} if xml_section is not None else {nested_name: self._read_nested_section(None, (self.ITEM_TYPE, def_item)) for nested_name, def_item in def_section.items()}

class XMLReaderClassCollection(dict):
	RESMGR_TYPES = ('Binary', 'Blob', 'Bool', 'Float', 'Int', 'Int64', 'Matrix', 'String', 'Vector2', 'Vector3', 'Vector4', 'WideString')
	READER_TYPES = {
		'Dict': DictXMLReader
	}

	def __init__(self, *args, **kwargs):
		reader_class_collection = {type_name: ResMgrXMLReader for type_name in self.RESMGR_TYPES}
		reader_class_collection.update(self.READER_TYPES)
		reader_class_collection.update(*args, **kwargs)
		return super(XMLReaderClassCollection, self).__init__(reader_class_collection)

	def __new__(sclass, *args, **kwargs):
		return super(XMLReaderClassCollection, sclass).__new__(sclass)

	def __repr__(self):
		return 'XMLReaderClassCollection({})'.format(super(XMLReaderClassCollection, self).__repr__())

class XMLReaderCollection(dict):
	@staticmethod
	def open_section(xml_path):
		return ResMgr.openSection(xml_path)

	@classmethod
	def new(sclass, reader_class_collection):
		reader_collection = sclass()
		reader_collection.update({type_name: reader_class(type_name, weakref.proxy(reader_collection)) for type_name, reader_class in reader_class_collection.items()})
		return reader_collection

	def __init__(self):
		return super(XMLReaderCollection, self).__init__()

	def parse_default_item(self, def_item):
		if isinstance(def_item, dict):
			return 'Dict', def_item
		elif isinstance(def_item, (list, tuple)):
			return def_item
		raise TypeError('Invalid default config item type "{}"'.format(type(def_item).__name__))
		return None

	def __call__(self, xml_section, def_item):
		reader_type_name, def_section = self.parse_default_item(def_item)
		return self[reader_type_name](xml_section, def_section)

	def __repr__(self):
		return '{}:{}'.format(object.__repr__(self), super(XMLReaderCollection, self).__repr__())

class XMLConfigReader(XMLReaderCollection):
	@classmethod
	def new(sclass, *args, **kwargs):
		return super(XMLConfigReader, sclass).new(XMLReaderClassCollection(*args, **kwargs))
