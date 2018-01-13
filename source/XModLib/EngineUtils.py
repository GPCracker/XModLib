# Authors: Vladislav Ignatenko <gpcracker@mail.ru>

# ------------ #
#    Python    #
# ------------ #
import os.path

# -------------- #
#    BigWorld    #
# -------------- #
import ResMgr

# ---------------- #
#    WoT Client    #
# ---------------- #
# nothing

# ------------------- #
#    X-Mod Library    #
# ------------------- #
# nothing

# -------------------- #
#    Module Content    #
# -------------------- #
def joinResMgrPath(path, *paths):
	if any(os.path.isabs(component) for component in paths):
		raise TypeError('additional components must not contain absolute paths')
	return os.path.normpath(os.path.join(path, *paths)).replace(os.sep, '/')

def resolveResMgrPath(path):
	if os.path.isabs(path):
		raise TypeError('relative path expected, got absolute')
	return os.path.relpath(ResMgr.resolveToAbsolutePath(path)).replace(os.sep, '/')

def getResMgrBasePath(path):
	if os.path.isabs(path):
		raise TypeError('relative path expected, got absolute')
	return joinResMgrPath(resolveResMgrPath(path), os.path.relpath(os.curdir, path))

def getResMgrRelPath(path, base=os.curdir):
	return os.path.relpath(path, base).replace(os.sep, '/')

def iterResMgrPathComponents(path, base=os.curdir):
	def iternames(path):
		while path:
			path, name = os.path.split(path)
			yield name
		return
	return reversed(tuple(iternames(os.path.relpath(path, base))))

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
