# Authors: GPCracker

# *************************
# Python
# *************************
import re
import functools
import itertools
import collections

# *************************
# BigWorld
# *************************
# Nothing

# *************************
# WoT Client
# *************************
# Nothing

# *************************
# X-Mod Library
# *************************
# Nothing

class Version(tuple):
	__slots__ = ()

	@classmethod
	def parseVersion(cls, version):
		# entire, version
		return cls(re.match('^(?:v\.?)?(\d+(?:\.\d+)*)$', version).group(1))

	@classmethod
	def parseGitDescription(cls, description):
		# entire, tag, version, ahead, abbrev, dirty
		return cls(re.match('^((?:v\.?)?(\d+(?:\.\d+)*))(?:\-(\d+)\-g([0-9a-f]+))?(?:\-(dirty))?$', description).group(2))

	def __new__(cls, version):
		if not isinstance(version, basestring):
			raise TypeError('version argument must be string, not {!s}'.format(type(version).__name__))
		return super(Version, cls).__new__(cls, itertools.imap(int, version.split('.')))

def _isVersionCompatible(provided, required):
	return provided.current in required and required.origin in provided

class ProvidedVersion(collections.namedtuple('ProvidedVersion', ('origin', 'current'))):
	__slots__ = ()

	def __new__(cls, current=(), origin=()):
		if not isinstance(current, tuple):
			raise TypeError('current argument must be tuple, not {!s}'.format(type(current).__name__))
		if not isinstance(origin, tuple):
			raise TypeError('origin argument must be tuple, not {!s}'.format(type(origin).__name__))
		return super(ProvidedVersion, cls).__new__(cls, origin or current, current)

	def __contains__(self, version):
		if not isinstance(version, tuple):
			raise TypeError('version argument must be tuple, not {!s}'.format(type(version).__name__))
		return not version or (self.origin or version) <= version <= (self.current or version)

	def isVersionCompatible(self, required):
		if not isinstance(required, RequiredVersion):
			raise TypeError('required argument must be RequiredVersion, not {!s}'.format(type(required).__name__))
		return _isVersionCompatible(self, required)

class RequiredVersion(collections.namedtuple('RequiredVersion', ('origin', 'highest'))):
	__slots__ = ()

	def __new__(cls, origin=(), highest=()):
		if not isinstance(origin, tuple):
			raise TypeError('origin argument must be tuple, not {!s}'.format(type(origin).__name__))
		if not isinstance(highest, tuple):
			raise TypeError('highest argument must be tuple, not {!s}'.format(type(highest).__name__))
		return super(RequiredVersion, cls).__new__(cls, origin, highest)

	def __contains__(self, version):
		if not isinstance(version, tuple):
			raise TypeError('version argument must be tuple, not {!s}'.format(type(version).__name__))
		return not version or (self.origin or version) <= version <= (self.highest or version)

	def isVersionCompatible(self, provided):
		if not isinstance(provided, ProvidedVersion):
			raise TypeError('provided argument must be ProvidedVersion, not {!s}'.format(type(provided).__name__))
		return _isVersionCompatible(provided, self)

def _isClientVersionCompatible(provided, required):
	return all((
		not required.realms or provided.realm in required.realms,
		not required.version or provided.version == required.version
	))

class ProvidedClientVersion(collections.namedtuple('ProvidedClientVersion', ('realm', 'version'))):
	__slots__ = ()

	def __new__(cls, realm, version):
		if not isinstance(realm, basestring):
			raise TypeError('realm argument must be string, not {!s}'.format(type(realm).__name__))
		if not isinstance(version, tuple):
			raise TypeError('version argument must be tuple, not {!s}'.format(type(version).__name__))
		return super(ProvidedClientVersion, cls).__new__(cls, realm, version)

	def isClientVersionCompatible(self, required):
		if not isinstance(required, RequiredClientVersion):
			raise TypeError('required argument must be RequiredClientVersion, not {!s}'.format(type(required).__name__))
		return _isClientVersionCompatible(self, required)

class RequiredClientVersion(collections.namedtuple('RequiredClientVersion', ('realms', 'version'))):
	__slots__ = ()

	def __new__(cls, realms=(), version=()):
		if not isinstance(realms, (tuple, frozenset)):
			raise TypeError('realms argument must be tuple, not {!s}'.format(type(realms).__name__))
		if not isinstance(version, tuple):
			raise TypeError('version argument must be tuple, not {!s}'.format(type(version).__name__))
		return super(RequiredClientVersion, cls).__new__(cls, realms, version)

	def isClientVersionCompatible(self, provided):
		if not isinstance(provided, ProvidedClientVersion):
			raise TypeError('provided argument must be ProvidedClientVersion, not {!s}'.format(type(provided).__name__))
		return _isClientVersionCompatible(provided, self)
