import repr
import re
import json
import urllib


class JSONPointerException(Exception):
    pass


class InvalidJSONPointer(JSONPointerException):
    pass


class EndOfArrayInRead(JSONPointerException):
    pass


class PointerDecodeException(JSONPointerException):
    pass


class MissingPropertyOrIndex(JSONPointerException):

    def __init__(self, message, prop_or_index):
        super(MissingPropertyOrIndex, self).__init__(message)
        self.prop_or_index = prop_or_index


def unescape(part, UNESCAPER=re.compile(u'(~(.?))')):
    replacements = (u'~', u'/')

    def replace(m):
        try:
            idx = int(m.group(2))
        except ValueError:
            raise InvalidJSONPointer(u'~ not used as escape character: %s'
                                     % m.group(0))

        try:
            return replacements[idx]
        except IndexError:
            raise InvalidJSONPointer(u'~ used in invalid escape sequence: %s'
                                     % m.group(0))

    return UNESCAPER.sub(replace, part)


def _prepare_path(path):
    if not isinstance(path, unicode):
        try:
            path = json.loads(b'"%s"' % path)
        except ValueError:
            raise PointerDecodeException(u"Could not decode string path %s"
                                         % repr.repr(path))
    if path.startswith(u'#'):
        # TODO: does unquote have a problem with unicode objects??
        path = urllib.unquote(path[1:])

    return [unescape(part) for part in path.split(u'/')]


def numeric_accessor(thing, number):
    if isinstance(thing, list):
        return thing[int(number)]
    return thing[number]


def string_accessor(thing, name):
    return thing[name]


def read_traversal(path):
    parts = _prepare_path(path)
    traversal = []
    for idx, part in enumerate(parts):
        if part == '-':
            raise EndOfArrayInRead("Can't use '-' inside a read pointer"
                                   ' expression')
        elif not part:
            continue

        accessor = numeric_accessor if part.isdigit() else string_accessor

        def traverse(obj, func=accessor, property=part, idx=idx):
            try:
                return func(obj, property)
            except (KeyError, ValueError, TypeError):
                pointer = '/'.join(parts[:idx + 1])
                raise MissingPropertyOrIndex("Missing property or index %r"
                                             % pointer, pointer)
        traversal.append(traverse)
    return traversal


class JSONPointer(object):

    def __init__(self, path):
        self.path = path
        self.read_traversal = read_traversal(path)

    def get(self, obj):
        for component in self.read_traversal:
            obj = component(obj)
        return obj
