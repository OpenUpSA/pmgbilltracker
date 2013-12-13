import re
from glob import glob
import csv
import sys

re_bill = re.compile("\[B\s*[0-9]+\s[A-Z]*\s*\-\s*[0-9]{4}\s*\]")
re_hansard_date = re.compile("[0-9]{4}\-[0-9]{2}\-[0-9]{2}")

writer = csv.writer(sys.stdout)
writer.writerow(["bill", "date", "filename", "source"])

for fname in glob("hansard/*.txt"):
    text = open(fname).read()
    dt = re_hansard_date.search(fname).group(0)

    groups = re_bill.finditer(text)
    for group in groups:
        bill = group.group(0)
        bill = "".join(bill.split())
        writer.writerow([bill, dt, fname, "hansard"])

    sys.stdout.flush()



