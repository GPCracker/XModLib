package net.GPCracker.base
{
	import flash.display.Sprite;

	import net.GPCracker.base.AtlasEvent;
	import net.GPCracker.interfaces.IAtlasManager;

	public class AtlasSprite extends Sprite
	{
		protected var _atlasManager:IAtlasManager = null;
		protected var _atlasPath:String = null;
		protected var _source:String = null;

		public var autoRedraw:Boolean = true;
		public var fillSmooth:Boolean = false;
		public var fillRepeat:Boolean = false;
		public var fillCenter:Boolean = false;

		public function AtlasSprite(atlasManager:IAtlasManager, atlasPath:String="../flash/atlases", autoRedraw:Boolean=true)
		{
			super();
			this._atlasManager = atlasManager;
			this._atlasPath = atlasPath;
			this.autoRedraw = autoRedraw;
			return;
		}

		protected function getSourceParts():Array
		{
			if (this._source)
			{
				var splitted:Array = this._source.split(':');
				if (splitted.length == 2 && splitted[0] && splitted[1])
				{
					return splitted;
				}
			}
			return null;
		}

		public function getAtlasName():String
		{
			var sourceParts:Array = this.getSourceParts();
			return sourceParts ? sourceParts[0] : null;
		}

		public function getAtlasItemName():String
		{
			var sourceParts:Array = this.getSourceParts();
			return sourceParts ? sourceParts[1] : null;
		}

		public function drawGraphics():void
		{
			var sourceParts:Array = this.getSourceParts();
			var atlasName:String = sourceParts ? sourceParts[0] : null;
			var atlasItemName:String = sourceParts ? sourceParts[1] : null;
			if (atlasName && atlasItemName && this._atlasManager)
			{
				if (this._atlasManager.isAtlasLoaded(atlasName))
				{
					this._atlasManager.drawGraphics(atlasName, atlasItemName, this.graphics, this.fillSmooth, this.fillRepeat, this.fillCenter);
				}
				else
				{
					this._atlasManager.addEventListener(AtlasEvent.ATLAS_LOADED, this.onAtlasLoadingCompleteHandler);
					this._atlasManager.loadAtlas(atlasName, this._atlasPath);
				}
			}
			return;
		}

		public function clearGraphics():void
		{
			this.graphics.clear();
			return;
		}

		public function get source():String
		{
			return this._source;
		}

		public function set source(value:String):void
		{
			this._source = value;
			if (this.autoRedraw)
			{
				if (value)
				{
					this.drawGraphics();
				}
				else
				{
					this.clearGraphics();
				}
			}
			return;
		}

		private function onAtlasLoadingCompleteHandler(event:AtlasEvent):void
		{
			var atlasName:String = this.getAtlasName();
			if (atlasName && atlasName == event.atlasName)
			{
				this._atlasManager.removeEventListener(AtlasEvent.ATLAS_LOADED, this.onAtlasLoadingCompleteHandler);
				this.drawGraphics();
			}
			return;
		}
	}
}
