package net.GPCracker.interfaces
{
	import flash.display.Graphics;
	import flash.events.IEventDispatcher;
	import net.wg.infrastructure.interfaces.entity.IDisposable;

	public interface IAtlasManager extends IEventDispatcher, IDisposable
	{
		function isAtlasLoaded(atlasName:String):Boolean;
		function loadAtlas(atlasName:String, atlasPath:String):void;
		function drawGraphics(atlasName:String, atlasItemName:String, targetGraphics:Graphics, smooth:Boolean=false, repeat:Boolean=false, center:Boolean=false):void;
	}
}
