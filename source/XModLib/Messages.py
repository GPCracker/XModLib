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
from .AppLoader import AppLoader

class Messenger(object):
	@staticmethod
	def getBattleChatControllers():
		squadChannelClientID = messenger.ext.channel_num_gen.getClientID4Prebattle(constants.PREBATTLE_TYPE.SQUAD)
		teamChannelClientID = messenger.ext.channel_num_gen.getClientID4BattleChannel(messenger.m_constants.BATTLE_CHANNEL.TEAM.name)
		commonChannelClientID = messenger.ext.channel_num_gen.getClientID4BattleChannel(messenger.m_constants.BATTLE_CHANNEL.COMMON.name)
		return (
			messenger.MessengerEntry.g_instance.gui.channelsCtrl.getController(squadChannelClientID),
			messenger.MessengerEntry.g_instance.gui.channelsCtrl.getController(teamChannelClientID),
			messenger.MessengerEntry.g_instance.gui.channelsCtrl.getController(commonChannelClientID)
		)

	@staticmethod
	def showMessageOnPanel(msgType, msgKey, msgText, msgColor):
		if AppLoader.getBattleApp() is not None and msgType in ['Vehicle', 'VehicleError', 'Player']:
			panel = AppLoader.getBattleApp().containerManager.getContainer(gui.Scaleform.framework.ViewTypes.VIEW).getView().components['battle' + msgType + 'Messages']
			methods = gui.Scaleform.daapi.view.battle.shared.messages.fading_messages._COLOR_TO_METHOD
			if msgColor in methods:
				getattr(panel, methods[msgColor])(msgKey, msgText)
		return

	@staticmethod
	def showMessageInChat(msgText):
		if messenger.MessengerEntry.g_instance is not None:
			messenger.MessengerEntry.g_instance.gui.addClientMessage(msgText)
		return

	@staticmethod
	def externalBrowserOpenURL(url):
		BigWorld.wg_openWebBrowser(url)
		return

class LobbyMessenger(object):
	@staticmethod
	def getGuiSettings(*args, **kwargs):
		return gui.shared.notifications.NotificationGuiSettings(*args, **kwargs)

	@staticmethod
	def appendFormatter(key, formatter):
		messenger.formatters.collections_by_type.CLIENT_FORMATTERS[key] = formatter
		return

	@staticmethod
	def pushClientMessage(message, key, *args, **kwargs):
		gui.SystemMessages.g_instance.proto.serviceChannel.pushClientMessage(message, key, *args, **kwargs)
		return

	@staticmethod
	def showSimpleDialog(title, text, buttons, handler=None):
		gui.DialogsInterface.showDialog(gui.Scaleform.daapi.view.dialogs.SimpleDialogMeta(title, text, buttons), handler)
		return

class SystemMessageFormatter(object):
	def isAsync(self):
		return False

	def isNotify(self):
		return True

	def __init__(self, guiSettings):
		self.guiSettings = guiSettings
		return

	def format(self, message, *args, **kwargs):
		return message, self.guiSettings

class SystemMessage(dict):
	protected_keys = {'icon', 'defaultIcon', 'bgIcon'}

	@property
	def defaults(self):
		return {
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
		for key, value in self.defaults.items():
			self.setdefault(key, value)
		return

	def __setitem__(self, key, value):
		if key not in self.protected_keys:
			super(SystemMessage, self).__setitem__(key, value)
		return

	def copy(self):
		return SystemMessage(self)

class SystemMessageButton(dict):
	@property
	def defaults(self):
		return {
			'action': '',
			'label': '',
			'type': 'submit'
		}

	def __init__(self, *args, **kwargs):
		super(SystemMessageButton, self).__init__(*args, **kwargs)
		for key, value in self.defaults.items():
			self.setdefault(key, value)
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

class SimpleDialogButtons(object):
	def __init__(self, buttons=None):
		self.buttons = buttons if buttons is not None else list()
		return None

	def getLabels(self):
		return self.buttons

class SimpleDialogButton(dict):
	@property
	def defaults(self):
		return {
			'id': '',
			'label': '',
			'focused': True
		}

	def __init__(self, *args, **kwargs):
		super(SimpleDialogButton, self).__init__(*args, **kwargs)
		for key, value in self.defaults.items():
			self.setdefault(key, value)
		return

class SimpleDialog(gui.Scaleform.daapi.view.dialogs.SimpleDialog.SimpleDialog):
	handler = lambda buttonID: None

	@classmethod
	def factory(sclass, name, handler=handler):
		return type(name, (sclass, ), {'handler': staticmethod(handler)})

	def onButtonClick(self, buttonID):
		self.handler(buttonID)
		return super(SimpleDialog, self).onButtonClick(buttonID)

	@classmethod
	def install(sclass, alias):
		gui.Scaleform.framework.g_entitiesFactories.addSettings(
			gui.Scaleform.framework.GroupedViewSettings(
				alias,
				sclass,
				'simpleDialog.swf',
				gui.Scaleform.framework.ViewTypes.TOP_WINDOW,
				'',
				None,
				gui.Scaleform.framework.ScopeTemplates.DYNAMIC_SCOPE
			)
		)
		return

	@staticmethod
	def loadView(alias, title, message, buttons=None):
		buttons = buttons if buttons is not None else list()
		AppLoader.getLobbyApp().loadView(alias, None, message, title, buttons, None)
		return
