package net.GPCracker.battle.views.components.minimap.entries
{
	import net.wg.gui.battle.components.BattleUIComponent;
	import net.wg.gui.battle.views.minimap.MinimapEntryController;
	import net.wg.gui.battle.views.minimap.components.entries.interfaces.IMinimapEntryWithNonScaleContent;

	public class ScalableMinimapEntry extends BattleUIComponent implements IMinimapEntryWithNonScaleContent
	{
		public function ScalableMinimapEntry()
		{
			super();
			return;
		}

		override protected function configUI():void
		{
			super.configUI();
			MinimapEntryController.instance.registerScalableEntry(this, true);
			return;
		}

		public function setContentNormalizedScale(param1:Number):void
		{
			return;
		}

		override protected function onDispose():void
		{
			MinimapEntryController.instance.unregisterScalableEntry(this, true);
			super.onDispose();
			return;
		}
	}
}
