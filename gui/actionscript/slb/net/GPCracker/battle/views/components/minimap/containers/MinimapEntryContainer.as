package net.GPCracker.battle.views.components.minimap.containers
{
	import flash.display.Sprite;

	public class MinimapEntryContainer extends Sprite
	{
		public function MinimapEntryContainer()
		{
			super();
			this.graphics.clear();
			this.graphics.beginFill(0x00ff00, 0.0);
			this.graphics.drawRect(-105.0, -105.0, 210.0, 210.0);
			this.graphics.endFill();
			return;
		}
	}
}
