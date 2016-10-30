package net.GPCracker.battle.views.components.panels
{
	import flash.events.MouseEvent;
	import net.GPCracker.battle.views.components.panels.elements.PanelBackground;
	import net.GPCracker.battle.views.components.panels.elements.PanelBorder;
	import net.GPCracker.battle.views.components.panels.elements.PanelText;
	import net.GPCracker.battle.meta.TextPanelMeta;
	import net.GPCracker.battle.interfaces.ITextPanel;

	public class TextPanel extends TextPanelMeta implements ITextPanel
	{
		private static const DEFAULT_WIDTH:Number = 100;
		private static const DEFAULT_HEIGHT:Number = 50;

		public var textBackground:PanelBackground = null;
		public var textBorder:PanelBorder = null;
		public var textField:PanelText = null;
		public var tooltip:String = "";

		public function TextPanel()
		{
			super();
			// Global parameters.
			this.buttonMode = true;
			this.tabEnabled = false;
			this.tabChildren = false;
			this.useHandCursor = true;
			this.mouseChildren = false;
			// Instance creation.
			this.textBackground = new PanelBackground();
			this.textBorder = new PanelBorder();
			this.textField = new PanelText();
			this.textBackground.name = "background";
			this.textBorder.name = "border";
			this.textField.name = "text";
			// Adding instances as children.
			this.addChild(this.textBackground);
			this.addChild(this.textBorder);
			this.addChildAt(this.textField, 1);
			// Instance configuration.
			this.setSize(TextPanel.DEFAULT_WIDTH, TextPanel.DEFAULT_HEIGHT);
			return;
		}

		private function registerMouseClickEvents():void
		{
			this.addEventListener(MouseEvent.MOUSE_DOWN, this.onDragStart);
			this.addEventListener(MouseEvent.MOUSE_UP, this.onDragStop);
			return
		}

		private function unregisterMouseClickEvents():void
		{
			this.removeEventListener(MouseEvent.MOUSE_DOWN, this.onDragStart);
			this.removeEventListener(MouseEvent.MOUSE_UP, this.onDragStop);
			return;
		}

		private function registerMouseHoverEvents():void
		{
			this.addEventListener(MouseEvent.MOUSE_OVER, this.onToolTipShow);
			this.addEventListener(MouseEvent.MOUSE_OUT, this.onToolTipHide);
			return;
		}

		private function unregisterMouseHoverEvents():void
		{
			this.removeEventListener(MouseEvent.MOUSE_OVER, this.onToolTipShow);
			this.removeEventListener(MouseEvent.MOUSE_OUT, this.onToolTipHide);
			return;
		}

		private function onDragStart(event:MouseEvent):void
		{
			App.toolTipMgr.hide();
			this.unregisterMouseHoverEvents();
			this.textBorder.setColor(0x000000);
			this.py_onPanelDragS(this.x, this.y);
			this.startDrag();
			return;
		}

		private function onDragStop(event:MouseEvent):void
		{
			this.stopDrag();
			this.py_onPanelDropS(this.x, this.y);
			this.textBorder.setColor(0x999999);
			this.registerMouseHoverEvents();
			App.toolTipMgr.show(this.tooltip);
			return;
		}

		private function onToolTipShow(event:MouseEvent):void
		{
			this.textBorder.setColor(0x999999);
			this.textBorder.visible = true;
			App.toolTipMgr.show(this.tooltip);
			return;
		}

		private function onToolTipHide(event:MouseEvent):void
		{
			App.toolTipMgr.hide();
			this.textBorder.visible = false;
			this.textBorder.setColor(0x999999);
			return;
		}

		private function setAlpha(alpha:Number):void
		{
			this.textBackground.alpha = alpha;
			this.textField.alpha = alpha;
			return;
		}

		private function setSize(width:Number, height:Number):void
		{
			this.textBackground.setContainerSize(width, height);
			this.textField.width = width;
			this.textField.height = height;
			this.textBorder.drawRect(this);
			return;
		}

		public function as_toggleCursor(enabled:Boolean):void
		{
			this.textBorder.visible = false;
			if (enabled)
			{
				this.registerMouseClickEvents();
				this.registerMouseHoverEvents();
			}
			else
			{
				this.unregisterMouseClickEvents()
				this.unregisterMouseHoverEvents()
			}
			return;
		}

		public function as_setBackground(image:String):void
		{
			this.textBackground.source = image;
			return;
		}

		public function as_setText(text:String):void
		{
			this.textField.htmlText = text;
			return;
		}

		public function as_setToolTip(tooltip:String):void
		{
			this.tooltip = tooltip;
			return;
		}

		public function as_setVisible(visible:Boolean):void
		{
			this.visible = visible;
			return;
		}

		public function as_setAlpha(alpha:Number):void
		{
			this.setAlpha(alpha);
			return;
		}

		public function as_setPosition(x:Number, y:Number):void
		{
			this.x = x;
			this.y = y;
			return;
		}

		public function as_setSize(width:Number, height:Number):void
		{
			this.setSize(width, height);
			return;
		}

		public function as_setTextShadow(alpha:Number, angle:Number, blur:Number, color:Number, distance:Number, strength:Number):void
		{
			this.textField.setShadow(alpha, angle, blur, color, distance, strength);
			return;
		}

		public function as_applyConfig(config:Object):void
		{
			if (config)
			{
				if (config.alpha != undefined && config.alpha is Number)
				{
					this.setAlpha(config.alpha);
				}
				if (config.visible != undefined && config.visible is Boolean)
				{
					this.visible = config.visible;
				}
				if (config.background != undefined && config.background is String)
				{
					this.textBackground.source = config.background;
				}
				if (config.tooltip != undefined && config.tooltip is String)
				{
					this.tooltip = config.tooltip;
				}
				if (config.text != undefined && config.text is String)
				{
					this.textField.htmlText = config.text;
				}
				if (config.position != undefined && config.position is Array && config.position.length == 2)
				{
					this.x = config.position[0];
					this.y = config.position[1];
				}
				if (config.size != undefined && config.size is Array && config.size.length == 2)
				{
					this.setSize(config.size[0], config.size[1]);
				}
			}
			return;
		}
	}
}
