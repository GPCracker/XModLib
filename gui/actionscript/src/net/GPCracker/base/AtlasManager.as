package net.GPCracker.base
{
	import flash.utils.Dictionary;
	import flash.display.Graphics;
	import flash.events.EventDispatcher;

	import net.GPCracker.base.Atlas;
	import net.GPCracker.base.AtlasEvent;
	import net.GPCracker.interfaces.IAtlas;
	import net.GPCracker.interfaces.IAtlasManager;

	public class AtlasManager extends EventDispatcher implements IAtlasManager
	{
		private var _atlases:Dictionary = null;

		public function AtlasManager()
		{
			super();
			this._atlases = new Dictionary(true);
			return;
		}

		public function isAtlasLoaded(atlasName:String):Boolean
		{
			var atlasObject:IAtlas = this._atlases[atlasName];
			return atlasObject && atlasObject.isLoaded();
		}

		public function loadAtlas(atlasName:String, atlasPath:String):void
		{
			if (!this._atlases[atlasName])
			{
				var atlasObject:IAtlas = new Atlas(atlasPath);
				atlasObject.addEventListener(AtlasEvent.ATLAS_LOADED, this.onAtlasLoadingCompleteHandler);
				atlasObject.name = atlasName;
				this._atlases[atlasName] = atlasObject;
			}
			return;
		}

		public function drawGraphics(atlasName:String, atlasItemName:String, targetGraphics:Graphics, smooth:Boolean=false, repeat:Boolean=false, center:Boolean=false):void
		{
			var atlasObject:IAtlas = this._atlases[atlasName];
			if (atlasObject)
			{
				atlasObject.drawGraphics(atlasItemName, targetGraphics, smooth, repeat, center);
			}
			return;
		}

		private function onAtlasLoadingCompleteHandler(event:AtlasEvent):void
		{
			this.dispatchEvent(event.clone());
			return;
		}

		public function dispose():void
		{
			if (this._atlases)
			{
				for each (var atlasObject:IAtlas in this._atlases)
				{
					atlasObject.removeEventListener(AtlasEvent.ATLAS_LOADED, this.onAtlasLoadingCompleteHandler);
				}
				App.utils.data.cleanupDynamicObject(this._atlases);
			}
			this._atlases = null;
		}
	}
}
