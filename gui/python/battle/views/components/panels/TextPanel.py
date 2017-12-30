# Authors: Vladislav Ignatenko <gpcracker@mail.ru>

# ------------ #
#    Python    #
# ------------ #
# nothing

# -------------- #
#    BigWorld    #
# -------------- #
# nothing

# ---------------- #
#    WoT Client    #
# ---------------- #
import gui.shared
import gui.shared.events

# ------------------- #
#    X-Mod Library    #
# ------------------- #
from .TextPanelMeta import TextPanelMeta

# -------------------- #
#    Module Content    #
# -------------------- #
class TextPanel(TextPanelMeta):
	@staticmethod
	def _computeConfigPatch(update, base):
		return {key: value for key, value in update.viewitems() if key in base and base[key] != value}

	def __init__(self, *args, **kwargs):
		super(TextPanel, self).__init__(*args, **kwargs)
		# Text panel flash default parameters.
		self.__config = {
			'alpha': 1.0,
			'visible': True,
			'background': '',
			'tooltip': '',
			'text': '',
			'position': (0.0, 0.0),
			'size': (100.0, 50.0)
		}
		return

	def py_onPanelDrag(self, x, y):
		self.__config['position'] = (x, y)
		return

	def py_onPanelDrop(self, x, y):
		self.__config['position'] = (x, y)
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
		self.as_changeAppResolutionS(event.ctx['width'], event.ctx['height'])
		return

	def getConfig(self):
		return self.__config.copy()

	def updateConfig(self, config):
		config = self._computeConfigPatch(config, self.__config)
		self.__config.update(config)
		self.as_applyConfigS(config)
		return

	def updateText(self, text):
		self.__config['text'] = text
		self.as_setTextS(text)
		return
