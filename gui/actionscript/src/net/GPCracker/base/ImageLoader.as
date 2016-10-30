package net.GPCracker.base
{
	import flash.net.URLRequest;
	import flash.system.LoaderContext;
	import flash.system.ApplicationDomain;
	import flash.events.Event;
	import flash.events.IOErrorEvent;
	import flash.display.Loader;
	import flash.display.Sprite;

	public class ImageLoader extends Sprite
	{
		public static const LOADING:String = "loading";
		public static const SUCCESS:String = "success";
		public static const FAILURE:String = "failure";
		public static const UNLOADED:String = "unloaded";

		public var status:String = ImageLoader.UNLOADED;

		private var _width:Number = 0;
		private var _height:Number = 0;
		private var _loader:Loader = null;
		private var _source:String = null;

		public function ImageLoader()
		{
			super();
			this._loader = new Loader();
			this.addChild(this._loader);
			this.addLoaderListeners();
			return;
		}

		private function addLoaderListeners():void
		{
			this._loader.contentLoaderInfo.addEventListener(Event.COMPLETE, this.onLoaderCompleteHandler);
			this._loader.contentLoaderInfo.addEventListener(IOErrorEvent.IO_ERROR, this.onLoaderErrorHandler);
			this._loader.contentLoaderInfo.addEventListener(Event.UNLOAD, this.onLoaderUnloadHandler);
			return;
		}

		private function delLoaderListeners():void
		{
			this._loader.contentLoaderInfo.removeEventListener(Event.COMPLETE, this.onLoaderCompleteHandler);
			this._loader.contentLoaderInfo.removeEventListener(IOErrorEvent.IO_ERROR, this.onLoaderErrorHandler);
			this._loader.contentLoaderInfo.removeEventListener(Event.UNLOAD, this.onLoaderUnloadHandler);
			return;
		}

		private function onLoaderCompleteHandler(event:Event):void
		{
			this.status = ImageLoader.SUCCESS;
			this.updateContainerSize();
			return;
		}

		private function onLoaderErrorHandler(event:IOErrorEvent):void
		{
			this.status = ImageLoader.FAILURE;
			return;
		}

		private function onLoaderUnloadHandler(event:Event):void
		{
			this.status = ImageLoader.UNLOADED;
			return;
		}

		public function load(image:String):void
		{
			this._source = image;
			this.status = ImageLoader.LOADING;
			var urlRequest:URLRequest = new URLRequest(image);
			var loaderContext:LoaderContext = new LoaderContext(false, ApplicationDomain.currentDomain);
			this._loader.load(urlRequest, loaderContext);
			return;
		}

		public function unload():void
		{
			this._loader.unload();
			this._source = null;
			return;
		}

		public function get source():String
		{
			return this._source;
		}

		public function set source(image:String):void
		{
			if (Boolean(image) != Boolean(this._source))
			{
				if (image)
				{
					this.load(image);
				}
				else
				{
					this.unload();
				}
			}
			return;
		}

		private function updateContainerSize():void
		{
			if (this._width != 0 && this._height != 0)
			{
				this.width = this._width;
				this.height = this._height;
			}
			else
			{
				this.scaleX = 1.0;
				this.scaleY = 1.0;
			}
			return;
		}

		public function getContainerSize():Array
		{
			return [this._width, this._height];
		}

		public function setContainerSize(width:Number, height:Number):void
		{
			this._width = width;
			this._height = height;
			if (this.status == ImageLoader.SUCCESS)
			{
				this.updateContainerSize();
			}
			return;
		}
	}
}
