import io
import os
import imp
import json
import time
import shutil
import struct
import marshal
import zipfile
import operator
import functools
import itertools
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

def compile_flash_project(fdp_filename):
	args = ['tools/fdbuild/fdbuild.exe', '-notrace', '-compiler:$FLEX_HOME', fdp_filename]
	if os.name == 'posix':
		args.insert(0, 'mono')
	elif os.name != 'nt':
		raise RuntimeError('Current operation system is not supported.')
	args = map(os.path.expandvars, args)
	fdbuild_process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout_data, stderr_data = fdbuild_process.communicate()
	if fdbuild_process.poll():
		# Output compiler return.
		print '[FDBuild stdout] >>>'
		print stdout_data
		print '--------------------'
		print stderr_data
		print '<<< [FDBuild stderr]'
		raise RuntimeError('An error occured while compiling ActionScript project.')
	return

def compile_python_string(source, filename='<string>', filetime=time.time()):
	with io.BytesIO() as dst_bin_buffer:
		dst_bin_buffer.write(imp.get_magic())
		dst_bin_buffer.write(struct.pack('<I', int(filetime)))
		dst_bin_buffer.write(marshal.dumps(compile(source, filename, 'exec')))
		dst_bin_data = dst_bin_buffer.getvalue()
	return dst_bin_data

