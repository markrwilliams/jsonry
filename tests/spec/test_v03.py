import pytest
import itertools

from jsonry import schema

# 5
SCHEMA_TEMPLATE = {'name': 'test-schema',
                   'description': 'a test schema',
                   'properties': None}


# where's float?
def test_schema_definition():
    sch = SCHEMA_TEMPLATE.copy()
    del sch['properties']

    # does a schema need a name?
    validator = schema.JSONValidate(fromdict=sch)
    assert validator.name == sch['name']
    assert validator.description == sch['description']


# 5.1
def test_simple_type():
    types = {'array': {'invalid': [1, 'a'],
                       'valid': [[1, 2]]},
             'boolean': {'invalid': ['a', 1.5, None],
                         'valid': [True, False]},
             'integer': {'invalid': [1.5, None, 'a'],
                         'valid': [0, 1]},
             'null': {'invalid': [],
                      'valid': [None]},
             'number': {'invalid': [None, 'a'],
                        'valid': [1, 1.5]},
             'string': {'invalid': [None, 1],
                        'valid': ['str', u'unicode']}}

    types['any'] = {'valid': itertools.chain.from_iterable(types.values()),
                    'invalid': []}

    sch = SCHEMA_TEMPLATE.copy()
    sch['properties'] = {}

    for t, fixtures in types.iteritems():
        sch['properties']['test'] = {'type': t}
        validator = schema.JSONValidate(fromdict=sch)
        for valid in fixtures['valid']:
            validator.validate({'test': valid})
        for invalid in fixtures['invalid']:
            with pytest.raises(ValueError):
                validator.validate({'test': invalid})

    # try to add a nonsense type
    sch['properties']['test'] = {'type': 'nonsense'}
    with pytest.raises(schema.InvalidSchema):
        schema.JSONValidate(fromdict=sch)
