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
from ..BattleViewComponentBase import BattleViewComponentBase

# -------------------- #
#    Module Content    #
# -------------------- #
class TextPanelMeta(BattleViewComponentBase):
	def py_onPanelDrag(self, x, y):
		self._printOverrideError('py_onPanelDrag')
		return

	def py_onPanelDrop(self, x, y):
		self._printOverrideError('py_onPanelDrop')
		return

	def as_toggleCursorS(self, enabled):
		if self._isDAAPIInited():
			return self.flashObject.as_toggleCursor(enabled)
		return

	def as_changeAppResolutionS(self, width, height):
		if self._isDAAPIInited():
			return self.flashObject.as_changeAppResolution(width, height)
		return

	def as_setBackgroundS(self, image):
		if self._isDAAPIInited():
			return self.flashObject.as_setBackground(image)
		return

	def as_setTextS(self, text):
		if self._isDAAPIInited():
			return self.flashObject.as_setText(text)
		return

	def as_setToolTipS(self, text):
		if self._isDAAPIInited():
			return self.flashObject.as_setToolTip(text)
		return

	def as_setVisibleS(self, visible):
		if self._isDAAPIInited():
			return self.flashObject.as_setVisible(visible)
		return

	def as_setAlphaS(self, alpha):
		if self._isDAAPIInited():
			return self.flashObject.as_setAlpha(alpha)
		return

	def as_setPositionS(self, x, y):
		if self._isDAAPIInited():
			return self.flashObject.as_setPosition(x, y)
		return

	def as_setSizeS(self, width, height):
		if self._isDAAPIInited():
			return self.flashObject.as_setSize(width, height)
		return

	def as_setTextShadowS(self, alpha, angle, blur, color, distance, strength):
		if self._isDAAPIInited():
			return self.flashObject.as_setTextShadow(alpha, angle, blur, color, distance, strength)
		return

	def as_applyConfigS(self, config):
		if self._isDAAPIInited():
			return self.flashObject.as_applyConfig(config)
		return
