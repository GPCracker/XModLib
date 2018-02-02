package net.GPCracker.battle.views
{
	import net.wg.gui.battle.views.BaseBattlePage;
	import net.wg.infrastructure.base.BaseBattleDAAPIComponent;

	import net.GPCracker.battle.views.LoaderViewBase;
	import net.GPCracker.battle.views.components.panels.getPanelClassReference;

	public class PanelsLoaderView extends LoaderViewBase
	{
		public function PanelsLoaderView()
		{
			super();
			return;
		}

		public function as_createBattlePagePanel(panelAlias:String, panelClass:String, panelIndex:Number=-1):void
		{
			var battlePage:BaseBattlePage = this.getBattlePage();
			var ClassReference:Class = getPanelClassReference(panelClass);
			if (battlePage && ClassReference)
			{
				var battlePagePanel:BaseBattleDAAPIComponent = new ClassReference();
				battlePagePanel.name = panelAlias;
				this.registerBattleComponent(battlePage, battlePagePanel, panelAlias, panelIndex);
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
