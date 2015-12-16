import io
import os
import imp
import json
import time
import shutil
import struct
import marshal
import zipfile
import traceback

def compileSource(source, filename = '<string>', filetime = time.time()):
	with io.BytesIO() as bytesIO:
		bytesIO.write(imp.get_magic())
		bytesIO.write(struct.pack('I', int(filetime)))
		bytesIO.write(marshal.dumps(compile(source, filename, 'exec')))
		result = bytesIO.getvalue()
	return result

def processFile(src_file, dst_file, zip_file, fzip, isCode=False):
	print '{0} --> {1}'.format(src_file, dst_file)
	if not os.path.isdir(os.path.dirname(dst_file)):
		os.makedirs(os.path.dirname(dst_file))
	with open(src_file, 'rt' if isCode else 'rb') as f:
		source = f.read()
	with open(dst_file, 'wb') as f:
		f.write(compileSource(source, src_file, os.path.getmtime(src_file)) if isCode else source)
	fzip.write(dst_file, zip_file)
	return

if __name__ == '__main__':
	try:
		cfg_file = (os.path.splitext(__file__)[0] + '.cfg').replace(os.sep, '/')
		with open(cfg_file, 'rt') as f:
			config = json.load(f)
		application = config["application"]
		sources = config["sources"]
		buildPath = config["buildPath"]
		releasePath = config["releasePath"]
		zipPath = config["zipPath"]
		if os.path.isdir(buildPath):
			shutil.rmtree(buildPath)
		if os.path.isdir(releasePath):
			shutil.rmtree(releasePath)
		os.makedirs(buildPath)
		os.makedirs(releasePath)
		with zipfile.ZipFile(os.path.join(releasePath, application + '.zip').replace(os.sep, '/'), 'w', zipfile.ZIP_DEFLATED) as fzip:
			for source in sources:
				source = os.path.relpath(source)
				if os.path.isfile(source):
					isCode = os.path.splitext(source)[1] == '.py'
					src_file = os.path.join('.', source).replace(os.sep, '/')
					dst_name = (os.path.splitext(source)[0] + '.pyc') if isCode else source
					dst_file = os.path.join(buildPath, dst_name).replace(os.sep, '/')
					zip_file = os.path.join(zipPath, dst_name).replace(os.sep, '/')
					processFile(src_file, dst_file, zip_file, fzip, isCode)
				elif os.path.isdir(source):
					for root, dirs, files in os.walk(source):
						for file in files:
							isCode = os.path.splitext(file)[1] == '.py'
							src_file = os.path.join('.', root, file).replace(os.sep, '/')
							dst_name = (os.path.splitext(file)[0] + '.pyc') if isCode else file
							dst_file = os.path.join(buildPath, root, dst_name).replace(os.sep, '/')
							zip_file = os.path.join(zipPath, root, dst_name).replace(os.sep, '/')
							processFile(src_file, dst_file, zip_file, fzip, isCode)
	except:
		traceback.print_exc()
