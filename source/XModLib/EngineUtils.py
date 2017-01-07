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
# X-Mod Library
# *************************
# Nothing

def joinResMgrPath(*args):
	return os.path.normpath(os.path.join(*args)).replace(os.sep, '/')

def resolveResMgrPath(path):
	return os.path.relpath(ResMgr.resolveToAbsolutePath(path)).replace(os.sep, '/')

def getResMgrBasePath(path):
	return joinResMgrPath(resolveResMgrPath(path), os.path.relpath('.', path))
