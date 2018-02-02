package net.GPCracker.battle.views
{
	import flash.display.MovieClip;
	import flash.display.DisplayObjectContainer;
	import net.wg.gui.battle.views.BaseBattlePage;
	import net.wg.infrastructure.base.BaseDAAPIComponent;
	import net.wg.infrastructure.base.BaseBattleDAAPIComponent;

	import net.GPCracker.battle.meta.LoaderViewBaseMeta;
	import net.GPCracker.battle.interfaces.ILoaderViewBase;

	public class LoaderViewBase extends LoaderViewBaseMeta implements ILoaderViewBase
	{
		public function LoaderViewBase()
		{
			super();
			return;
		}

		protected function getBattlePage():BaseBattlePage
		{
			var battleApp:DisplayObjectContainer = this.stage.getChildByName("root1") as DisplayObjectContainer;
			if (battleApp)
			{
				var battleViews:DisplayObjectContainer = battleApp.getChildByName("views") as DisplayObjectContainer;
				if (battleViews)
				{
					var battlePage:BaseBattlePage = battleViews.getChildByName("main") as BaseBattlePage;
					if (battlePage)
					{
						return battlePage;
					}
				}
			}
			return null;
		}

		protected function registerBattleComponent(parentObject:MovieClip, childObject:MovieClip, childAlias:String, componentIndex:Number=-1):void
		{
			var parentGood:Boolean = parentObject is BaseDAAPIComponent || parentObject is BaseBattleDAAPIComponent;
			var childGood:Boolean = childObject is BaseDAAPIComponent || childObject is BaseBattleDAAPIComponent;
			if (parentGood && childGood)
			{
				parentObject.constructor.prototype[childAlias] = null;
				parentObject[childAlias] = childObject;
				if (0 <= componentIndex < parentObject.numChildren)
				{
					parentObject.addChildAt(parentObject[childAlias], componentIndex);
				}
				else
				{
					parentObject.addChild(parentObject[childAlias]);
				}
				parentObject.registerFlashComponentS(parentObject[childAlias], childAlias);
			}
			else
			{
				DebugUtils.LOG_DEBUG("Invalid type of parent or child objects. Unable to register BattleComponent.");
			}
			return;
		}

		override protected function onPopulate():void
		{
			super.onPopulate();
			return;
		}

		override protected function onDispose():void
		{
			super.onDispose();
			return;
		}
	}
}
