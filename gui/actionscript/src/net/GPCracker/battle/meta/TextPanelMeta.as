package net.GPCracker.battle.meta
{
	import net.wg.data.constants.Errors;
	import net.GPCracker.battle.views.components.BattleViewComponentBase;

	public class TextPanelMeta extends BattleViewComponentBase
	{
		public var py_onPanelDrag:Function;
		public var py_onPanelDrop:Function;

		public function TextPanelMeta()
		{
			super();
			return;
		}

		public function py_onPanelDragS(x:Number, y:Number):void
		{
			App.utils.asserter.assertNotNull(this.py_onPanelDrag, "py_onPanelDrag" + Errors.CANT_NULL);
			DebugUtils.LOG_DEBUG("A panel " + this.name + " was dragged at [" + [x, y] + "].");
			this.py_onPanelDrag(x, y);
			return;
		}

		public function py_onPanelDropS(x:Number, y:Number):void
		{
			App.utils.asserter.assertNotNull(this.py_onPanelDrop, "py_onPanelDrop" + Errors.CANT_NULL);
			DebugUtils.LOG_DEBUG("A panel " + this.name + " was dropped at [" + [x, y] + "].");
			this.py_onPanelDrop(x, y);
			return;
		}
	}
}
