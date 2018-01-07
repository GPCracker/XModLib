# Authors: Vladislav Ignatenko <gpcracker@mail.ru>

# ------------ #
#    Python    #
# ------------ #
import io
import re
import copy
import errno
import gettext
import operator
import itertools
import collections

# -------------- #
#    BigWorld    #
# -------------- #
# nothing

# ---------------- #
#    WoT Client    #
# ---------------- #
# nothing

# ------------------- #
#    X-Mod Library    #
# ------------------- #
from . import EngineUtils

# -------------------- #
#    Module Content    #
# -------------------- #
def getDefaultTranslatorsCache():
	return globals().setdefault('_defaultTranslatorsCache', TranslatorsCache())

def getDefaultTranslationFormatter():
	return globals().setdefault('_defaultTranslationFormatter', TranslationFormatter())

class TranslationFile(io.BytesIO):
	__slots__ = ('_filename', )

	name = property(lambda self: self._filename)

	def __init__(self, content=b'', filename='<string>'):
		super(TranslationFile, self).__init__(content)
		if not isinstance(filename, basestring):
			raise TypeError('filename argument must be string, not {!s}'.format(type(filename).__name__))
		self._filename = filename
		return

class TranslatorsCache(dict):
	__slots__ = ()

	@staticmethod
	def _translator(domain):
		filename = EngineUtils.joinResMgrPath('text/lc_messages', domain + '.mo')
		content = EngineUtils.getResMgrBinaryFileContent(filename)
		if content is None:
			raise IOError(errno.ENOENT, 'no translation file found for domain', domain)
		with TranslationFile(content, filename) as fakefile:
			translation = gettext.GNUTranslations(fakefile)
		return translation

	def __missing__(self, domain):
		if not isinstance(domain, basestring):
			raise TypeError('domain argument must be string, not {!s}'.format(type(domain).__name__))
		return self.setdefault(domain, self._translator(domain))

	def gettext(self, domain, message):
		return self[domain].gettext(message)

	def __repr__(self):
		return '{!s}({!s})'.format(self.__class__.__name__, dict.__repr__(self))

class TranslationFormatter(collections.namedtuple('TranslationFormatter', ('cache', 'regex'))):
	__slots__ = ()

	def __new__(cls, cache=None, header='#', trailer=';', delimiter=':'):
		if cache is None:
			cache = getDefaultTranslatorsCache()
		if not isinstance(cache, TranslatorsCache):
			raise TypeError('cache argument must be TranslatorsCache, not {!s}'.format(type(cache).__name__))
		if not isinstance(header, basestring) or len(header) != 1 or re.match(r'^[\\\w\s/]$', header):
			raise TypeError('header argument must be non-word char, not {!s}'.format(type(header).__name__))
		if not isinstance(trailer, basestring) or len(trailer) != 1 or re.match(r'^[\\\w\s/]$', trailer):
			raise TypeError('trailer argument must be non-word char, not {!s}'.format(type(trailer).__name__))
		if not isinstance(delimiter, basestring) or len(delimiter) != 1 or re.match(r'^[\\\w\s/]$', delimiter):
			raise TypeError('delimiter argument must be non-word char, not {!s}'.format(type(delimiter).__name__))
		header, trailer, delimiter, separator = itertools.imap(re.escape, (header, trailer, delimiter, '/'))
		regex = re.compile(r'{h}(\w+?){d}(\w+?(?:{s}\w+?)*?){t}'.format(h=header, t=trailer, d=delimiter, s=separator))
		return super(TranslationFormatter, cls).__new__(cls, cache, regex)

	def __call__(self, template):
		def replacement(match):
			domain, message = match.groups()
			text = self.cache.gettext(domain, message)
			return text if text != message else match.group()
		return self.regex.sub(replacement, template)

	def __repr__(self):
		return '<{!s} [cache={!r}, regex={!r}]>'.format(object.__repr__(self).strip('<>'), self.cache, self.regex)

