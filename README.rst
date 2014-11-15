# jsonry

A JSON utility library; a place for JSON tools.

## `jsonry.schema`

``jsonry.schema`` is a Python module that checks if JSON objects conform to `JSON schemas <http://tools.ietf.org/html/draft-zyp-json-schema-03>`_.

### Usage
Schema and instance taken from `Wikipedia <http://en.wikipedia.org/wiki/Json#Schema>`_.

    >>> schema = '''
    {
            "name":"Product",
            "properties":
            {
                    "id":
                    {
                            "type":"number",
                            "description":"Product identifier",
                            "required":true
                    },
                    "name":
                    {
                            "type":"string",
                            "description":"Name of the product",
                            "required":true
                    },
                    "price":
                    {
                            "type":"number",
                            "minimum":0,
                            "required":true
                    },
                    "tags":
                    {
                            "type":"array",
                            "items":
                            {
                                    "type":"string"
                            }
                    },
                    "stock":
                    {
                            "type":"object",
                            "properties":
                            {
                                    "warehouse":
                                    {
                                            "type":"number"
                                    },
                                    "retail":
                                    {
                                            "type":"number"
                                    }
                            }
                    }
            }
    }
    '''
    >>> doc = '''
    {
            "id": 1,
            "name": "Foo",
            "price": 123,
            "tags": ["Bar","Eek"],
            "stock": { "warehouse":300, "retail":20 }
        }
    '''
    >>> from jsonry.schema import JSONValidate(fromstring=schema)
    >>> validator = JSONValidate(fromstring=schema)
    >>> validator.validate(fromstring=doc)
    True
    >>> docdict = loads(doc)
    >>> docdict['stock']['warehouse'] = 'bad value'
    >>> validator.validate(fromdict=docdict)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "jschema/__init__.py", line 131, in validate
        valid = any(validator(value) for validator in validators)
      File "jschema/__init__.py", line 131, in <genexpr>
        valid = any(validator(value) for validator in validators)
      File "jschema/__init__.py", line 134, in validate
        '{value}'.format(prop=prop, value=value))
    ValueError: warehouse invalid: bad value
    >>>
