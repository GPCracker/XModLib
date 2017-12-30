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
# nothing

# ------------------- #
#    X-Mod Library    #
# ------------------- #
from .LoaderViewBase import LoaderViewBase

# -------------------- #
#    Module Content    #
# -------------------- #
class PanelsLoaderViewMeta(LoaderViewBase):
	def as_createBattlePagePanelS(self, panelAlias, panelClass, panelIndex):
		if self._isDAAPIInited():
			return self.flashObject.as_createBattlePagePanel(panelAlias, panelClass, panelIndex)
		return
