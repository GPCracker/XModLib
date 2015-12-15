# Authors: GPCracker

# *************************
# Python
# *************************
# Nothing

# *************************
# BigWorld
# *************************
import GUI

# *************************
# WoT Client
# *************************
# Nothing

# *************************
# X-Mod Code Library
# *************************
# Nothing

class GUIWrapper(object):
	@classmethod
	def createGUI(sclass, className, settings, useWrapper = True):
		gui = getattr(GUI, className)('')
		sclass.applySettings(gui, settings)
		return sclass(gui) if useWrapper else gui

	@staticmethod
	def applySettings(gui, settings):
		for attribute, value in settings.items():
			getattr(gui, attribute)
			setattr(gui, attribute, value)
		return None

	def __init__(self, gui):
		self.__gui = gui
		self.addRoot()
		return

	@property
	def gui(self):
		return self.__gui

	def addRoot(self):
		GUI.addRoot(self.__gui)
		return

	def delRoot(self):
		GUI.delRoot(self.__gui)
		return

	def __del__(self):
		self.delRoot()
		self.__gui = None
		return
