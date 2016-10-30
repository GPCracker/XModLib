package net.GPCracker.base
{
	import flash.events.Event;

	public class AtlasEvent extends Event
	{
		public static const ATLAS_LOADED:String = "atlasLoaded";
		public static const ATLAS_IMG_LOADED:String = "atlasImgLoaded";
		public static const ATLAS_XML_LOADED:String = "atlasXmlLoaded";

		public var atlasName:String = null;

		public function AtlasEvent(type:String, atlasName:String, bubbles:Boolean=false, cancelable:Boolean=false)
		{
			super(type, bubbles, cancelable);
			this.atlasName = atlasName;
			return;
		}

		public override function clone():Event
		{
			return new AtlasEvent(this.type, this.atlasName, this.bubbles, this.cancelable);
		}
	}
}
