__application__ = ('X-Mod Library', 'XModLib', 'GPCracker.XModLib')
__official_topic__ = None
__authors__ = ('GPCracker', )
__version__ = ('<<version>>', None)
__client__ = (('ru', ), '<<client>>', None)

# *************************
# Application info
# *************************
if __name__ == '__main__':
	applicationInfo = '{appname} ({appshort}) {version} ({client} {clusters}) by {authors}'.format(
		appname = __application__[0],
		appshort = __application__[1],
		version = __version__[0],
		client = __client__[1],
		clusters = ', '.join(__client__[0]).upper(),
		authors = ', '.join(__authors__)
	)
	print applicationInfo
	__import__('time').sleep(len(applicationInfo) * 0.05)
	exit()

# *************************
# Compatibility test
# *************************
from . import Versioning

def isCompatibleLibVersion(application=(None, None), xmodlib=__version__):
	def parseGitDescription(description=None):
		return Versioning.Version.parseGitDescription(description) if description not in ('custom-build', None) else ()
	requiredOrigin, requiredHighest = map(parseGitDescription, application)
	providedCurrent, providedOrigin = map(parseGitDescription, xmodlib)
	requiredVersion = Versioning.RequiredVersion(requiredOrigin, requiredHighest)
	providedVersion = Versioning.ProvidedVersion(providedCurrent, providedOrigin)
	return requiredVersion.isVersionCompatible(providedVersion)