def compile_gettext_string(src_bin_data):
	if os.name == 'posix':
		msgfmt = 'msgfmt'
	elif os.name == 'nt':
		msgfmt = 'tools/gettext/msgfmt.exe'
	else:
		raise RuntimeError('Current operation system is not supported.')
	gettext_process = subprocess.Popen([msgfmt, '-', '-o', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	dst_bin_data = gettext_process.communicate(src_bin_data)[0]
	if gettext_process.poll():
		raise RuntimeError('An error occured while compiling localization file.')
	return dst_bin_data

def compile_atlas(dst_atlas, src_wildcards, src_basepath, ext_args=None):
	dst_basepath, dst_basename = os.path.split(dst_atlas)
	args = ['python', 'tools/atlases/atlscnv.py', 'assemble']
	args += ['--subtexture-path', src_basepath, '--atlas-path', dst_basepath]
	args += ext_args if ext_args is not None else []
	args += [dst_basename, ] + src_wildcards
	args = map(os.path.expandvars, args)
	atlscnv_process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout_data, stderr_data = atlscnv_process.communicate()
	if atlscnv_process.poll():
		# Output assembler return.
		print '[atlscnv stdout] >>>'
		print stdout_data
		print '--------------------'
		print stderr_data
		print '<<< [atlscnv stderr]'
		raise RuntimeError('An error occured while assembling atlas.')
	return

def compile_zipfile_string(src_data_blocks, dst_bin_comment='', compress=False):
	def get_parent_dirs(path):
		def get_parent_dirs_inv(path):
			while path:
				path = os.path.dirname(path)
				yield path + '/'
			return
		return reversed(tuple(get_parent_dirs_inv(path))[:-1])
	with io.BytesIO() as dst_bin_buffer:
		with zipfile.ZipFile(dst_bin_buffer, 'w', zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED) as dst_zip_buffer:
			for src_block_name, src_block_data in sorted(src_data_blocks, key=operator.itemgetter(0)):
				dst_zip_namelist = dst_zip_buffer.namelist()
				for src_block_parent_dir in get_parent_dirs(src_block_name):
					if src_block_parent_dir not in dst_zip_namelist:
						dst_zip_buffer.writestr(src_block_parent_dir, b'')
				dst_zip_buffer.writestr(src_block_name, src_block_data)
			dst_zip_buffer.comment = dst_bin_comment
		dst_bin_data = dst_bin_buffer.getvalue()
	return dst_bin_data

def acquire_version_data():
	if os.name == 'posix':
		git = 'git'
	elif os.name == 'nt':
		git = 'tools/git-scm/bin/git.exe'
	else:
		raise RuntimeError('Current operation system is not supported.')
	args = [git, 'describe', '--match=v*', '--dirty']
	git_process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	vcs_str_data = git_process.communicate()[0].strip()
	if git_process.poll():
		vcs_str_data = 'custom-build'
	return vcs_str_data

def merge_dicts(base, *args, **kwargs):
	result = base.copy()
	map(result.update, args)
	result.update(**kwargs)
	return result

def format_macros(string, macros):
	for macro, replace in macros.viewitems():
		string = string.replace(macro, replace)
	return string

def join_path(*args, **kwargs):
	path = os.path.normpath(os.path.join(*args, **kwargs)).replace(os.sep, '/')
	return path + ('/' if os.path.isdir(path) else '')

def norm_path(path):
	path = os.path.normpath(path).replace(os.sep, '/')
	return path + ('/' if os.path.isdir(path) else '')

def get_path_group_iterator(path_group, home='./'):
	# Resolves path group. If path group is a folder, returns list of files inside, or dot otherwise.
	_path = join_path(home, path_group)
	if os.path.isfile(_path):
		yield norm_path('./')
	elif os.path.isdir(_path):
		for root, dirs, files in os.walk(_path):
			root = os.path.relpath(root, _path)
			for file in files:
				yield join_path(root, file)
	return

def get_path_groups_iterator(path_groups, home='./'):
	# Resolves a list of path groups.
	for path_group in path_groups:
		for path in get_path_group_iterator(path_group, home):
			yield join_path(path_group, path)
	return

def get_path_group_block_iterator(path_group_block, home='./'):
	# Resolves first path group, others used as path prefixes.
	for path in get_path_group_iterator(path_group_block[0], home):
		yield [join_path(base, path) for base in path_group_block]
	return

def get_path_group_blocks_iterator(path_group_blocks, home='./'):
	# Resolves a list of path group blocks.
	for path_group_block in path_group_blocks:
		for path_block in get_path_group_block_iterator(path_group_block, home):
			yield path_block
	return

def load_file_data(src_filename):
	with open(src_filename, 'rb') as src_bin_buffer:
		dst_bin_data = src_bin_buffer.read()
	return dst_bin_data

def load_file_str(src_filename, encoding='acsii'):
	return unicode(load_file_data(src_filename), encoding=encoding)

def save_file_data(dst_filename, src_bin_data):
	if not os.path.isdir(os.path.dirname(dst_filename)):
		os.makedirs(os.path.dirname(dst_filename))
	with open(dst_filename, 'wb') as dst_bin_buffer:
		dst_bin_buffer.write(src_bin_data)
	return

def save_file_str(dst_filename, src_str_data, encoding='acsii'):
	save_file_data(dst_filename, src_str_data.encode(encoding=encoding))
	return

def load_source_string(src_filenames, source_encoding='acsii'):
	return u'\n'.join([load_file_str(src_filename, encoding=source_encoding) for src_filename in get_path_groups_iterator(src_filenames)])

if __name__ == '__main__':
	try:
		## Reading configuration.
		cfg_filename = join_path(os.path.splitext(__file__)[0] + '.cfg')
		with open(cfg_filename, 'rb') as cfg_bin_buffer:
			g_config = json.loads(cfg_bin_buffer.read())
		## Printing status.
		print 'Build config file loaded.'
		## Getting build version.
		g_version = acquire_version_data()
		## Printing status.
		print 'Acquired version for build: {}.'.format(g_version)
		## Loading macros.
		g_globalMacros = {macro: format_macros(replace, {'<<version>>': g_version}) for macro, replace in g_config["globalMacros"].viewitems()}
		g_pathsMacros = {macro: format_macros(replace, g_globalMacros) for macro, replace in g_config["pathsMacros"].viewitems()}
		g_metaMacros = {macro.replace('<<', '{{').replace('>>', '}}'): replace for macro, replace in g_globalMacros.viewitems()}
		g_allMacros = merge_dicts(g_globalMacros, g_pathsMacros)
		## Cleanup previous build.
		for cleanup in g_config["cleanup"]:
			cleanup = norm_path(format_macros(cleanup, g_allMacros))
			# Printing status.
			print 'Cleaning build path: {}.'.format(cleanup)
			# Removing all content.
			if os.path.isdir(cleanup):
				shutil.rmtree(cleanup)
			# Creating new folder.
			os.makedirs(cleanup)
		## Build commands.
		# FlashDevelop project build command.
		def g_actionscriptBuildProject(src_entry, level=0):
			# Parsing ActionScript entry.
			prj_filename, asm_filename, bin_filename, zip_filename = src_entry
			# Formatting macros.
			prj_filename = norm_path(format_macros(prj_filename, g_allMacros))
			asm_filename = norm_path(format_macros(asm_filename, g_allMacros))
			bin_filename = norm_path(format_macros(bin_filename, g_allMacros))
			zip_filename = norm_path(format_macros(zip_filename, g_allMacros))
			# Printing status.
			indent = ' ' * level
			print indent + 'Building FlashDevelop file: {}.'.format(prj_filename)
			print indent + ' Build result file: {}.'.format(asm_filename)
			print indent + ' Target binary file: {}.'.format(bin_filename)
			print indent + ' Target package file: {}.'.format(zip_filename)
			# Compiling FlashDevelop project.
			compile_flash_project(prj_filename)
			# Loading binary file.
			dst_bin_data = load_file_data(asm_filename)
			# Saving binary file.
			save_file_data(bin_filename, dst_bin_data)
			# Returning archive blocks.
			return [[zip_filename, dst_bin_data]]
		# Python source module build command.
		def g_pythonBuildSourceModule(src_entry, src_encoding, level=0):
			# Formatting macros.
			src_entry = [norm_path(format_macros(path, g_allMacros)) for path in src_entry]
			# Getting base path.
			mod_filename = src_entry[0]
			# Creating archive data blocks storage.
			archive_blocks = list()
			# Processing source entries.
			for src_entry in get_path_group_block_iterator(src_entry):
				# Parsing localization entry.
				src_filename, bin_filename, zip_filename = src_entry
				# Formatting macros.
				src_filename = norm_path(format_macros(src_filename, g_allMacros))
				bin_filename = norm_path(format_macros(bin_filename, g_allMacros))
				zip_filename = norm_path(format_macros(zip_filename, g_allMacros))
				# Changing binaries extension.
				bin_filename = os.path.splitext(bin_filename)[0] + '.pyc'
				zip_filename = os.path.splitext(zip_filename)[0] + '.pyc'
				# Printing status.
				indent = ' ' * level
				print indent + 'Building module file: {}.'.format(src_filename)
				print indent + ' Target binary file: {}.'.format(bin_filename)
				print indent + ' Target package file: {}.'.format(zip_filename)
				# Loading source block.
				src_str_data = format_macros(load_file_str(src_filename, src_encoding), g_globalMacros)
				# Getting parameters for compiler.
				cmp_filename = join_path(os.path.basename(mod_filename), os.path.relpath(src_filename, mod_filename))
				cmp_filetime = time.time()
				# Compiling source block.
				dst_bin_data = compile_python_string(src_str_data, cmp_filename, cmp_filetime)
				# Saving binary file.
				save_file_data(bin_filename, dst_bin_data)
				# Appending archive block.
				archive_blocks.append([zip_filename, dst_bin_data])
			return archive_blocks
		# Python source group build command.
		def g_pythonBuildSourceGroup(src_entry, src_encoding, level=0):
			# Parsing source group.
			cmp_filename, src_filenames, asm_filename, bin_filename, zip_filename = src_entry
			# Formatting macros.
			cmp_filename = norm_path(format_macros(cmp_filename, g_allMacros))
			src_filenames = [norm_path(format_macros(src_filename, g_allMacros)) for src_filename in src_filenames]
			asm_filename = norm_path(format_macros(asm_filename, g_allMacros))
			bin_filename = norm_path(format_macros(bin_filename, g_allMacros))
			zip_filename = norm_path(format_macros(zip_filename, g_allMacros))
			# Printing status.
			indent = ' ' * level
			print indent + 'Building source group to single file: {}.'.format(cmp_filename)
			for src_filename in get_path_groups_iterator(src_filenames):
				print indent + '  Chunk file: {}.'.format(src_filename)
			print indent + ' Target source file: {}.'.format(asm_filename)
			print indent + ' Target binary file: {}.'.format(bin_filename)
			print indent + ' Target package file: {}.'.format(zip_filename)
			# Loading source as single block.
			src_str_data = format_macros(load_source_string(src_filenames, src_encoding), g_globalMacros)
			# Saving assembled file.
			save_file_str(asm_filename, src_str_data, src_encoding)
			# Getting parameters for compiler.
			cmp_filetime = os.path.getmtime(asm_filename)
			# Compiling source block.
			dst_bin_data = compile_python_string(src_str_data, cmp_filename, cmp_filetime)
			# Saving binary file.
			save_file_data(bin_filename, dst_bin_data)
			# Returning archive blocks.
			return [[zip_filename, dst_bin_data]]
		# Resource build command.
		def g_resourceBuildEntry(src_entry, level=0):
			# Formatting macros.
			src_entry = [norm_path(format_macros(path, g_allMacros)) for path in src_entry]
			# Creating archive data blocks storage.
			archive_blocks = list()
			# Processing source entries.
			for src_entry in get_path_group_block_iterator(src_entry):
				# Parsing resource entry.
				bin_filename, zip_filename = src_entry
				# Formatting macros.
				bin_filename = norm_path(format_macros(bin_filename, g_allMacros))
				zip_filename = norm_path(format_macros(zip_filename, g_allMacros))
				# Printing status.
				indent = ' ' * level
				print indent + 'Building resource file: {}.'.format(bin_filename)
				print indent + ' Target package file: {}.'.format(zip_filename)
				# Loading binary file.
				dst_bin_data = load_file_data(bin_filename)
				# Appending archive block.
				archive_blocks.append([zip_filename, dst_bin_data])
			return archive_blocks
		# Localization build command.
		def g_localizationBuildEntry(src_entry, level=0):
			# Formatting macros.
			src_entry = [norm_path(format_macros(path, g_allMacros)) for path in src_entry]
			# Creating archive data blocks storage.
			archive_blocks = list()
			# Processing source entries.
			for src_entry in get_path_group_block_iterator(src_entry):
				# Parsing localization entry.
				src_filename, bin_filename, zip_filename = src_entry
				# Formatting macros.
				src_filename = norm_path(format_macros(src_filename, g_allMacros))
				bin_filename = norm_path(format_macros(bin_filename, g_allMacros))
				zip_filename = norm_path(format_macros(zip_filename, g_allMacros))
				# Printing status.
				indent = ' ' * level
				print indent + 'Building localization file: {}.'.format(src_filename)
				print indent + ' Target binary file: {}.'.format(bin_filename)
				print indent + ' Target package file: {}.'.format(zip_filename)
				# Loading portable object file.
				src_bin_data = load_file_data(src_filename)
				# Compiling portable object file.
				dst_bin_data = compile_gettext_string(src_bin_data)
				# Saving binary file.
				save_file_data(bin_filename, dst_bin_data)
				# Appending archive block.
				archive_blocks.append([zip_filename, dst_bin_data])
			return archive_blocks
		# Atlas build command.
		def g_atlasBuildEntry(src_entry, level=0):
			# Parsing atlas entry.
			dst_atlas, src_wildcards, src_basepath, ext_args, atl_entries = src_entry
			# Formatting macros.
			dst_atlas = norm_path(format_macros(dst_atlas, g_allMacros))
			src_wildcards = [norm_path(format_macros(src_wildcard, g_allMacros)) for src_wildcard in src_wildcards]
			src_basepath = norm_path(format_macros(src_basepath, g_allMacros))
			ext_args = [format_macros(ext_arg, g_allMacros) for ext_arg in ext_args]
			# Printing status.
			indent = ' ' * level
			print indent + 'Building atlas: {}.'.format(dst_atlas)
			# Assembling atlas.
			compile_atlas(dst_atlas, src_wildcards, src_basepath, ext_args)
			# Returning archive blocks.
			return list(itertools.chain.from_iterable(g_resourceBuildEntry(atl_entry, level + 1) for atl_entry in atl_entries))
		# Package metadata build command.
		def g_packageMetadataBuildEntry(src_entry, level=0):
			# Formatting macros.
			src_entry = [norm_path(format_macros(path, g_allMacros)) for path in src_entry]
			# Creating archive data blocks storage.
			archive_blocks = list()
			# Processing source entries.
			for src_entry in get_path_group_block_iterator(src_entry):
				# Parsing metadata entry.
				src_filename, zip_filename, src_encoding = src_entry
				# Formatting macros.
				src_filename = norm_path(format_macros(src_filename, g_allMacros))
				zip_filename = norm_path(format_macros(zip_filename, g_allMacros))
				# Printing status.
				indent = ' ' * level
				print indent + 'Building metadata file: {}.'.format(src_filename)
				print indent + ' Target package file: {}.'.format(zip_filename)
				# Loading meta file.
				dst_str_data = load_file_str(src_filename, src_encoding)
				# Formatting macros in meta data.
				dst_bin_data = format_macros(dst_str_data, g_metaMacros).encode(encoding=src_encoding)
				# Appending archive block.
				archive_blocks.append([zip_filename, dst_bin_data])
			return archive_blocks
		# Package build command.
		def g_packageBuildEntry(src_entry, level=0):
			# Parsing package entry.
			entry_parser = operator.itemgetter('name', 'build', 'release', 'metadata', 'actionscript', 'python', 'resources', 'localizations', 'atlases')
			pkg_name, pkg_build, pkg_release, pkg_metadata, pkg_actionscript, pkg_python, pkg_resources, pkg_localizations, pkg_atlases = entry_parser(src_entry)
			# Formatting macros.
			pkg_name = norm_path(format_macros(pkg_name, g_allMacros))
			pkg_build = norm_path(format_macros(pkg_build, g_allMacros))
			pkg_release = norm_path(format_macros(pkg_release, g_allMacros))
			# Printing status.
			indent = ' ' * level
			print indent + 'Building package: {}.'.format(pkg_name)
			print indent + ' Target binary file: {}.'.format(pkg_build)
			print indent + ' Target package file: {}.'.format(pkg_release)
			# Creating package data blocks storage.
			package_blocks = list()
			#>> Building package ActionScript.
			print indent + ' >> Building package ActionScript... <<'
			# Detecting flex.
			detect_flex()
			# Building projects.
			package_blocks.extend(itertools.chain.from_iterable(
				[g_actionscriptBuildProject(src_entry, level + 2) for src_entry in pkg_actionscript]
			))
			#>> Building package Python.
			print indent + ' >> Building package Python... <<'
			#> Loading Python source encoding.
			python_encoding = pkg_python["encoding"]
			#> Building package Python modules.
			print indent + '  > Building package Python modules... <'
			# Building modules.
			package_blocks.extend(itertools.chain.from_iterable(
				[g_pythonBuildSourceModule(src_entry, python_encoding, level + 3) for src_entry in pkg_python["modules"]]
			))
			#> Building package Python sources.
			print indent + '  > Building package Python sources... <'
			# Building sources.
			package_blocks.extend(itertools.chain.from_iterable(
				[g_pythonBuildSourceGroup(src_entry, python_encoding, level + 3) for src_entry in pkg_python["sources"]]
			))
			#>> Building package resources.
			print indent + ' >> Building package resources... <<'
			# Building resources.
			package_blocks.extend(itertools.chain.from_iterable(
				[g_resourceBuildEntry(src_entry, level + 2) for src_entry in pkg_resources]
			))
			#>> Building package localizations.
			print indent + ' >> Building package localizations... <<'
			# Building localizations.
			package_blocks.extend(itertools.chain.from_iterable(
				[g_localizationBuildEntry(src_entry, level + 2) for src_entry in pkg_localizations]
			))
			#>> Building package atlases.
			print indent + ' >> Building package atlases... <<'
			# Building atlases.
			package_blocks.extend(itertools.chain.from_iterable(
				[g_atlasBuildEntry(src_entry, level + 2) for src_entry in pkg_atlases]
			))
			#>> Building package metadata.
			print indent + ' >> Building package metadata... <<'
			# Building metadata.
			package_blocks.extend(itertools.chain.from_iterable(
				[g_packageMetadataBuildEntry(src_entry, level + 2) for src_entry in pkg_metadata]
			))
			#>> Assembling package.
			dst_bin_data = compile_zipfile_string(package_blocks, compress=False)
			#>> Saving binary file.
			save_file_data(pkg_build, dst_bin_data)
			# Returning archive blocks.
			return [[pkg_release, dst_bin_data]]
		## Creating release archive data blocks storage.
		g_releaseBlocks = list()
		## Building release archive packages.
		print '>>> Building packages... <<<'
		# Building packages.
		g_releaseBlocks.extend(itertools.chain.from_iterable(
			[g_packageBuildEntry(src_entry, level=1) for src_entry in g_config["releasePackages"]]
		))
		## Building release archive resources.
		print '>>> Building resources... <<<'
		g_releaseBlocks.extend(itertools.chain.from_iterable(
			[g_resourceBuildEntry(src_entry, level=1) for src_entry in g_config["releaseResources"]]
		))
		## Loading release archive filename.
		g_releaseArchive = norm_path(format_macros(g_config["releaseArchive"], g_allMacros))
		## Loading release archive comment.
		g_releaseComment = format_macros(g_config["releaseComment"], g_allMacros).encode('ascii')
		## Saving release archive file.
		print '>>> Saving archive... <<<'
		save_file_data(g_releaseArchive, compile_zipfile_string(g_releaseBlocks, g_releaseComment, compress=True))
		## Build finished.
		print '>>> Build finished. <<<'
	except:
		traceback.print_exc()
