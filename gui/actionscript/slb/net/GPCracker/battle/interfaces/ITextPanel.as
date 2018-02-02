package net.GPCracker.battle.interfaces
{
	import flash.events.IEventDispatcher;

	public interface ITextPanel extends IEventDispatcher
	{
		function py_onPanelDragS(x:Number, y:Number):void;
		function py_onPanelDropS(x:Number, y:Number):void;
		function as_toggleCursor(enabled:Boolean):void;
		function as_setBackground(image:String):void;
		function as_setText(text:String):void;
		function as_setToolTip(text:String):void;
		function as_setVisible(visible:Boolean):void;
		function as_setAlpha(alpha:Number):void;
		function as_setPosition(x:Number, y:Number):void;
		function as_setSize(height:Number, width:Number):void;
		function as_setTextShadow(alpha:Number, angle:Number, blur:Number, color:Number, distance:Number, strength:Number):void;
		function as_applyConfig(config:Object):void;
	}
}