def getStandardMacrosFormatter(*args, **kwargs):
	return StandardMacrosFormattersCollection(default=StringMacrosFormatter(*args, **kwargs))

def getExtendedMacrosFormatter(*args, **kwargs):
	return ExtendedMacrosFormattersCollection(default=StringMacrosFormatter(*args, **kwargs))

class UnicodeUnescapeMacrosFormatter(object):
	__slots__ = ()

	def __call__(self, formatspec):
		return formatspec.decode('unicode-escape')

class StringMacrosFormatter(collections.namedtuple('StringMacrosFormatter', ('args', 'kwargs'))):
	__slots__ = ()

	def __new__(cls, *args, **kwargs):
		return super(StringMacrosFormatter, cls).__new__(cls, args, kwargs)

	def __call__(self, formatspec):
		try:
			return ('{' + formatspec + '}').format(*self.args, **self.kwargs)
		except (IndexError, KeyError, ValueError):
			return '{?' + formatspec + '?}'
		return

class TranslationMacrosFormatter(collections.namedtuple('TranslationMacrosFormatter', ('cache', 'regex'))):
	__slots__ = ()

	def __new__(cls, cache=None, delimiter=':'):
		if cache is None:
			cache = getDefaultTranslatorsCache()
		if not isinstance(cache, TranslatorsCache):
			raise TypeError('cache argument must be TranslatorsCache, not {!s}'.format(type(cache).__name__))
		if not isinstance(delimiter, basestring) or len(delimiter) != 1 or re.match(r'^[\\\w\s/]$', delimiter):
			raise TypeError('delimiter argument must be non-word char, not {!s}'.format(type(delimiter).__name__))
		delimiter, separator = itertools.imap(re.escape, (delimiter, '/'))
		regex = re.compile(r'^(\w+?){d}(\w+?(?:{s}\w+?)*?)$'.format(d=delimiter, s=separator))
		return super(TranslationMacrosFormatter, cls).__new__(cls, cache, regex)

	def __call__(self, formatspec):
		match = self.regex.match(formatspec)
		if not match:
			raise ValueError('translation macro does not match specification')
		domain, message = match.groups()
		text = self.cache.gettext(domain, message)
		return text if text != message else 'translation({!s})'.format(formatspec)

	def __repr__(self):
		return '<{!s} [cache={!r}, regex={!r}]>'.format(object.__repr__(self).strip('<>'), self.cache, self.regex)

class ConditionMacrosFormatter(collections.namedtuple('ConditionMacrosFormatter', ('istrue', 'regex', 'escapechars'))):
	__slots__ = ()

	def __new__(cls, istrue=None, delimiter=':', separator=':'):
		if istrue is None:
			def istrue(condition):
				condition = condition.lower()
				return condition in ('true', 'yes', 'y') or condition not in ('false', 'no', 'n') and None
		if not callable(istrue):
			raise TypeError('istrue argument must be callable, not {!s}'.format(type(istrue).__name__))
		if not isinstance(delimiter, basestring) or len(delimiter) != 1 or re.match(r'^[\\\w\s]$', delimiter):
			raise TypeError('delimiter argument must be non-word char, not {!s}'.format(type(delimiter).__name__))
		if not isinstance(separator, basestring) or len(separator) != 1 or re.match(r'^[\\\w\s]$', separator):
			raise TypeError('separator argument must be non-word char, not {!s}'.format(type(separator).__name__))
		escapechars = ''.join({delimiter, separator})
		delimiter, separator = itertools.imap(re.escape, (delimiter, separator))
		regex = re.compile(r'^([^{d}{s}]*?){d}([^{d}{s}]*?){s}([^{d}{s}]*?)$'.format(d=delimiter, s=separator))
		return super(ConditionMacrosFormatter, cls).__new__(cls, istrue, regex, escapechars)

	def __call__(self, formatspec):
		match = self.regex.match(formatspec)
		if not match:
			raise ValueError('condition macro does not match specification')
		condition, ifclause, elseclause = itertools.imap(operator.methodcaller('decode', 'unicode-escape'), match.groups())
		return ifclause if self.istrue(condition) else elseclause

	def __repr__(self):
		return '<{!s} [istrue={!r}, regex={!r}]>'.format(object.__repr__(self).strip('<>'), self.istrue, self.regex)

