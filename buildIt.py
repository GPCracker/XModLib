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

def compile_source(source, filename='<string>', filetime=time.time()):
	with io.BytesIO() as bytesIO:
		bytesIO.write(imp.get_magic())
		bytesIO.write(struct.pack('<I', int(filetime)))
		bytesIO.write(marshal.dumps(compile(source, filename, 'exec')))
		result = bytesIO.getvalue()
	return result

def join_path(*args, **kwargs):
	path = os.path.normpath(os.path.join(*args, **kwargs)).replace(os.sep, '/')
	return path + ('/' if os.path.isdir(path) else '')

def source_iterator(src_list, sourcePath='./'):
	for source in src_list:
		_source = join_path(sourcePath, source)
		if os.path.isfile(_source):
			yield join_path(source)
		elif os.path.isdir(_source):
			for root, dirs, files in os.walk(_source):
				root = os.path.relpath(root, _source)
				for file in files:
					yield join_path(source, root, file)
	return

def resource_iterator(res_list, resourcePath='./'):
	for resource, target in res_list:
		_resource = join_path(resourcePath, resource)
		if os.path.isfile(_resource):
			yield join_path(resource), join_path(target)
		elif os.path.isdir(_resource):
			for root, dirs, files in os.walk(_resource):
				root = os.path.relpath(root, _resource)
				for file in files:
					yield join_path(resource, root, file), join_path(target, root, file)
	return

def process_source(source, fzip, version, versionMacros='<version>', sourcePath='./', buildPath='./build/', zipPath='./'):
	src_file = join_path(sourcePath, source)
	dst_name = os.path.splitext(source)[0] + '.pyc'
	dst_file = join_path(buildPath, dst_name)
	zip_file = join_path(zipPath, dst_name)
	print '{0} --> {1}'.format(src_file, dst_file)
	if not os.path.isdir(os.path.dirname(dst_file)):
		os.makedirs(os.path.dirname(dst_file))
	with open(src_file, 'rt') as f:
		source = f.read().replace(versionMacros, version)
	with open(dst_file, 'wb') as f:
		f.write(compile_source(source, src_file, os.path.getmtime(src_file)))
	fzip.write(dst_file, zip_file)
	return

def process_resource(resource, target, fzip, resourcePath='./'):
	src_file = join_path(resourcePath, resource)
	print '{0} --> {1}'.format(src_file, '<release>')
	fzip.write(src_file, target)
	return

if __name__ == '__main__':
	try:
		cfg_file = join_path(os.path.splitext(__file__)[0] + '.cfg')
		with open(cfg_file, 'rb') as f:
			config = json.loads(f.read())
		vcs_file = join_path(os.path.dirname(__file__), 'version.cfg')
		version = '<custom_build>'
		if os.path.isfile(vcs_file):
			with open(vcs_file, 'r+b') as f:
				vcs_info = json.load(f)
				version = '{release}#{next_build}'.format(**vcs_info)
				vcs_info['next_build'] += 1
				f.seek(0)
				f.truncate()
				f.write(json.dumps(vcs_info) + '\n')
		application = config["application"]
		versionMacros = config["versionMacros"]
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
		with zipfile.ZipFile(join_path(releasePath, application + '.zip'), 'w', zipfile.ZIP_DEFLATED) as fzip:
			for source in source_iterator(sources, sourcePath):
				process_source(source, fzip, version, versionMacros, sourcePath, buildPath, zipPath)
			for resource, target in resource_iterator(resources, resourcePath):
				process_resource(resource, target, fzip, resourcePath)
	except:
		traceback.print_exc()
