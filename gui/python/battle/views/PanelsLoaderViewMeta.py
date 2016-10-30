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
# Nothing

# *************************
# X-Mod Library
# *************************
from .LoaderViewBase import LoaderViewBase

class PanelsLoaderViewMeta(LoaderViewBase):
	def as_createBattlePagePanelS(self, panelAlias, panelClass, panelIndex):
		if self._isDAAPIInited():
			return self.flashObject.as_createBattlePagePanel(panelAlias, panelClass, panelIndex)
		return
