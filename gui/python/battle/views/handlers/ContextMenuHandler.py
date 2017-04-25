# Authors: GPCracker

# *************************
# Python
# *************************
# Nothing

# *************************
# BigWorld
# *************************
# Nothing

# *************************
# WoT Client
# *************************
import gui.shared
import gui.shared.events
import gui.Scaleform.framework.managers.context_menu

# *************************
# X-Mod Library
# *************************
# Nothing

class ContextMenuHandler(gui.Scaleform.framework.managers.context_menu.AbstractContextMenuHandler):
	@classmethod
	def getHandler(cls, alias):
		return (alias, cls)

	def __init__(self, *args, **kwargs):
		super(ContextMenuHandler, self).__init__(*args, **kwargs)
		gui.shared.g_eventBus.addListener(gui.shared.events.GameEvent.HIDE_CURSOR, self._handleHideCursor, gui.shared.EVENT_BUS_SCOPE.GLOBAL)
		return

	def fini(self):
		gui.shared.g_eventBus.removeListener(gui.shared.events.GameEvent.HIDE_CURSOR, self._handleHideCursor, gui.shared.EVENT_BUS_SCOPE.GLOBAL)
		super(ContextMenuHandler, self).fini()
		return

	def _handleHideCursor(self, event):
		self.onContextMenuHide()
		return

	def _initFlashValues(self, ctx):
		super(ContextMenuHandler, self)._initFlashValues(ctx)
		return

	def _clearFlashValues(self):
		super(ContextMenuHandler, self)._clearFlashValues()
		return
