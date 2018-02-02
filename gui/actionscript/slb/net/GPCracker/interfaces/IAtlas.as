package net.GPCracker.interfaces
{
	import flash.display.Graphics;
	import flash.events.IEventDispatcher;
	import net.wg.infrastructure.interfaces.entity.IDisposable;

	import net.GPCracker.interfaces.IAtlasItemVO;

	public interface IAtlas extends IEventDispatcher, IDisposable
	{
		function get path():String;
		function get imgStatus():String;
		function get xmlStatus():String;
		function get name():String;
		function set name(value:String):void;
		function isLoaded():Boolean;
		function drawGraphics(itemName:String, targetGraphics:Graphics, smooth:Boolean=false, repeat:Boolean=false, center:Boolean=false):void;
	}
}
