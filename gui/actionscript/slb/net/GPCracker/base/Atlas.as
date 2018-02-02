package net.GPCracker.base
{
	import flash.net.URLLoader;
	import flash.net.URLRequest;
	import flash.geom.Matrix;
	import flash.utils.Dictionary;
	import flash.events.Event;
	import flash.events.IOErrorEvent;
	import flash.events.EventDispatcher;
	import flash.system.LoaderContext;
	import flash.system.ApplicationDomain;
	import flash.display.Bitmap;
	import flash.display.Loader;
	import flash.display.Graphics;
	import flash.display.BitmapData;

	import net.GPCracker.base.AtlasEvent;
	import net.GPCracker.base.AtlasItemVO;
	import net.GPCracker.interfaces.IAtlas;
	import net.GPCracker.interfaces.IAtlasItemVO;

	public class Atlas extends EventDispatcher implements IAtlas
	{
		public static const LOADING:String = "loading";
		public static const SUCCESS:String = "success";
		public static const FAILURE:String = "failure";
		public static const UNLOADED:String = "unloaded";

		private var _imgStatus:String = Atlas.UNLOADED;
		private var _xmlStatus:String = Atlas.UNLOADED;

		private var _path:String = null;
		private var _name:String = null;

		private var _imgData:BitmapData = null;
		private var _xmlData:Dictionary = null;
		private var _imgLoader:Loader = null;
		private var _xmlLoader:URLLoader = null;

		public function Atlas(path:String)
		{
			super();
			this._path = path;
			this._imgLoader = new Loader();
			this._xmlLoader = new URLLoader();
			return;
		}

		public function get path():String
		{
			return this._path;
		}

		public function get imgStatus():String
		{
			return this._imgStatus;
		}

		public function get xmlStatus():String
		{
			return this._xmlStatus;
		}

		private function addImgLoaderListeners():void
		{
			this._imgLoader.contentLoaderInfo.addEventListener(Event.COMPLETE, this.onImgLoaderCompleteHandler);
			this._imgLoader.contentLoaderInfo.addEventListener(IOErrorEvent.IO_ERROR, this.onImgLoaderErrorHandler);
			return;
		}

		private function delImgLoaderListeners():void
		{
			this._imgLoader.contentLoaderInfo.removeEventListener(Event.COMPLETE, this.onImgLoaderCompleteHandler);
			this._imgLoader.contentLoaderInfo.removeEventListener(IOErrorEvent.IO_ERROR, this.onImgLoaderErrorHandler);
			return;
		}

		private function addXmlLoaderListeners():void
		{
			this._xmlLoader.addEventListener(Event.COMPLETE, this.onXmlLoaderCompleteHandler);
			this._xmlLoader.addEventListener(IOErrorEvent.IO_ERROR, this.onXmlLoaderErrorHandler);
			return;
		}

		private function delXmlLoaderListeners():void
		{
			this._xmlLoader.removeEventListener(Event.COMPLETE, this.onXmlLoaderCompleteHandler);
			this._xmlLoader.removeEventListener(IOErrorEvent.IO_ERROR, this.onXmlLoaderErrorHandler);
			return;
		}

		private function onImgLoaderCompleteHandler(event:Event):void
		{
			this._imgData = Bitmap(this._imgLoader.content).bitmapData;
			this.imgLoaderFini();
			this._imgStatus = Atlas.SUCCESS;
			this.dispatchEvent(new AtlasEvent(AtlasEvent.ATLAS_IMG_LOADED, this._name));
			if (this._xmlStatus == Atlas.SUCCESS)
			{
				this.dispatchEvent(new AtlasEvent(AtlasEvent.ATLAS_LOADED, this._name));
			}
			return;
		}

		private function onImgLoaderErrorHandler(event:IOErrorEvent):void
		{
			this._imgData = null;
			this.imgLoaderFini();
			this._imgStatus = Atlas.FAILURE;
			return;
		}

		private function onXmlLoaderCompleteHandler(event:Event):void
		{
			this._xmlData = this.parseXmlData(this._xmlLoader.data);
			this.xmlLoaderFini();
			this._xmlStatus = Atlas.SUCCESS;
			this.dispatchEvent(new AtlasEvent(AtlasEvent.ATLAS_XML_LOADED, this._name));
			if (this._imgStatus == Atlas.SUCCESS)
			{
				this.dispatchEvent(new AtlasEvent(AtlasEvent.ATLAS_LOADED, this._name));
			}
			return;
		}

		private function onXmlLoaderErrorHandler(event:IOErrorEvent):void
		{
			this._xmlData = null;
			this.xmlLoaderFini();
			this._xmlStatus = Atlas.FAILURE;
			return;
		}

		private function parseXmlData(data:Object):Dictionary
		{
			var xmlDataObject:Dictionary = new Dictionary(true);
			var topXmlObject:XML = new XML(data);
			var subXmlObject:XML = null;
			var atlasItemVO:AtlasItemVO = null;
			for each(subXmlObject in topXmlObject.SubTexture)
			{
				atlasItemVO = new AtlasItemVO();
				atlasItemVO.name = subXmlObject.child("name");
				atlasItemVO.x = parseInt(subXmlObject.x);
				atlasItemVO.y = parseInt(subXmlObject.y);
				atlasItemVO.width = parseInt(subXmlObject.width);
				atlasItemVO.height = parseInt(subXmlObject.height);
				xmlDataObject[atlasItemVO.name] = atlasItemVO;
			}
			return xmlDataObject;
		}

		private function imgLoaderInit():void
		{
			this.addImgLoaderListeners();
			return;
		}

		private function imgLoaderFini():void
		{
			this._imgLoader.unload();
			this.delImgLoaderListeners();
			return;
		}

		private function xmlLoaderInit():void
		{
			this.addXmlLoaderListeners();
			return;
		}

		private function xmlLoaderFini():void
		{
			// Unload is not required.
			this.delXmlLoaderListeners();
			return;
		}

		public function get name():String
		{
			return this._name;
		}

		public function set name(value:String):void
		{
			if (value && value != this._name)
			{
				this._name = value;
				this.imgLoaderInit();
				this._imgStatus = Atlas.LOADING;
				var atlasImg:String = this._path + "/" + this._name + ".png";
				var imgUrlRequest:URLRequest = new URLRequest(atlasImg);
				var imgLoaderContext:LoaderContext = new LoaderContext(false, ApplicationDomain.currentDomain);
				this._imgLoader.load(imgUrlRequest, imgLoaderContext);
				this.xmlLoaderInit();
				this._xmlStatus = Atlas.LOADING;
				var atlasXml:String = this._path + "/" + this._name + ".xml";
				var xmlUrlRequest:URLRequest = new URLRequest(atlasXml);
				this._xmlLoader.load(xmlUrlRequest);
			}
			return;
		}

		public function isLoaded():Boolean
		{
			return this._imgStatus == Atlas.SUCCESS && this._xmlStatus == Atlas.SUCCESS;
		}

		public function drawGraphics(itemName:String, targetGraphics:Graphics, smooth:Boolean=false, repeat:Boolean=false, center:Boolean=false):void
		{
			if (this._imgStatus == Atlas.SUCCESS && this._xmlStatus == Atlas.SUCCESS)
			{
				var atlasItemVO:AtlasItemVO = this._xmlData[itemName];
				var extOffsetX:int = 0;
				var extOffsetY:int = 0;
				var offsetMatrix:Matrix = new Matrix();

				if (atlasItemVO)
				{
					if (center)
					{
						extOffsetX = -(atlasItemVO.width >> 1);
						extOffsetY = -(atlasItemVO.height >> 1);
					}
					offsetMatrix.translate(-atlasItemVO.x + extOffsetX, -atlasItemVO.y + extOffsetY);
					targetGraphics.clear();
					targetGraphics.beginBitmapFill(this._imgData, offsetMatrix, repeat, smooth);
					targetGraphics.drawRect(extOffsetX, extOffsetY, atlasItemVO.width, atlasItemVO.height);
					targetGraphics.endFill();
				}
			}
			return;
		}

		public function dispose():void
		{
			if (this._imgStatus != Atlas.SUCCESS && this.imgStatus != Atlas.FAILURE)
			{
				this._imgLoader.close();
			}
			this._imgLoader = null;
			if (this._xmlStatus != Atlas.SUCCESS && this._xmlStatus != Atlas.FAILURE)
			{
				this._xmlLoader.close();
			}
			this._xmlLoader = null;
			if (this._imgData)
			{
				this._imgData.dispose();
				this._imgData = null;
			}
			if (this._xmlData)
			{
				// Dispose is not required.
				this._xmlData = null;
			}
			return;
		}
	}
}
