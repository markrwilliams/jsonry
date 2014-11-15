import pkgutil
from jsonry.schema import JSONValidate

SCHEMA = '''\
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

DOC = '''{
    "id": 1,
    "name": "Foo",
    "price": 123,
    "stock": {
        "retail": 20,
        "warehouse": 300
    },
    "tags": [
        "Bar",
        "Eek"
    ]
}'''


def test_sanity():
    v = JSONValidate(fromstring=SCHEMA)
    assert v.schema
    assert v.validate(fromstring=DOC)
