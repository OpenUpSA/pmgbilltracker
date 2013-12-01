import requests
import xmltodict
import simplejson
from bs4 import BeautifulSoup
import time
import os
import logging

# logging setup
logger = logging.getLogger('spider')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('spider.log')
fh.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)

base_url = "http://www.parliament.gov.za/live/commonrepository/Processed/"


def refresh_index():

    logger.debug("Refreshing Index")

    # retrieve index page
    index_page = requests.get(base_url)
    index_html = index_page.text

    # parse the HTML using BeautifulSoup
    index_parsed = BeautifulSoup(index_html)

    # extract hyperlinks
    index = []
    for link in index_parsed.find_all('a'):
        index.append(str(link.get('href')))

    # remove link to parent directory
    index = index[1::]

    # save to file
    with open('index.json', 'w') as outfile:
        simplejson.dump(index, outfile)
    return index


def scrape_dir(str_dir):

    logger.debug("Scraping directory: " + str_dir)

    # retrieve page
    dir_url = base_url + str_dir
    dir_page = requests.get(dir_url)
    dir_html = dir_page.text

    # parse the HTML using BeautifulSoup
    dir_parsed = BeautifulSoup(dir_html)

    # extract hyperlinks
    items = []
    link_list = dir_parsed.find_all('li')
    for i in range(len(link_list)):
        # ignore first entry, which is a link to parent directory
        if not i == 0:
            items.append(link_list[i].find('a').get('href'))

    logger.debug(items)

    entries = []
    for str_file in items:
        if not ".xml" in str_file:
            try:
                meta = get_metadata(str_dir, str_file)
            except Exception as e:
                logger.error(e)
                logger.error("No metadata for " + str_dir + str_file)
                meta = None
                pass

            filename = get_file(str_dir, str_file, meta)
            entries.append({'file': filename, 'meta': meta})
            time.sleep(13)
    return entries


def get_metadata(str_dir, str_file):

    logger.debug("Retrieving meta data")
    str_meta = ".".join(str_file.split(".")[0:-1]) + ".xml"
    url = base_url + str_dir + str_meta
    tmp = requests.get(url)
    if tmp.status_code != 200:
        logger.error("HTTP error " + str(tmp.status_code) + " while retrieving metadata.")
    tmp_dict = xmltodict.parse(tmp.text)
    #logger.debug(simplejson.dumps(tmp_dict, indent=4))
    meta = dict(tmp_dict['Document'])
    meta["original_filename"] = str_file
    return meta


def get_file(str_dir, str_file, meta):

    logger.debug("Downloading file from " + str_dir + str_file)

    # prepare filename
    type_str = ""
    if meta and meta.get("DocumentTypeID"):
        # separate files into directories, based on type
        type_str = meta["DocumentTypeID"].lower() + "/"
        if not os.path.exists("/mnt/archive/" + type_str):
            os.makedirs("/mnt/archive/" + type_str)

    # prepend upload date to filename
    date_str = str_dir[0:4] + "-" + str_dir[4:6] + "-" + str_dir[6:8]
    filename = type_str + date_str + "_" + str_file

    # download file
    tmp = requests.get(base_url + str_dir + str_file)
    if tmp.status_code != 200:
        logger.error("HTTP error " + str(tmp.status_code) + " while downloading file.")

    # save file to disc
    tmp_file = open("/mnt/archive/" + filename, "wb")
    tmp_file.write(tmp.content)
    tmp_file.close()
    return filename


def save_state(index_success, index_error):

    # save initial state to file
    with open('index_success.json', 'w') as outfile:
        simplejson.dump(index_success, outfile)
    with open('index_error.json', 'w') as outfile:
        simplejson.dump(index_error, outfile)


def initialize():

    # load index of directories to crawl
    try:
        index_file = open("index.json")
        index = simplejson.load(index_file)
        index_file.close()

    except IOError:
        index = refresh_index()

    for directory in index:
        logger.debug(directory)

    index_success = []
    index_error = []

    save_state(index_success, index_error)

    return index, index_success, index_error


def load_state():

    tmp = open("index.json")
    index = simplejson.load(tmp)
    tmp.close()

    tmp = open("index_success.json")
    index_success = simplejson.load(tmp)
    tmp.close()

    tmp = open("index_error.json")
    index_error = simplejson.load(tmp)
    tmp.close()

    return index, index_success, index_error


if __name__ == "__main__":

    try:
        # continue / retry
        index, index_success, index_error = load_state()
    except IOError:
        #start
        index, index_success, index_error = initialize()
        pass

    #errs = []
    #for item in errs:
    #    print scrape_dir(item)

    num_dirs = len(index)
    for i in range(num_dirs):
        ## hardstop
        #if i > 3:
        #    break
        directory = index.pop()
        if not directory in index_success:
            try:
                file_list = scrape_dir(directory)

                if file_list:
                    out = {"directory": directory, "files": file_list}
                    out = simplejson.dumps(out, indent=4)
                    with open("archive.json", "a") as tmp_file:
                        tmp_file.write(out + ",\n")
                if directory in index_error:
                    index_error.remove(directory)
                index_success.append(directory)
            except Exception:
                logger.error("Error scraping directory " + directory)
                if not directory in index_error:
                    index_error.append(directory)
                if directory in index_success:
                    index_success.remove(directory)
                pass
            save_state(index_success, index_error)
        logger.debug(str(i+1) + "/" + str(num_dirs) + " DIRECTORIES SCRAPED, " + str(len(index_error)) + " ERRORS")





