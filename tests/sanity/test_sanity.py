import pkg_resources

from jschema import JSONValidate

def test_sanity():
    schema_file = pkg_resources.resource_filename(__name__, 'test_schema.json')
    doc_file = pkg_resources.resource_filename(__name__, 'doc.json')
    schema = open(schema_file)
    doc = open(doc_file)
    v = JSONValidate(fromfile=schema)
    
    assert v.validate(fromfile=doc)


if __name__ == '__main__':
    import sys
    import traceback

    try:
        test_sanity()
    except:
        print traceback.format_exc()
        sys.exit(1)
    sys.exit(0)

