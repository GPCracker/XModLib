# Authors: Vladislav Ignatenko <gpcracker@mail.ru>

# ------------ #
#    Python    #
# ------------ #
import string
import itertools

# -------------- #
#    BigWorld    #
# -------------- #
# nothing

# ---------------- #
#    WoT Client    #
# ---------------- #
import helpers
import constants

# ------------------- #
#    X-Mod Library    #
# ------------------- #
from . import Versioning

# -------------------- #
#    Module Content    #
# -------------------- #
def getClientVersion():
	realm = constants.CURRENT_REALM.lower()
	version = helpers.getShortClientVersion().strip()
	return Versioning.ProvidedClientVersion(realm, Versioning.Version.parseVersion(version))

def isCompatibleClientVersion(required=(None, None)):
	def parseRequiredVersion(realms, version):
		realms = tuple(itertools.imap(string.lower, realms)) if realms not in ('any-realm', None) else ()
		version = Versioning.Version.parseVersion(version) if version not in ('any-version', None) else ()
		return Versioning.RequiredClientVersion(realms, version)
	return getClientVersion().isClientVersionCompatible(parseRequiredVersion(*required))
