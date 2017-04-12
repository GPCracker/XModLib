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
	def parseGitDescription(sclass, description):
		# entire, tag, version, ahead, abbrev, dirty
		return sclass(re.match('(v(\d+(?:\.\d+)*))(?:\-(\d+)\-g([0-9a-f]+))?(?:\-(dirty))?', description).group(2))

	def __new__(sclass, version):
		return super(Version, sclass).__new__(sclass, itertools.imap(int, version.split('.')))

def _isVersionCompatible(provided, required):
	return provided.current in required and required.origin in provided

class ProvidedVersion(collections.namedtuple('ProvidedVersion', ('origin', 'current'))):
	__slots__ = ()

	def __new__(sclass, current=(), origin=()):
		return super(ProvidedVersion, sclass).__new__(sclass, origin or current, current)

	def __contains__(self, version):
		return not version or (self.origin or version) <= version <= (self.current or version)

	def isVersionCompatible(self, required):
		return _isVersionCompatible(self, required)

class RequiredVersion(collections.namedtuple('RequiredVersion', ('origin', 'highest'))):
	__slots__ = ()

	def __new__(sclass, origin=(), highest=()):
		return super(RequiredVersion, sclass).__new__(sclass, origin, highest)

	def __contains__(self, version):
		return not version or (self.origin or version) <= version <= (self.highest or version)

	def isVersionCompatible(self, provided):
		return _isVersionCompatible(provided, self)
