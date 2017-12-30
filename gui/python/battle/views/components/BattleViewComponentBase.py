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
import gui.Scaleform.framework
import gui.Scaleform.framework.ViewTypes
import gui.Scaleform.framework.ScopeTemplates
import gui.Scaleform.framework.entities.BaseDAAPIComponent

# ------------------- #
#    X-Mod Library    #
# ------------------- #
# nothing

# -------------------- #
#    Module Content    #
# -------------------- #
class BattleViewComponentBase(gui.Scaleform.framework.entities.BaseDAAPIComponent.BaseDAAPIComponent):
	@classmethod
	def getSettings(sclass, alias):
		return gui.Scaleform.framework.ViewSettings(alias, sclass, None, gui.Scaleform.framework.ViewTypes.COMPONENT, None, gui.Scaleform.framework.ScopeTemplates.DEFAULT_SCOPE)

	def _populate(self):
		super(BattleViewComponentBase, self)._populate()
		return

	def _dispose(self):
		super(BattleViewComponentBase, self)._dispose()
		return
