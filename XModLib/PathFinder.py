# Authors: GPCracker

import os

import ResMgr

class PathFinder(object):
	def __init__(self):
		xml = ResMgr.openSection('../paths.xml/Paths')
		self.resPaths = filter(os.path.isdir, xml.readWideStrings('Path')) if xml is not None else []
		return

	def __call__(self, relPath):
		for resPath in self.resPaths:
			glbPath = os.path.join(resPath, relPath).replace(os.sep, '/')
			if os.path.exists(glbPath):
				return glbPath
		return None
