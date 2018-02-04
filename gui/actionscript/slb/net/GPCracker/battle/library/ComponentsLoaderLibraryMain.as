package net.GPCracker.battle.library
{
	import flash.display.MovieClip;
	import net.wg.gui.battle.views.BaseBattlePage;
	import net.wg.infrastructure.base.BaseDAAPIComponent;
	import net.wg.infrastructure.base.BaseBattleDAAPIComponent;

	public class ComponentsLoaderLibraryMain extends MovieClip
	{
		public function ComponentsLoaderLibraryMain()
		{
			super();
			BaseBattlePage.prototype['registerExternalComponent'] = function(componentObject:MovieClip, componentAlias:String, componentIndex:Number=-1):void
			{
				if (componentObject is BaseDAAPIComponent || componentObject is BaseBattleDAAPIComponent)
				{
					this.constructor.prototype[componentAlias] = null;
					this[componentAlias] = componentObject;
					componentObject.name = componentAlias;
					if (0 <= componentIndex < this.numChildren)
					{
						this.addChildAt(componentObject, componentIndex);
					}
					else
					{
						this.addChild(componentObject);
					}
					this.registerFlashComponentS(componentObject, componentAlias);
				}
				else
				{
					DebugUtils.LOG_DEBUG("Invalid type of component object. Unable to register ExternalBattlePageComponent.");
				}
				return;
			};
			return;
		}
	}
}
