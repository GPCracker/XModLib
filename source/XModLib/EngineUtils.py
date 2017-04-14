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

def getResMgrBinaryFileContent(path):
	if ResMgr.isFile(path):
		section = ResMgr.openSection(path)
		if section is not None:
			return section.asBinary
	return None

def getResMgrDirectoryContent(path):
	uniques = lambda entries: sorted(set(entries), key=entries.index)
	if ResMgr.isDir(path):
		section = ResMgr.openSection(path)
		if section is not None:
			return uniques(section.keys())
	return None

def walkResMgrTree(dirpath):
	entries = getResMgrDirectoryContent(dirpath)
	if entries is not None:
		dirnames = filter(lambda subpath: ResMgr.isDir(joinResMgrPath(dirpath, subpath)), entries)
		filenames = filter(lambda subpath: ResMgr.isFile(joinResMgrPath(dirpath, subpath)), entries)
		yield dirpath, dirnames, filenames
		for dirname in dirnames:
			for block in walkResMgrTree(joinResMgrPath(dirpath, dirname)):
				yield block
	return
