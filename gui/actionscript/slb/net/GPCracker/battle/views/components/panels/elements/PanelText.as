package net.GPCracker.battle.views.components.panels.elements
{
	import flash.text.TextField;
	import flash.text.TextFormat;
	import flash.text.TextFieldAutoSize;
	import flash.filters.DropShadowFilter;

	public class PanelText extends TextField
	{
		public function PanelText()
		{
			super();
			var textformat:TextFormat = new TextFormat();
			textformat.underline = false;
			textformat.color = 0xffffff;
			textformat.font = "$UniversCondC";
			textformat.size = 20;
			this.border = false;
			this.autoSize = TextFieldAutoSize.NONE;
			this.wordWrap = false;
			this.multiline = true;
			this.background = false;
			this.selectable = false;
			this.tabEnabled = false;
			this.defaultTextFormat = textformat;
			return;
		}

		public function setShadow(alpha:Number, angle:Number, blur:Number, color:Number, distance:Number, strength:Number):void
		{
			var dropShadowFilter:DropShadowFilter = new DropShadowFilter();
			dropShadowFilter.alpha = alpha;
			dropShadowFilter.angle = angle;
			dropShadowFilter.blurX = blur;
			dropShadowFilter.blurY = blur;
			dropShadowFilter.color = color;
			dropShadowFilter.inner = false;
			dropShadowFilter.quality = 3;
			dropShadowFilter.distance = distance;
			dropShadowFilter.knockout = false;
			dropShadowFilter.strength = strength;
			dropShadowFilter.hideObject = false;
			this.filters = [dropShadowFilter];
			return;
		}
	}
}
