package net.GPCracker.battle.library
{
	import net.wg.gui.battle.views.BaseBattlePage;
	import net.wg.infrastructure.base.BaseBattleDAAPIComponent;

	import net.GPCracker.battle.library.ComponentsLoaderLibraryMain;
	import net.GPCracker.battle.views.components.panels.getPanelClassReference;

	public class PanelsLoaderLibraryMain extends ComponentsLoaderLibraryMain
	{
		public function PanelsLoaderLibraryMain()
		{
			super();
			BaseBattlePage.prototype['as_createBattlePagePanel'] = function(panelAlias:String, panelClass:String, panelIndex:Number=-1):void
			{
				var ClassReference:Class = getPanelClassReference(panelClass);
				if (ClassReference)
				{
					var battlePagePanel:BaseBattleDAAPIComponent = new ClassReference();
					this.registerExternalComponent(battlePagePanel, panelAlias, panelIndex);
				}
				return;
			};
			return;
		}
	}
}
