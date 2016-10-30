package net.GPCracker.battle.views.components.panels
{
	import net.GPCracker.battle.views.components.panels.TextPanel;

	public function getPanelClassReference(classAlias:String):Class
	{
		var classReference:Class = null;
		switch (classAlias)
		{
			case "TextPanel": classReference = TextPanel; break;
		}
		return classReference;
	}
}
