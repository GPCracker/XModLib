package net.GPCracker
{
	import net.GPCracker.base.AtlasManager;
	import net.GPCracker.interfaces.IAtlasManager;

	public class Application
	{
		private static var _atlasManager:IAtlasManager = new AtlasManager();

		public static function get atlasManager():IAtlasManager
		{
			return Application._atlasManager;
		}
	}
}
