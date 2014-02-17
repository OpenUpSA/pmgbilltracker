import requests
import json
import os
import tempfile
import re

url = "http://db3sqepoi5n3s.cloudfront.net/files/pmb5_2013.pdf"
url = "http://db3sqepoi5n3s.cloudfront.net/files/130416pmb3-2013.pdf"
url = "http://db3sqepoi5n3s.cloudfront.net/files/131031b18b-2013.pdf"
url = "http://db3sqepoi5n3s.cloudfront.net/files/130621b15-2013.pdf"
url = "http://db3sqepoi5n3s.cloudfront.net/files/131118b55-2013public_administration_management.pdf"

reg_section1 = re.compile(r"section\s+(?:74|75|76|77)\s+bill", re.IGNORECASE)
reg_section2 = re.compile(r"section\s+(?:74|75|76|77)\b", re.IGNORECASE)
reg_introduced_by1 = re.compile(r"""
    # Search for something that looks like (Minister of Finance)
    \(
    (
        Minister
        [^)]+
    )
    \)
""", re.VERBOSE | re.IGNORECASE)

reg_introduced_by2 = re.compile(r"""
    # Search for something that looks like (Ms J Jacobson MP)
    \(
    (
        [^)]+
    MP)
    \)
""", re.VERBOSE | re.IGNORECASE)

reg_introduced_by3 = re.compile(r"""
    # Search for something that looks like (Select committee on Cooperative ....)
    \(
    ([^)]*Committee[^)]*)
    \)
""", re.VERBOSE | re.IGNORECASE)


def get_pdf(url, chunk_size=1000):
    fp = tempfile.NamedTemporaryFile("rw", prefix="pmg_", suffix=".pdf", delete=False)
    with open(fp.name, "wb") as fp:
        resp = requests.get(url, stream=True)
        for chunk in resp.iter_content(chunk_size):
            fp.write(chunk)
    return fp.name

def convert_to_text(path):
    cmd = "pdftotext %s" % path
    os.system(cmd)
    return path.replace(".pdf", ".txt")

def extract_section(text):
    match = reg_section1.search(text)
    if not match:
        match = reg_section2.search(text)

    if not match:
        return None

    section = match.group()

    if "74" in section: return 74
    if "75" in section: return 75
    if "76" in section: return 76
    if "77" in section: return 77

def extract_introduced_by(text):
    match = reg_introduced_by1.search(text)

    if not match:
        match = reg_introduced_by2.search(text)

    if not match:
        match = reg_introduced_by3.search(text)

    if not match:
        return "Boom!!"

    return match.groups()[0]

def extract_introduction_location(text):
    return "NA"
    
def scrape_pdf(url):
    pdf_path = get_pdf(url)
    text_path = convert_to_text(pdf_path)
    text = open(text_path).read()[0:2000]
    js = {
        "section" : extract_section(text),
        "introduced_by" : extract_introduced_by(text),
        "introduced_at" : extract_introduction_location(text)
    }

    print json.dumps(js, indent=4)
    
scrape_pdf(url)
