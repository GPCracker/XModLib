package net.GPCracker.battle.views.components.panels.elements
{
	import flash.geom.ColorTransform;
	import flash.display.Sprite;
	import flash.display.DisplayObject;

	public class PanelBorder extends Sprite
	{
		public function PanelBorder()
		{
			super();
			this.visible = false;
			return;
		}

		public function drawRect(object:DisplayObject):void
		{
			this.graphics.clear();
			this.graphics.beginFill(0xffffff, 0.1);
			this.graphics.lineStyle(1.0, 0xffffff, 1.0, true);
			this.graphics.drawRect(0.0, 0.0, object.width, object.height);
			this.graphics.endFill();
			return;
		}

		public function setColor(color:uint):void
		{
			var colorTransform:ColorTransform = new ColorTransform();
			colorTransform.color = color;
			this.transform.colorTransform = colorTransform;
			return;
		}
	}
}
