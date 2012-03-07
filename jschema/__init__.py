try:
    import simplejson as json
except ImportError:
    import json

class InvalidSchema(Exception):
    """raised for invalid schemas"""

_DEFAULT = object()

class deserialize(object):

    def __init__(self, func):
        self.func = func

    def __call__(self, fromdict=None, fromstring=None, fromfile=None,
                *args, **kwargs):
        for source, loader in ((fromdict, lambda d: d),
                               (fromstring, json.loads),
                               (fromfile, json.load)):
            if source is not None:
                return self.func(loader(source), *args, **kwargs)
        return self.func({}, *args, **kwargs)

    def __get__(self, obj, type_=None):
        bound_func = self.func.__get__(obj, type_)
        return self.__class__(bound_func)


class JSONValidate(object):

    @deserialize
    def __init__(self, obj=None):
        self._schema = None
        self._establish_simple_constraints()
        self.schema = obj

    def _establish_simple_constraints(self):
        string_constraints = {_DEFAULT: lambda s: isinstance(s, basestring),
                              'minLength': lambda n: lambda s: len(s) >= n,
                              'maxLength': lambda n: lambda s: len(s) <= n}

        number_constraints = {_DEFAULT: (lambda n: isinstance(n, float)
                                         or isinstance(n, int)),
                              'minimum': lambda m: lambda n: n >= m,
                              'maximum': lambda m: lambda n: n <= m,
                              'exclusiveMinimum': lambda m: lambda n: n > m,
                              'exclusiveMaximum': lambda m: lambda n: n < m,
                              'divisibleBy': lambda m: lambda n: not n % m}

        integer_constraints = number_constraints.copy()
        integer_constraints[_DEFAULT] = lambda n: isinstance(n, int)

        boolean_constraints = {_DEFAULT: lambda n: isinstance(n, bool)}

        # XXX: this isn't simple
        object_constraints = {_DEFAULT: self.object_validator}

        array_constraints = {_DEFAULT: lambda a: isinstance(a, list),
                             # XXX: this isn't simple
                             'items': self.items_validator,
                             'minItems': lambda n: lambda i: len(i) >= n,
                             'maxItems': lambda n: lambda i: len(i) <= n}

        null_constraints = {_DEFAULT: lambda n: n is None}

        all_defaults = [constraint[_DEFAULT] for constraint in (string_constraints,
                                                                number_constraints,
                                                                integer_constraints,
                                                                boolean_constraints,
                                                                object_constraints,
                                                                array_constraints,
                                                                null_constraints)]

        any_constraints = {_DEFAULT: lambda v: any(d(v) for d in all_defaults)}

        self.type_constraints = {'string': string_constraints,
                                 'number': number_constraints,
                                 'integer': integer_constraints,
                                 'boolean': boolean_constraints,
                                 'object': object_constraints,
                                 'array': array_constraints,
                                 'null': null_constraints,
                                 'any': any_constraints}

    def items_validator(self, items_schema):
        validator = self.object_validator({'properties': {None: items_schema}})
        def items(items):
            return all(validator({None: i}) for i in items)
        return items

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, schema):
        self._schema = schema
        self.name = schema.get('name', '<unknown>')
        self.description = schema.get('description')
        self.validate = (self.object_validator(schema)
                         if schema
                         else lambda value: True)

    def object_validator(self, schema):
        props_validators = []
        required = set()

        for prop, requirements in schema.get('properties', {}).iteritems():
            types = requirements['type']
            if not isinstance(types, list):
                types = [types]
            try:
                validators = [self.validator_creator(self.type_constraints[t],
                                                     requirements)
                              for t in types]
            except KeyError, e:
                raise InvalidSchema('unknown type {type_}'.format(type_=e))

            props_validators.append((prop, validators))

            if requirements.get('required'):
                required.add(prop)

        @deserialize
        def validate(obj=None):
            valid = False
            seen = set()

            for prop, validators in props_validators:
                value = obj.get(prop)
                if value is None and prop in required:
                    valid = False
                else:
                    valid = any(validator(value) for validator in validators)
                if not valid:
                    raise ValueError('{prop} invalid: '
                                     '{value}'.format(prop=prop, value=value))
                seen.add(prop)

            unknown = set(obj) - seen
            if unknown:
                props = ', '.join(unknown)
                raise ValueError('unknown properties: '
                                 '{props}'.format(props=props))
            return valid
        return validate

    def validator_creator(self, constraints, requirements):
        default = constraints[_DEFAULT]
        # XXX this isn't right
        if default == self.object_validator:
            return self.object_validator(requirements)

        validators = [default]

        # we iterate over _DEFAULT but nobody'll have it
        for k, validator in constraints.iteritems():
            constraint = requirements.get(k)
            if constraint:
                validators.append(validator(constraint))
        def validator(value):
            try:
                valid = all(v(value) for v in validators)
            except Exception:
                valid = False
            return valid
        return validator
