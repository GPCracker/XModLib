# Authors: GPCracker

# *************************
# Python
# *************************
# Nothing

# *************************
# BigWorld
# *************************
import BigWorld

# *************************
# WoT Client
# *************************
import items.vehicles

# *************************
# X-Mod Code Library
# *************************
from .ArenaInfo import ArenaInfo

## Warning! This file should be updated!
## Large amount of changes is required here!
## Do not use it in new versions!

class TagsGroup(object):
	def __init__(self, include=None, exclude=None):
		self._include = frozenset(include if include is not None else tuple())
		self._exclude = frozenset(exclude if exclude is not None else tuple())
		if self._include & self._exclude:
			raise AssertionError('Tags intersection detected. Check include and exclude tag sets.')
		return

	@property
	def include(self):
		return self._include

	@property
	def exclude(self):
		return self._exclude

	def __hash__(self):
		return hash((self._include, self._exclude))

	def __repr__(self):
		return 'TagsGroup(include={!r}, exclude={!r})'.format(self._include, self._exclude)

	def __call__(self, tags):
		return tags & self._include == self._include and not tags & self._exclude

class TagsFilter(object):
	def __init__(self, groups=None, activated=True):
		self._groups = frozenset(groups if groups is not None else tuple())
		self.activated = activated
		return

	@property
	def groups(self):
		return self._groups

	def __hash__(self):
		return hash(self._groups)

	def __repr__(self):
		return 'TagsFilter(groups={!r}, activated={!r})'.format(self._groups, self.activated)

	def __call__(self, tags):
		return any(map(lambda group: group(tags), self._groups))

class Entity(object):
	def __init__(self):
		return

	def __hash__(self):
		return hash(())

	def __repr__(self):
		return 'Entity()'

	def __del__(self):
		return

class FilterSettings(object):
	def __init__(self, eclass=Entity):
		self._eclass = eclass
		return

	@property
	def eclass(self):
		return self._eclass

	def __hash__(self):
		return hash(())

	def __repr__(self):
		return 'FilterSettings()'

	def __call__(self, vehicle):
		return self._eclass()

class VehicleFilter(TagsFilter):
	def __init__(self, groups=None, settings=None, activated=True):
		super(VehicleFilter, self).__init__(groups, activated)
		self._settings = frozenset(settings if settings is not None else tuple())
		return

	@property
	def settings(self):
		return self._settings

	def __repr__(self):
		return 'VehicleFilter(groups={!r}, settings={!r}, activated={!r})'.format(self._groups, self._settings, self.activated)

class VehicleHandle(object):
	def __init__(self, vehicle, vfilter, activated=True):
		self._entities = None
		self._vehicle = vehicle
		self._vfilter = vfilter
		self.activated = activated
		if self.activated and self._vfilter.activated:
			self._addEntities()
		return

	def _addEntities(self):
		self._entities = set([settings(self._vehicle) for settings in self._vfilter.settings])
		return

	def _delEntities(self):
		self._entities = set()
		return

	@property
	def entities(self):
		return self._entities

	@property
	def vehicle(self):
		return self._vehicle

	@property
	def vfilter(self):
		return self._vfilter

	def update(self):
		activated = self.activated and self._vfilter.activated
		if activated != bool(self._entities):
			if activated:
				self._addEntities()
			else:
				self._delEntities()
		return

	def redraw(self):
		if self._entities:
			self._delEntities()
		if self.activated and self._vfilter.activated:
			self._addEntities()
		return

	def __hash__(self):
		return hash(self._vehicle)

	def __repr__(self):
		return 'VehicleHandle(vehicle={!r}, vfilter={!r}, activated={!r})'.format(self._vehicle, self._vfilter, self.activated)

	def __del__(self):
		if self._entities:
			self._delEntities()
		return

class VehicleManager(object):
	VEHICLE_TAGS = frozenset({'alive', 'ally', 'teamkiller', 'squad', 'player', 'target', 'autoaim'}) | items.vehicles.VEHICLE_CLASS_TAGS

	@staticmethod
	def getVehicleTags(vehicle):
		tags = set()
		if vehicle.isAlive():
			tags.add('alive')
		if vehicle.publicInfo['team'] == BigWorld.player().team:
			tags.add('ally')
		if ArenaInfo.isTeamKiller(vehicle.id):
			tags.add('teamkiller')
		if ArenaInfo.isSquadMan(vehicle.id):
			tags.add('squad')
		if vehicle.isPlayer:
			tags.add('player')
		if vehicle == BigWorld.player().target:
			tags.add('target')
		if vehicle == BigWorld.player().autoAimVehicle:
			tags.add('autoaim')
		tags |= vehicle.typeDescriptor.type.tags & items.vehicles.VEHICLE_CLASS_TAGS
		return frozenset(tags)

	def __init__(self, vfilters=None, vhandles=None, activated=True, vhclass=VehicleHandle):
		self._vhclass = vhclass
		self._vfilters = dict(vfilters if vfilters is not None else tuple())
		self._vhandles = dict(vhandles if vhandles is not None else tuple())
		self.activated = activated
		self.updateHandles()
		return

	@property
	def vhclass(self):
		return self._vhclass

	@property
	def vfilters(self):
		return self._vfilters

	@property
	def vhandles(self):
		return self._vhandles

	def updateHandle(self, vehicle):
		vfilter = self.getFilter(vehicle)
		self._vhandles[vehicle] = self._vhclass(vehicle, vfilter, self.activated) if vfilter is not None else None
		return

	def removeHandle(self, vehicle):
		self._vhandles.pop(vehicle, None)
		return

	def updateHandles(self, vfilter=None):
		for handle in self._vhandles.itervalues():
			if handle is not None and (vfilter is None or handle.vfilter == vfilter):
				handle.activated = self.activated
				handle.update()
		return

	def redrawHandles(self, vfilter=None):
		for handle in self._vhandles.itervalues():
			if handle is not None and (vfilter is None or handle.vfilter == vfilter):
				handle.activated = self.activated
				handle.redraw()
		return

	def getFilter(self, vehicle):
		vtags = self.getVehicleTags(vehicle)
		vfilters = filter(lambda vfilter: vfilter(vtags), self._vfilters.iterkeys())
		if vfilters:
			if len(vfilters) != 1:
				raise AssertionError('VehicleFilter double-pass is forbidden. Check filters and their tag groups.')
			return vfilters.pop()
		return None

	def handleShortcut(self, event):
		for vfilter, fshortcut in self._vfilters.iteritems():
			shandle = fshortcut(event)
			if shandle is not None:
				vfilter.activated = shandle(vfilter.activated)
				self.updateHandles(vfilter)
		return

	def __del__(self):
		return
