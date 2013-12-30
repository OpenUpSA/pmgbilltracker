import requests
import re

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


# RE-pattern for finding bill instances
# (bracket / space) (type) (number) (version) - (year) (bracket / space)
bill_pattern_1 = r'(^|[\s\[])(PMB|B)\s*([0-9]+)([A-Z])*\s*-\s*([0-9]{4})($|[\s\]])'  # doesn't match draft bills
bill_pattern_2 = r'(PMB|B)\s*([0-9]+|X+)*([A-Z])*\s*-\s*([0-9]{4})'  # matches draft bills


def find_bills(text, include_versions=False):
    """
    Find the reference code for each bill mentioned in the given text.
    """

    matches = re.findall(bill_pattern_1, text, re.IGNORECASE|re.MULTILINE)
    if not matches:
        return None

    out = {}
    for result in set(matches):
        bracket_1, bill_type, number, version, year, bracket_2 = result
        bill_type = bill_type.upper()
        version = version.upper()
        code = bill_type + number + "-" + year
        out[code] = [code,]
        if include_versions and version:
            version_id = bill_type + number + (version if version else "") + "-" + year
            if not version_id in out[code]:
                out[code].append(version_id)

    if include_versions:
        return out
    else:
        return out.keys()


def analyze_bill_code(text):
    """
    Extract components of the information contained in a code that references a particular bill, eg. "[PMB15C - 2013]".
    """

    match = re.match(bill_pattern_2, text, re.IGNORECASE)
    if not match:
        return None

    bill_type = match.group(1).upper()
    number = match.group(2)
    if number and "X" in number:
        number = None
    version = match.group(3)
    if version:
        version = version.upper()
    year = match.group(4)

    code = bill_type + (number if number else "X") + "-" + year

    status = "Bill"
    if not number:
        status = "Draft"
    elif "as enacted" in text.lower():
        status = "Act"

    out = {
        'code': code,
        'type': bill_type,
        'status': status,
        'year': year,
        'version': version if version else None,
    }
    return out