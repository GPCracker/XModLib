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
import gui.Scaleform.framework.entities.View

# ------------------- #
#    X-Mod Library    #
# ------------------- #
# nothing

# -------------------- #
#    Module Content    #
# -------------------- #
class LoaderViewBaseMeta(gui.Scaleform.framework.entities.View.View):
	@classmethod
	def getSettings(sclass, alias, swf):
		return gui.Scaleform.framework.ViewSettings(alias, sclass, swf, gui.Scaleform.framework.ViewTypes.WINDOW, None, gui.Scaleform.framework.ScopeTemplates.DEFAULT_SCOPE)
