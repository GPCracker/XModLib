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
import Account

# *************************
# X-Mod Code Library
# *************************
# Nothing

class ClientInfo(object):
	@staticmethod
	def getClientVersion():
		'''
		getClientVersion() -> cluster, version, patch
		'''
		return Account._readClientServerVersion()[1].split('_')

	@classmethod
	def isCompatibleClientVersion(sclass, application = [None, None, None]):
		client = sclass.getClientVersion()
		return all([
			application[0] is None or client[0] in application[0],
			application[1] is None or client[1] == application[1],
			application[2] is None or client[2] == application[2]
		])
