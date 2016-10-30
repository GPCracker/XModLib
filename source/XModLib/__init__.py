__application__ = ['X-Mod Library', 'XModLib']
__official_topic__ = None
__authors__ = ['GPCracker']
__version__ = '<version>'
__client__ = [['ru'], '0.9.15.2', None]

# *************************
# Application info
# *************************
if __name__ == '__main__':
	applicationInfo = '{appname} ({appshort}) {version} ({client} {clusters}) by {authors}'.format(
		appname = __application__[0],
		appshort = __application__[1],
		version = __version__,
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
def isCompatibleLibVersion(application=[[None, None]], xmodlib=__version__.split('#')):
	return any([all([version[0] is None or xmodlib[0] == version[0], version[1] is None or xmodlib[1] == version[1]]) for version in application])