class StandardMacrosFormattersCollection(dict):
	__slots__ = ('__weakref__', '_aliases')

	def __init__(self, *args, **kwargs):
		super(StandardMacrosFormattersCollection, self).__init__(*args, **kwargs)
		self.setdefault('unescape', UnicodeUnescapeMacrosFormatter())
		self.setdefault('default', StringMacrosFormatter())
		self.aliases.setdefault('format', 'default')
		return

	@property
	def aliases(self):
		if not hasattr(self, '_aliases'):
			setattr(self, '_aliases', dict())
		return self._aliases

	def copy(self):
		return copy.copy(self)

	def escapechars(self, macrotype):
		return getattr(self[macrotype], 'escapechars', '')

	def setnewargs(self, *args, **kwargs):
		self.update(default=StringMacrosFormatter(*args, **kwargs))
		return

	def __missing__(self, macrotype):
		alias = self.aliases[macrotype]
		if alias == macrotype:
			raise KeyError(macrotype)
		return self[alias]

	def __call__(self, macrotype, formatspec):
		return self[macrotype](formatspec)

	def __repr__(self):
		return '{!s}({!s})'.format(self.__class__.__name__, dict.__repr__(self))

class ExtendedMacrosFormattersCollection(StandardMacrosFormattersCollection):
	__slots__ = ()

	def __init__(self, *args, **kwargs):
		super(ExtendedMacrosFormattersCollection, self).__init__(*args, **kwargs)
		self.setdefault('translation', TranslationMacrosFormatter())
		self.setdefault('condition', ConditionMacrosFormatter())
		self.aliases.setdefault('gettext', 'translation')
		self.aliases.setdefault('if', 'condition')
		return

class _MacrosFormatterSubTemplate(tuple):
	__slots__ = ()

	def __new__(cls, iterable):
		subtemplate = super(_MacrosFormatterSubTemplate, cls).__new__(cls, iterable)
		return ''.join(subtemplate) if all(isinstance(chunk, basestring) for chunk in subtemplate) else subtemplate

	def __call__(self, formatter):
		def iterchunks(subtemplate):
			for chunk in subtemplate:
				if isinstance(chunk, basestring):
					yield chunk
					continue
				macrotype, formatspec, escapechars = chunk
				if not isinstance(formatspec, basestring):
					formatspec = formatspec(formatter)
				formatted = formatter(macrotype, formatspec)
				if escapechars:
					escaperegex = re.compile('[' + re.escape(escapechars) + ']')
					replacement = lambda match: r'\x{:02x}'.format(ord(match.group()))
					formatted = escaperegex.sub(replacement, formatted.encode('unicode-escape'))
				yield formatted
			return
		return ''.join(iterchunks(self))

	def __repr__(self):
		return '{!s}({!s})'.format(self.__class__.__name__, tuple.__repr__(self))

