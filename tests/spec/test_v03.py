import pytest
import itertools

import jschema
# 5
SCHEMA_TEMPLATE  = {'name': 'test-schema',
                    'description': 'a test schema',
                    'properties': None}

# where's float?
def test_schema_definition():
    schema = SCHEMA_TEMPLATE.copy()
    del schema['properties']

    # does a schema need a name?
    validator = jschema.JSONValidate(fromdict=schema)
    assert validator.name == schema['name']
    assert validator.description == schema['description']

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

    schema = SCHEMA_TEMPLATE.copy()
    schema['properties'] = {}

    for t, fixtures in types.iteritems():
        schema['properties']['test'] = {'type': t}
        validator = jschema.JSONValidate(fromdict=schema)
        for valid in fixtures['valid']:
            validator.validate({'test': valid})
        for invalid in fixtures['invalid']:
            with pytest.raises(ValueError):
                validator.validate({'test': invalid})

    # try to add a nonsense type
    schema['properties']['test'] = {'type': 'nonsense'}
    with pytest.raises(jschema.InvalidSchema):
        jschema.JSONValidate(fromdict=schema)

