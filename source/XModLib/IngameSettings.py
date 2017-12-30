# Authors: Vladislav Ignatenko <gpcracker@mail.ru>

# ------------ #
#    Python    #
# ------------ #
import base64
import cPickle
import functools

# -------------- #
#    BigWorld    #
# -------------- #
import ResMgr

# ---------------- #
#    WoT Client    #
# ---------------- #
import Settings

# ------------------- #
#    X-Mod Library    #
# ------------------- #
from . import XMLConfigReader

# -------------------- #
#    Module Content    #
# -------------------- #
def openPreferences(sectionPath, newSection=False):
	section = Settings.g_instance.userPrefs[sectionPath]
	if section is None and newSection:
		section = Settings.g_instance.userPrefs.createSection(sectionPath)
	return section

def savePreferences():
	return Settings.g_instance.save()

class IngameSettingsAbstractDataObject(object):
	__slots__ = ()

	@staticmethod
	def openPreferences(sectionPath, sectionDefault, newSection=False):
		section = openPreferences(sectionPath)
		if section is None and newSection:
			section = openPreferences(sectionPath, newSection)
			if section is not None:
				section.asString = sectionDefault
		return section

	savePreferences = staticmethod(savePreferences)

	@staticmethod
	def _encode(data):
		return base64.b64encode(cPickle.dumps(data))

	@staticmethod
	def _decode(data):
		return cPickle.loads(base64.b64decode(data))

	@classmethod
	def load(cls, sectionPath, sectionDefault=None, newSection=False):
		raise NotImplementedError
		return None

	@classmethod
	def loader(cls, sectionPath, newSection=False):
		raise NotImplementedError
		return None

	def save(self):
		raise NotImplementedError
		return

class IngameSettingsDictDataObject(IngameSettingsAbstractDataObject, dict):
	__slots__ = ('section', )

	@classmethod
	def load(cls, sectionPath, sectionDefault='KGRwMQou', newSection=False):
		section = cls.openPreferences(sectionPath, sectionDefault, newSection)
		return cls(section, cls._decode(section.asString if section is not None else sectionDefault))

	@classmethod
	def loader(cls, sectionPath, newSection=False):
		return functools.partial(cls.load, sectionPath, newSection=newSection)

	def __new__(cls, section, *args, **kwargs):
		return super(IngameSettingsAbstractDataObject, cls).__new__(cls, *args, **kwargs)

	def __init__(self, section, *args, **kwargs):
		super(IngameSettingsAbstractDataObject, self).__init__(*args, **kwargs)
		self.section = section
		return

	def save(self):
		if self.section is not None:
			self.section.asString = self._encode(self.copy())
			self.savePreferences()
		return

class IngameSettingsXMLReaderMeta(XMLConfigReader.XMLReaderMeta):
	__slots__ = ()

	@classmethod
	def construct(cls, className, constructor):
		readerClass = super(IngameSettingsXMLReaderMeta, cls).construct(className)
		readerClass.constructor = staticmethod(constructor)
		return readerClass

	def _readSection(self, xmlSection, defSection):
		if getattr(self, 'constructor', None) is None:
			raise AttributeError('Constructor is undefined or None.')
		return self.constructor(defSection)