class MacrosFormatterTemplate(_MacrosFormatterSubTemplate):
	__slots__ = ()

	def __new__(cls, template, escapes=lambda macrotype: '', header='{', trailer='}', delimiter='|'):
		if not isinstance(template, basestring):
			raise TypeError('template argument must be string, not {!s}'.format(type(template).__name__))
		if not callable(escapes):
			raise TypeError('escapes argument must be callable, not {!s}'.format(type(escapes).__name__))
		if not isinstance(header, basestring) or len(header) != 1 or re.match(r'^[\\\w\s]$', header):
			raise TypeError('header argument must be non-word char, not {!s}'.format(type(header).__name__))
		if not isinstance(trailer, basestring) or len(trailer) != 1 or re.match(r'^[\\\w\s]$', trailer):
			raise TypeError('trailer argument must be non-word char, not {!s}'.format(type(trailer).__name__))
		if not isinstance(delimiter, basestring) or len(delimiter) != 1 or re.match(r'^[\\\w\s]$', delimiter):
			raise TypeError('delimiter argument must be non-word char, not {!s}'.format(type(delimiter).__name__))
		def searchfirst(template, regexes, *searchspan):
			matches = tuple(itertools.ifilter(None, itertools.imap(operator.methodcaller('search', template, *searchspan), regexes)))
			return min(matches, key=operator.methodcaller('start')) if matches else None
		header, trailer, delimiter = itertools.imap(re.escape, (header, trailer, delimiter))
		nestedstartbrace = re.compile(r'{h}'.format(h=header, t=trailer, d=delimiter))
		nestedstopbrace = re.compile(r'{t}'.format(h=header, t=trailer, d=delimiter))
		doublebrace = re.compile(r'({h}|{t})\1'.format(h=header, t=trailer, d=delimiter))
		startbrace = re.compile(r'{h}(?!{h})'.format(h=header, t=trailer, d=delimiter))
		stopbrace = re.compile(r'{t}(?!{t})'.format(h=header, t=trailer, d=delimiter))
		outersearch, innersearch = (doublebrace, startbrace, stopbrace), (nestedstartbrace, nestedstopbrace)
		extmacro = re.compile(r'^(?:(\w+?){d})?(.*?)$'.format(h=header, t=trailer, d=delimiter))
		def iterchunks(template, escapechars='', nested=0):
			def iterrawchunks(template, searchstart=0):
				inside = 0
				while True:
					if inside:
						inmatch = searchfirst(template, innersearch, searchstart)
						if not inmatch:
							raise ValueError('single {!r} encountered in format string'.format(outmatch.group()))
						if inmatch.re == nestedstartbrace:
							inside += 1
						elif inmatch.re == nestedstopbrace:
							inside -= 1
						if not inside:
							extmatch = extmacro.match(template[outmatch.end():inmatch.start()])
							if not extmatch:
								raise ValueError('extended macro does not match specification')
							macrotype, formatspec = extmatch.groups('default')
							extchunks = iterchunks(formatspec, escapechars=escapes(macrotype), nested=(nested + 1))
							yield macrotype, _MacrosFormatterSubTemplate(extchunks), escapechars
						searchstart = inmatch.end()
						continue
					outmatch = searchfirst(template, innersearch if nested else outersearch, searchstart)
					if not outmatch:
						break
					yield template[searchstart:outmatch.start()]
					if outmatch.re == doublebrace:
						yield outmatch.group(1)
					elif outmatch.re in (startbrace, nestedstartbrace):
						inside += 1
					elif outmatch.re in (stopbrace, nestedstopbrace):
						raise ValueError('single {!r} encountered in format string'.format(outmatch.group()))
					searchstart = outmatch.end()
				yield template[searchstart:]
				return
			rawchunks = itertools.ifilter(None, iterrawchunks(template))
			for key, group in itertools.groupby(rawchunks, key=lambda chunk: isinstance(chunk, basestring)):
				if not key:
					for chunk in group:
						yield chunk
					continue
				yield ''.join(group)
			return
		return super(MacrosFormatterTemplate, cls).__new__(cls, iterchunks(template))

	def __call__(self, formatter=lambda macrotype, formatspec: formatspec):
		if not callable(formatter):
			raise TypeError('formatter argument must be callable, not {!s}'.format(type(formatter).__name__))
		return super(MacrosFormatterTemplate, self).__call__(formatter)

	def __repr__(self):
		return '<{!s} [chunks={!s}]>'.format(object.__repr__(self).strip('<>'), tuple.__repr__(self))
