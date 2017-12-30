# Authors: Vladislav Ignatenko <gpcracker@mail.ru>

# ------------ #
#    Python    #
# ------------ #
import collections

# -------------- #
#    BigWorld    #
# -------------- #
import BigWorld

# ---------------- #
#    WoT Client    #
# ---------------- #
import constants
import gui.app_loader
import gui.SystemMessages
import gui.shared.notifications
import gui.Scaleform.framework.ViewTypes
import gui.Scaleform.daapi.view.battle.shared.messages.fading_messages
import notification.settings
import notification.NotificationMVC
import notification.actions_handlers
import messenger.MessengerEntry
import messenger.ext.channel_num_gen
import messenger.formatters.service_channel
import messenger.formatters.collections_by_type

# ------------------- #
#    X-Mod Library    #
# ------------------- #
# nothing

# -------------------- #
#    Module Content    #
# -------------------- #
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
		messageMethods = gui.Scaleform.daapi.view.battle.shared.messages.fading_messages._COLOR_TO_METHOD
		if msgColor in messageMethods:
			getattr(battlePage.components['battle' + msgType + 'Messages'], messageMethods[msgColor])(msgKey, msgText)
	return

def pushSystemMessage(msgData, msgType, isAlert=False, auxData=None):
	return gui.SystemMessages._getSystemMessages().proto.serviceChannel.pushClientMessage(msgData, msgType, isAlert=isAlert, auxData=auxData)

class SystemMessage(dict):
	def __setitem__(self, key, value):
		if key not in ('icon', 'bgIcon', 'defaultIcon'):
			super(SystemMessage, self).__setitem__(key, value)
		return

	def copy(self):
		return self.__class__(self)

class SystemMessageButton(dict):
	'''
	type('submit', 'cancel'), label, action, [width]
	'''
	def __init__(self, *args, **kwargs):
		super(SystemMessageButton, self).__init__(*args, **kwargs)
		self.setdefault('type', 'submit')
		self.setdefault('label', '')
		self.setdefault('action', '')
		return

class SystemMessageData(collections.namedtuple('SystemMessageData', ('data', 'settings'))):
	__slots__ = ()

	def __new__(cls, data=None, settings=None):
		return super(SystemMessageData, cls).__new__(cls, data, settings)

class SystemMessageFormatter(messenger.formatters.service_channel.ServiceChannelFormatter):
	def _getGuiSettings(self, auxData=None):
		return gui.shared.notifications.NotificationGuiSettings(isNotify=self.isNotify(), auxData=auxData)

	def format(self, message, *args):
		formatted = SystemMessage(message)
		formatted.setdefault('message', '')
		formatted.setdefault('type', 'lightGrey')
		formatted.setdefault('icon', '')
		formatted.setdefault('bgIcon', '')
		formatted.setdefault('defaultIcon', '')
		formatted.setdefault('timestamp', -1)
		formatted.setdefault('filters', list())
		formatted.setdefault('savedData', None)
		formatted.setdefault('buttonsLayout', list())
		return [SystemMessageData(formatted, self._getGuiSettings(*args)), ]

	def install(self, msgType):
		messenger.formatters.collections_by_type.CLIENT_FORMATTERS[msgType] = self
		return

class _SystemMessageActionHandler(notification.actions_handlers._ActionHandler):
	@classmethod
	def getNotType(cls):
		return notification.settings.NOTIFICATION_TYPE.MESSAGE

	@staticmethod
	def handleAction(model, entityID, action):
		raise NotImplementedError
		return

	@classmethod
	def install(cls):
		actionsHandlers = notification.NotificationMVC.g_instance._NotificationMVC__actionsHandlers
		if actionsHandlers is not None:
			actionsHandlers._NotificationsActionsHandlers__multi[cls.getNotType()].add(cls)
		notification.actions_handlers._AVAILABLE_HANDLERS += (cls, )
		return

def SystemMessageActionHandler(handler):
	return type('SystemMessageActionHandler', (_SystemMessageActionHandler, ), {'handleAction': staticmethod(handler)})
