"""
Parses hansard documents.
Assumes documents are found in a subfolder called hansards/
All hansard documents should be converted to text,
I used antiword to do convert .doc to .txt
"""

from glob import glob, iglob
from collections import defaultdict
from dateutil import parser
import re
import os
import sys

re_bill = re.compile("((?:[A-Z]+\s*){1,6} BILL)")
re_new_section = re.compile("^\s*(?:[A-Z]+\s*)+\s*$")
re_ayes = re.compile("AYES:*\s*-\s*[0-9]+:\s*")
re_noes = re.compile("NOES:*\s*-\s*[0-9]+:\s*")
path_debates = "debates/"
path_hansards = "hansard/"

def write_debates(bill):
    outname = "debates/debate_{debate}_{date}.txt".format(debate=bill["name"], date=bill["date"].strftime("%Y-%m-%d"))
    fp = open(outname, "w")
    fp.write(str(bill["date"]))
    fp.write("\n")
    fp.write(bill["debate"].strip())
    fp.close()

def write_division(bill):
    outname = "debates/division_{debate}_{date}.txt".format(debate=bill["name"], date=bill["date"].strftime("%Y-%m-%d"))
    fp = open(outname, "w")
    fp.write(bill["name"])
    fp.write("\n")
    fp.write("AYES (%d)\n" % len(bill["ayes"]))
    for el in bill["ayes"]:
        fp.write("{el}\n".format(el=el))

    fp.write("\n")
    fp.write("NOES (%d)\n" % len(bill["noes"]))
    for el in bill["noes"]:
        fp.write("{el}\n".format(el=el))

    if type(bill["abstain"]) == list and len(bill["abstain"]) > 0:
        fp.write("\n")
        fp.write("ABSTAIN (%d)\n" % len(bill["abstain"]))
        for el in bill["abstain"]:
            fp.write("{el}\n".format(el=el))
        
    fp.close()


class DividedParser(object):
    def __init__(self, text):
        self.text = text
        self.lines = iter(text.split("\n"))
        self.state = self.find_date_state
        self.current_bill = self._newbill()
        self.date = None

    def _newbill(self):
        return defaultdict(str)

    def _is_new_section(self, line):
        line = line.strip()
        if len(line) > 0:
            if line == line.upper() and line[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                return True
        return False

    @property
    def passes_basic_checks(self):
        if "The House divided" in self.text:
            return True
        return False

    def find_date_state(self, line):
        if line != "":
            try:
                date = parser.parse(line)
                self.date = date
                self.state = self.find_bill_state
            except ValueError:
                pass


    def find_bill_state(self, line):
        if not "BILL" in line: return
        match = re_bill.search(line)
        if match:
            self.current_bill["name"] = line
            self.state = self.find_second_reading_state

    def find_second_reading_state(self, line):
        if line != "":
            if line != "(Second Reading debate)":
                self.current_bill = self._newbill()
                self.state = self.find_bill_state
            else:
                self.state = self.find_house_divided_state


    def find_house_divided_state(self, line):
        if line == "The House divided:":
            self.state = self.find_ayes_state
        elif self._is_new_section(line):
            self.current_bill = self._newbill()
            self.state = self.find_bill_state
        else:
            self.current_bill["debate"] += "\n" + line

    def find_ayes_state(self, line):
        if line.lower().startswith("ayes"):
            self.state = self.process_ayes_state
            return self.process_ayes_state(line)

    def process_ayes_state(self, line):
        if line.lower().startswith("noes"):
            self.state = self.process_noes_state
            return self.process_noes_state(line)
        else:
            self.current_bill["ayes"] += line

    def process_noes_state(self, line):
        if line == "":
            self.state = self.process_after_noes_state
        elif line.lower().startswith("abstain"):
            self.state = self.process_abstain_state
            return self.process_abstain_state(line)
        else:
            self.current_bill["noes"] += line

    def process_after_noes_state(self, line):
        if line.lower().startswith("abstain"):
            self.state = self.process_abstain_state
            return self.process_abstain_state(line)
        else:
            self.state = self.process_after_votes_state
            return self.process_after_votes_state(line)

    def process_abstain_state(self, line):
        if line == "":
            self.state = self.process_after_votes_state
            return self.process_after_votes_state(line)
        else:
            self.current_bill["abstain"] += line

    def process_after_votes_state(self, line):
        bill = self.current_bill
        self.current_bill = self._newbill()
        self.state = self.find_bill_state
        bill["date"] = self.date
        bill["ayes"] = re_ayes.sub("", bill["ayes"])
        bill["ayes"] = [el.strip() for el in bill["ayes"].split(";")]
        bill["noes"] = re_noes.sub("", bill["noes"])
        bill["noes"] = [el.strip() for el in bill["noes"].split(";")]
        if bill["abstain"] == "":
            bill["abstain"] = []
        else:
            bill["abstain"] = [el.strip() for el in bill["abstain"].split(":")[1].split(";")]
        return bill

    def __iter__(self):
        return self

    def next(self):
        for line in self.lines:
            line = line.strip()
            value = self.state(line)
            if value: return value
        raise StopIteration()

class Pager(object):
    def __init__(self, path):
        self.path = path
        self.files = iglob("{path}/*.txt".format(path=self.path))

    def __iter__(self):
        return self 

    def next(self):
        for fname in self.files:
            sys.stderr.write("\r{fname}".format(fname=fname))
            sys.stderr.flush()
            text = open(fname.strip()).read()
            return text
        sys.stderr.write("\n")
        raise StopIteration()

def parse():
    if not os.path.exists(path_debates):
        os.mkdir(path_debates)

    for text in Pager(path_hansards):
        parser = DividedParser(text)
        if parser.passes_basic_checks:
            for bill in parser:
                write_debates(bill)
                write_division(bill)

if __name__ == "__main__":
    parse()
