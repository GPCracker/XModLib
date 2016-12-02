import os
import sys
import shutil
import traceback
import subprocess

def detect_flex():
	if os.getenv('FLEX_HOME') is None:
		if os.name == 'posix':
			flex_home = '/opt/apache-flex'
		elif os.name == 'nt':
			flex_home = '$LOCALAPPDATA/FlashDevelop/Apps/flexsdk/4.6.0'
		else:
			raise RuntimeError('Current operation system is not supported.')
		os.environ['FLEX_HOME'] = os.path.expandvars(flex_home)
	return

if __name__ == '__main__':
	try:
		# Detecting flex.
		detect_flex()
		# Calculating args.
		flex_args = map(os.path.expandvars, [
			'java', '-Xmx384m', '-Dsun.io.useCanonCaches=false',
			'-jar', '$FLEX_HOME/lib/compc.jar', '+flexlib=$FLEX_HOME/frameworks',
			'-output', 'bin/XModLib.swc',
			'-external-library-path+=swc/wg_battle.swc',
			'-include-sources+=src'
		])
		# Starting flex.
		return_code = subprocess.call(flex_args)
	except:
		traceback.print_exc()
	sys.exit(return_code)
