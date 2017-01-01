import io
import os
import imp
import json
import time
import shutil
import struct
import marshal
import zipfile
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

def compile_zipfile_string(src_data_blocks, src_bin_comment=''):
	with io.BytesIO() as dst_bin_buffer:
		with zipfile.ZipFile(dst_bin_buffer, 'w', zipfile.ZIP_DEFLATED) as dst_zip_buffer:
			for src_block_name, src_block_data in src_data_blocks:
				dst_zip_buffer.writestr(src_block_name, src_block_data)
			dst_zip_buffer.comment = src_bin_comment
		dst_bin_data = dst_bin_buffer.getvalue()
	return dst_bin_data

def acquire_version_data(vcs_filename):
	vcs_str_data = '<custom_build>'
	if os.path.isfile(vcs_filename):
		with open(vcs_filename, 'r+b') as vcs_bin_buffer:
			vcs_obj_data = json.load(vcs_bin_buffer)
			vcs_str_data = '{release}#{next_build}'.format(**vcs_obj_data)
			vcs_obj_data['next_build'] += 1
			vcs_bin_buffer.seek(0)
			vcs_bin_buffer.truncate()
			vcs_bin_buffer.write(json.dumps(vcs_obj_data) + '\n')
	return vcs_str_data

def merge_dicts(base, *args, **kwargs):
	result = base.copy()
	map(result.update, args)
	result.update(**kwargs)
	return result

def format_macros(string, macros):
	for macro, replace in macros.items():
		string = string.replace(macro, replace)
	return string

def join_path(*args, **kwargs):
	path = os.path.normpath(os.path.join(*args, **kwargs)).replace(os.sep, '/')
	return path + ('/' if os.path.isdir(path) else '')

def norm_path(path):
	path = os.path.normpath(path).replace(os.sep, '/')
	return path + ('/' if os.path.isdir(path) else '')

def get_path_group_iterator(path_group, home='./'):
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
	for path_group in path_groups:
		for path in get_path_group_iterator(path_group, home):
			yield join_path(path_group, path)
	return

def get_path_group_block_iterator(path_group_block, home='./'):
	for path in get_path_group_iterator(path_group_block[0], home):
		yield [join_path(base, path) for base in path_group_block]
	return

