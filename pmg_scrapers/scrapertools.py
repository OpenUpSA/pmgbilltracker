import requests

def handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

class URLFetcher(object):
    def __init__(self, url):
        self.url = url

    @property
    def html(self):
        r = requests.get(self.url)
        return r.content

class FileFetcher(object):
    filename = "bill"

    @property
    def html(self):
        return open(FileFetcher.filename).read()

