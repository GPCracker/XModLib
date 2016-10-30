## X-Mod Library

X-Mod is a code library for World of Tanks mods. It provides

* Simple access to arena requests (score, squad, player status)
* Simple callback control and callback-based classes
* Client version getting and comparison
* Collision test functions
* WG-XML-based config reader (ResMgr supports specific BigWorld classes, like Matrix, Vectors)
* 3D Geometry helpers, planes and bounding box calculations
* BW-GUI wrapper, provides easier access to BW GUI elements
* Code helpers (events, triggers)
* Hook control class (simple hook injection with decorators)
* Keyboard helper (key event parser, key sequence builder and parser)
* Python string format decorator (custom macros header and trailer)
* Messenger wrappers (chat message displaying or sending)
* Minimap entry manager (simple minimap entries creation or removing)
* PathFinder module (gets full path to file by ResMgr relative path)
* Sound events and queues
* Umlaut decoder for BW GUI texts
* Vehicle info class (vehicle entity-based info)
* Vehicle math module (model calculations and matrix transformations)

## X-Mod Library Usage

X-Mod is an important part (a core module) of several mods and is being developed as a common script storage for them. This approach prevents code doubling between mods, providing single change history. Author does not aim to implement features required in neither of his mods here.

## Updating, Bugs, Errors, Discussion

Author tries to update library as soon as possible after new WoT patch released, but if you need it "just now" or you want to use it on specific game client version, you can fix it yourself. Feature requests and bug reports should be made in official topics of appropriate mods.