def get_path_group_blocks_iterator(path_group_blocks, home='./'):
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
		## Reading build version.
		vcs_filename = join_path(os.path.dirname(__file__), 'version.cfg')
		g_version = acquire_version_data(vcs_filename)
		## Printing status.
		print 'Acquired new version for build: {}.'.format(g_version)
		## Loading macros.
		g_globalMacros = {macro: format_macros(replace, {'<version>': g_version}) for macro, replace in g_config["globalMacros"].items()}
		g_pathsMacros = {macro: format_macros(replace, g_globalMacros) for macro, replace in g_config["pathsMacros"].items()}
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
		## ActionScript build commands.
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
			print indent + ' Assembled binary file: {}.'.format(asm_filename)
			print indent + ' Resulting binary file: {}.'.format(bin_filename)
			print indent + ' Target zip archive file: {}.'.format(zip_filename)
			# Compiling FlashDevelop project.
			compile_flash_project(prj_filename)
			# Loading binary file.
			dst_bin_data = load_file_data(asm_filename)
			# Saving binary file.
			save_file_data(bin_filename, dst_bin_data)
			# Returning archive blocks.
			return [[zip_filename, dst_bin_data]]
		## Python build commands.
		# Loading source encoding.
		g_pythonSourceEncoding = g_config["python"]["sourceEncoding"]
		# Source module build command.
		def g_pythonBuildSourceModule(src_entry, level=0):
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
				print indent + ' Target zip archive file: {}.'.format(zip_filename)
				# Loading source block.
				src_str_data = format_macros(load_file_str(src_filename, g_pythonSourceEncoding), g_globalMacros)
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
		# Source group build command.
		def g_pythonBuildSourceGroup(src_entry, src_plugins=None, level=0):
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
				print indent + ' Source file: {}.'.format(src_filename)
			print indent + ' Target assembled file: {}.'.format(asm_filename)
			print indent + ' Target binary file: {}.'.format(bin_filename)
			print indent + ' Target zip archive file: {}.'.format(zip_filename)
			print indent + ' Building binaries {} plug-ins.'.format('with' if src_plugins is not None else 'without')
			# Loading source as single block.
			src_str_data = format_macros(load_source_string(src_filenames, g_pythonSourceEncoding), g_globalMacros)
			# Saving assembled file.
			save_file_str(asm_filename, src_str_data, g_pythonSourceEncoding)
			# Getting parameters for compiler.
			cmp_filetime = os.path.getmtime(asm_filename)
			# Compiling source block.
			dst_bin_data = compile_python_string(src_str_data, cmp_filename, cmp_filetime)
			# Attaching plug-in.
			if src_plugins is not None and cmp_filename in src_plugins:
				dst_bin_data += src_plugins[cmp_filename]
			# Saving binary file.
			save_file_data(bin_filename, dst_bin_data)
			# Returning archive blocks.
			return [[zip_filename, dst_bin_data]]
		# Plug-in build command.
		def g_pythonBuildPluginAttachGroup(att_entry, level=0):
			# Parsing resource entry.
			att_filename, att_comment, src_entries = att_entry
			# Formatting macros.
			att_filename = norm_path(format_macros(att_filename, g_allMacros))
			att_comment = format_macros(att_comment, g_allMacros).encode('ascii')
			# Printing status.
			indent = ' ' * level
			print indent + 'Building plug-in attach group: {}.'.format(att_filename)
			# Building zip archive attachment.
			dst_bin_data = compile_zipfile_string(itertools.chain.from_iterable(
				[g_pythonBuildSourceGroup(src_entry, level=level + 1) for src_entry in src_entries]
			), att_comment)
			return att_filename, dst_bin_data
		## Resource build commands.
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
				print indent + ' Target zip archive file: {}.'.format(zip_filename)
				# Loading binary file.
				dst_bin_data = load_file_data(bin_filename)
				# Appending archive block.
				archive_blocks.append([zip_filename, dst_bin_data])
			return archive_blocks
		## Localization build commands.
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
				print indent + ' Target zip archive file: {}.'.format(zip_filename)
				# Loading portable object file.
				src_bin_data = load_file_data(src_filename)
				# Compiling portable object file.
				dst_bin_data = compile_gettext_string(src_bin_data)
				# Saving binary file.
				save_file_data(bin_filename, dst_bin_data)
				# Appending archive block.
				archive_blocks.append([zip_filename, dst_bin_data])
			return archive_blocks
		## Atlas build commands.
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
			return list(itertools.chain.from_iterable(g_resourceBuildEntry(atl_entry, level) for atl_entry in atl_entries))
		## Creating release archive data blocks storage.
		g_releaseBlocks = list()
		## Building ActionScript.
		print '>>> Building ActionScript... <<<'
		# Detecting flex.
		detect_flex()
		# Building projects.
		g_releaseBlocks.extend(itertools.chain.from_iterable(
			[g_actionscriptBuildProject(src_entry, level=1) for src_entry in g_config["actionscript"]]
		))
		## Building Python.
		print '>>> Building Python... <<<'
		# Printing status.
		print 'Modules build started.'
		# Building modules.
		g_releaseBlocks.extend(itertools.chain.from_iterable(
			[g_pythonBuildSourceModule(src_entry, level=1) for src_entry in g_config["python"]["modules"]]
		))
		# Printing status.
		print 'Plug-ins build started.'
		# Building plug-ins.
		g_pythonSourcePlugins = dict(g_pythonBuildPluginAttachGroup(att_entry, level=1) for att_entry in g_config["python"]["plugins"])
		# Printing status.
		print 'Source build started.'
		# Building and adding sources.
		g_releaseBlocks.extend(itertools.chain.from_iterable(
			[g_pythonBuildSourceGroup(src_entry, g_pythonSourcePlugins, level=1) for src_entry in g_config["python"]["sources"]]
		))
		## Building Resource.
		print '>>> Building Resource... <<<'
		# Printing status.
		print 'Resource build started.'
		# Adding resources.
		g_releaseBlocks.extend(itertools.chain.from_iterable(
			[g_resourceBuildEntry(src_entry, level=1) for src_entry in g_config["resources"]]
		))
		## Building Localization.
		print '>>> Building Localization... <<<'
		# Printing status.
		print 'Localization build started.'
		# Compiling and adding localization.
		g_releaseBlocks.extend(itertools.chain.from_iterable(
			[g_localizationBuildEntry(src_entry, level=1) for src_entry in g_config["localizations"]]
		))
		## Building Atlas.
		print '>>> Building Atlas... <<<'
		# Printing status.
		print 'Atlas build started.'
		# Assembling and adding atlases.
		g_releaseBlocks.extend(itertools.chain.from_iterable(
			[g_atlasBuildEntry(src_entry, level=1) for src_entry in g_config["atlases"]]
		))
		## Loading release archive filename.
		g_releaseArchive = format_macros(g_config["releaseArchive"], g_allMacros)
		## Loading release archive comment.
		g_releaseComment = format_macros(g_config["releaseComment"], g_allMacros).encode('ascii')
		## Printing status.
		print 'Saving release archive.'
		## Saving release archive file.
		save_file_data(g_releaseArchive, compile_zipfile_string(g_releaseBlocks, g_releaseComment))
		## Build finished.
		print 'Build finished.'
	except:
		traceback.print_exc()
