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
from .LoaderViewBaseMeta import LoaderViewBaseMeta

# -------------------- #
#    Module Content    #
# -------------------- #
class LoaderViewBase(LoaderViewBaseMeta):
	def _populate(self):
		super(LoaderViewBase, self)._populate()
		return

	def _dispose(self):
		super(LoaderViewBase, self)._dispose()
		return
