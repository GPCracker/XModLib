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
		bytesIO.write(struct.pack('<I', int(filetime)))
		bytesIO.write(marshal.dumps(compile(source, filename, 'exec')))
		result = bytesIO.getvalue()
	return result

def joinPath(*args, **kwargs):
	path = os.path.normpath(os.path.join(*args, **kwargs)).replace(os.sep, '/')
	return path + ('/' if os.path.isdir(path) else '')

def sourceIterator(src_list, sourcePath='./'):
	for source in src_list:
		_source = joinPath(sourcePath, source)
		if os.path.isfile(_source):
			yield joinPath(source)
		elif os.path.isdir(_source):
			for root, dirs, files in os.walk(_source):
				root = os.path.relpath(root, _source)
				for file in files:
					yield joinPath(source, root, file)
	return

def resourceIterator(res_list, resourcePath='./'):
	for resource, target in res_list:
		_resource = joinPath(resourcePath, resource)
		if os.path.isfile(_resource):
			yield joinPath(resource), joinPath(target)
		elif os.path.isdir(_resource):
			for root, dirs, files in os.walk(_resource):
				root = os.path.relpath(root, _resource)
				for file in files:
					yield joinPath(resource, root, file), joinPath(target, root, file)
	return

def processSource(source, fzip, sourcePath='./', buildPath='./build/', zipPath='./'):
	src_file = joinPath(sourcePath, source)
	dst_name = os.path.splitext(source)[0] + '.pyc'
	dst_file = joinPath(buildPath, dst_name)
	zip_file = joinPath(zipPath, dst_name)
	print '{0} --> {1}'.format(src_file, dst_file)
	if not os.path.isdir(os.path.dirname(dst_file)):
		os.makedirs(os.path.dirname(dst_file))
	with open(src_file, 'rt') as f:
		source = f.read()
	with open(dst_file, 'wb') as f:
		f.write(compileSource(source, src_file, os.path.getmtime(src_file)))
	fzip.write(dst_file, zip_file)
	return

def processResource(resource, target, fzip, resourcePath='./'):
	src_file = joinPath(resourcePath, resource)
	print '{0} --> {1}'.format(src_file, '<release>')
	fzip.write(src_file, target)
	return

if __name__ == '__main__':
	try:
		cfg_file = joinPath(os.path.splitext(__file__)[0] + '.cfg')
		with open(cfg_file, 'rb') as f:
			config = json.loads(f.read())
		application = config["application"]
		clientVersion = config["clientVersion"]
		sourcePath = config["sourcePath"].replace('<client>', clientVersion)
		buildPath = config["buildPath"].replace('<client>', clientVersion)
		releasePath = config["releasePath"].replace('<client>', clientVersion)
		resourcePath = config["resourcePath"].replace('<client>', clientVersion)
		zipPath = config["zipPath"].replace('<client>', clientVersion)
		sources = config["sources"]
		resources = config["resources"]
		if os.path.isdir(buildPath):
			shutil.rmtree(buildPath)
		if os.path.isdir(releasePath):
			shutil.rmtree(releasePath)
		os.makedirs(buildPath)
		os.makedirs(releasePath)
		with zipfile.ZipFile(joinPath(releasePath, application + '.zip'), 'w', zipfile.ZIP_DEFLATED) as fzip:
			for source in sourceIterator(sources, sourcePath):
				processSource(source, fzip, sourcePath, buildPath, zipPath)
			for resource, target in resourceIterator(resources, resourcePath):
				processResource(resource, target, fzip, resourcePath)
	except:
		traceback.print_exc()
