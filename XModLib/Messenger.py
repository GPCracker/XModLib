# Authors: GPCracker

# *************************
# Python
# *************************
# Nothing

# *************************
# BigWorld
# *************************
# Nothing

# *************************
# WoT Client
# *************************
import messenger
import constants

# *************************
# X-Mod Code Library
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
	def showMessageOnPanel(panel, key, msgText, color):
		if AppLoader.getBattleApp() is not None and panel in ['VehicleErrorsPanel', 'VehicleMessagesPanel', 'PlayerMessagesPanel']:
			AppLoader.getBattleApp().call('battle.' + panel + '.ShowMessage', [key, msgText, color])
		return

	@staticmethod
	def showMessageInChat(msgText):
		if messenger.MessengerEntry.g_instance is not None:
			messenger.MessengerEntry.g_instance.gui.addClientMessage(msgText)
		return
