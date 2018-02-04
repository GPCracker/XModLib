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
import gui.Scaleform.battle_entry
import gui.Scaleform.daapi.view.battle.shared

# ------------------- #
#    X-Mod Library    #
# ------------------- #
import XModLib.HookUtils

# -------------------- #
#    Module Content    #
# -------------------- #
@XModLib.HookUtils.methodHook(gui.Scaleform.battle_entry.BattleEntry, '_getRequiredLibraries', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_BattleEntry_getRequiredLibraries(old_BattleEntry_getRequiredLibraries, self, *args, **kwargs):
	return old_BattleEntry_getRequiredLibraries(self, *args, **kwargs) + ('{0[1]}.swf'.format(XModLib.__application__), )

@XModLib.HookUtils.methodAdd(gui.Scaleform.daapi.view.battle.shared.SharedPage, 'as_createBattlePagePanelS')
def new_SharedPage_createBattlePagePanel(self, panelAlias, panelClass, panelIndex):
	if self._isDAAPIInited():
		return self.flashObject.as_createBattlePagePanel(panelAlias, panelClass, panelIndex)
	return
