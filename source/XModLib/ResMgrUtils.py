# Authors: GPCracker

# *************************
# Python
# *************************
import os.path

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

class ResMgrUtils(object):
	@staticmethod
	def join_path(*args, **kwargs):
		path = os.path.normpath(os.path.join(*args, **kwargs)).replace(os.sep, '/')
		return path + ('/' if os.path.isdir(path) else '')

	@staticmethod
	def resolve_path(path):
		path = os.path.relpath(ResMgr.resolveToAbsolutePath(path)).replace(os.sep, '/')
		return path + ('/' if os.path.isdir(path) else '')
