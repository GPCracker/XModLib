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
import constants
import gui.app_loader
import gui.SystemMessages
import gui.DialogsInterface
import gui.shared.notifications
import gui.Scaleform.framework
import gui.Scaleform.framework.ViewTypes
import gui.Scaleform.daapi.settings.views
import gui.Scaleform.daapi.view.dialogs.SimpleDialog
import gui.Scaleform.daapi.view.battle.shared.messages.fading_messages
import notification.settings
import notification.NotificationMVC
import notification.actions_handlers
import messenger.MessengerEntry
import messenger.ext.channel_num_gen
import messenger.formatters.collections_by_type

# *************************
# X-Mod Library
# *************************
# Nothing

def getBattleChatControllers():
	squadChannelClientID = messenger.ext.channel_num_gen.getClientID4Prebattle(constants.PREBATTLE_TYPE.SQUAD)
	teamChannelClientID = messenger.ext.channel_num_gen.getClientID4BattleChannel(messenger.m_constants.BATTLE_CHANNEL.TEAM.name)
	commonChannelClientID = messenger.ext.channel_num_gen.getClientID4BattleChannel(messenger.m_constants.BATTLE_CHANNEL.COMMON.name)
	return (
		messenger.MessengerEntry.g_instance.gui.channelsCtrl.getController(squadChannelClientID),
		messenger.MessengerEntry.g_instance.gui.channelsCtrl.getController(teamChannelClientID),
		messenger.MessengerEntry.g_instance.gui.channelsCtrl.getController(commonChannelClientID)
	)

def showMessageOnPanel(msgType, msgKey, msgText, msgColor):
	battleApp = gui.app_loader.g_appLoader.getDefBattleApp()
	if battleApp is not None and msgType in ['Vehicle', 'VehicleError', 'Player']:
		battlePage = battleApp.containerManager.getContainer(gui.Scaleform.framework.ViewTypes.VIEW).getView()
		messagePanel = battlePage.components['battle' + msgType + 'Messages']
		messageMethods = gui.Scaleform.daapi.view.battle.shared.messages.fading_messages._COLOR_TO_METHOD
		if msgColor in messageMethods:
			getattr(messagePanel, messageMethods[msgColor])(msgKey, msgText)
	return

class SystemMessageFormatter(object):
	@staticmethod
	def makeGuiSettings(*args, **kwargs):
		return gui.shared.notifications.NotificationGuiSettings(*args, **kwargs)

	def isAsync(self):
		return False

	def isNotify(self):
		return True

	def __init__(self, guiSettings):
		self.guiSettings = guiSettings
		return

	def install(self, key):
		messenger.formatters.collections_by_type.CLIENT_FORMATTERS[key] = self
		return

	def format(self, message, *args, **kwargs):
		return message, self.guiSettings

class SystemMessage(dict):
	protected_keys = {'icon', 'defaultIcon', 'bgIcon'}
	default_values = {
		'message': '',
		'type': 'lightGrey',
		'timestamp': -1,
		'icon': '',
		'defaultIcon': '',
		'bgIcon': '',
		'filters': list(),
		'savedData': None,
		'buttonsLayout': list()
	}

	def __init__(self, *args, **kwargs):
		super(SystemMessage, self).__init__(*args, **kwargs)
		self.update((key, value) for key, value in self.default_values.iteritems() if key not in self)
		return

	def __setitem__(self, key, value):
		if key not in self.protected_keys:
			super(SystemMessage, self).__setitem__(key, value)
		return

	def push(self, key, *args, **kwargs):
		gui.SystemMessages._getSystemMessages().proto.serviceChannel.pushClientMessage(self, key, *args, **kwargs)
		return

	def copy(self):
		return self.__class__(self)

class SystemMessageButton(dict):
	default_values = {
		'action': '',
		'label': '',
		'type': 'submit'
	}

	def __init__(self, *args, **kwargs):
		super(SystemMessageButton, self).__init__(*args, **kwargs)
		self.update((key, value) for key, value in self.default_values.iteritems() if key not in self)
		return

class SystemMessageActionHandler(object):
	handler = lambda model, entityID, action: None

	@classmethod
	def factory(sclass, name, handler=handler):
		return type(name, (sclass, ), {'handler': staticmethod(handler)})

	@classmethod
	def install(sclass):
		actionsHandlers = notification.NotificationMVC.g_instance._NotificationMVC__actionsHandlers
		if actionsHandlers is not None:
			actionsHandlers._NotificationsActionsHandlers__multi[sclass.getNotType()].add(sclass)
		notification.actions_handlers._AVAILABLE_HANDLERS += (sclass, )
		return

	@classmethod
	def getNotType(sclass):
		return notification.settings.NOTIFICATION_TYPE.MESSAGE

	@classmethod
	def getActions(sclass):
		return ()

	def handleAction(self, model, entityID, action):
		self.handler(model, entityID, action)
		return
