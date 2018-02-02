package net.GPCracker.base
{
	import net.GPCracker.interfaces.IAtlasItemVO;

	public class AtlasItemVO extends Object implements IAtlasItemVO
	{
		private var _name:String = null;
		private var _x:int = 0;
		private var _y:int = 0;
		private var _width:int = 0;
		private var _height:int = 0;

		public function AtlasItemVO()
		{
			super();
			return;
		}

		public function get name():String
		{
			return this._name;
		}

		public function set name(value:String):void
		{
			this._name = value;
			return;
		}

		public function get x():int
		{
			return this._x;
		}

		public function set x(value:int):void
		{
			this._x = value;
			return;
		}

		public function get y():int
		{
			return this._y;
		}

		public function set y(value:int):void
		{
			this._y = value;
			return;
		}

		public function get width():int
		{
			return this._width;
		}

		public function set width(value:int):void
		{
			this._width = value;
			return;
		}

		public function get height():int
		{
			return this._height;
		}

		public function set height(value:int):void
		{
			this._height = value;
			return;
		}
	}
}
