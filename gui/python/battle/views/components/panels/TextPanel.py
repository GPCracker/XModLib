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

# *************************
# X-Mod Library
# *************************
from .TextPanelMeta import TextPanelMeta

class TextPanel(TextPanelMeta):
	CONFIG_APPLY_SKIP = ('text', )

	def __init__(self, *args, **kwargs):
		super(TextPanel, self).__init__(*args, **kwargs)
		# Text panel flash default parameters.
		self._config = {
			'alpha': 1.0,
			'visible': True,
			'background': '',
			'tooltip': '',
			'text': '',
			'position': (0.0, 0.0),
			'size': (100.0, 50.0)
		}
		return

	@property
	def config(self):
		return self._config

	@config.setter
	def config(self, value):
		self._config.update(value)
		self.as_applyConfigS({key: value[key] for key in value if key not in self.CONFIG_APPLY_SKIP})
		return

	def py_onPanelDrag(self, x, y):
		return

	def py_onPanelDrop(self, x, y):
		return

	def _populate(self):
		super(TextPanel, self)._populate()
		gui.shared.g_eventBus.addListener(gui.shared.events.GameEvent.SHOW_CURSOR, self._handleShowCursor, gui.shared.EVENT_BUS_SCOPE.GLOBAL)
		gui.shared.g_eventBus.addListener(gui.shared.events.GameEvent.HIDE_CURSOR, self._handleHideCursor, gui.shared.EVENT_BUS_SCOPE.GLOBAL)
		gui.shared.g_eventBus.addListener(gui.shared.events.GameEvent.CHANGE_APP_RESOLUTION, self._handleChangeAppResolution, gui.shared.EVENT_BUS_SCOPE.GLOBAL)
		return

	def _dispose(self):
		gui.shared.g_eventBus.removeListener(gui.shared.events.GameEvent.SHOW_CURSOR, self._handleShowCursor, gui.shared.EVENT_BUS_SCOPE.GLOBAL)
		gui.shared.g_eventBus.removeListener(gui.shared.events.GameEvent.HIDE_CURSOR, self._handleHideCursor, gui.shared.EVENT_BUS_SCOPE.GLOBAL)
		gui.shared.g_eventBus.removeListener(gui.shared.events.GameEvent.CHANGE_APP_RESOLUTION, self._handleChangeAppResolution, gui.shared.EVENT_BUS_SCOPE.GLOBAL)
		super(TextPanel, self)._dispose()
		return

	def _handleShowCursor(self, event):
		self.as_toggleCursorS(True)
		return

	def _handleHideCursor(self, event):
		self.as_toggleCursorS(False)
		return

	def _handleChangeAppResolution(self, event):
		ctx = event.ctx
		self.as_changeAppResolutionS(ctx['width'], ctx['height'])
		return

	def updateText(self, text):
		self.as_setTextS(text)
		return
