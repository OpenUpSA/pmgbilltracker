import requests
import os
import xmltodict
import simplejson
import time
from operator import itemgetter

BASE_DIR = "/Users/petrus/Desktop/archive"
ERROR_DIR = BASE_DIR + "/errors"

class NoMetaDataException(Exception):
    pass


def add_to_archive(date_str, filename, meta):

    archive_file = open(BASE_DIR + "/index.json", "r")
    archive = simplejson.load(archive_file)
    archive_file.close()

    file_type = meta['DocumentTypeID'].lower()
    if not archive.get(file_type):
        archive[file_type] = {}
    meta['FileName'] = filename
    rec = {}
    for key, val in meta.iteritems():
        if not (key in ['DocumentTypeID', ] or val in [None, '1/1/1753']):
            rec[key] = val
    doc_id = meta["DocumentNumber"]
    tmp = []
    if archive[file_type].get(doc_id):
        tmp = archive[file_type][doc_id]
    tmp.append(rec)
    tmp_sorted = sorted(tmp, key=itemgetter('FileName'))
    archive[file_type][doc_id] = tmp_sorted


    archive_file = open(BASE_DIR + '/index.json', 'w+')
    archive_file.write(simplejson.dumps(archive, indent=4))
    archive_file.close()
    print "file meta data added to archive"
    return


def get_metadata(meta_url, date_str, filename_orig):

    tmp = requests.get(meta_url)
    if tmp.status_code == 404:
        raise NoMetaDataException
    elif tmp.status_code != 200:
        print "HTTP error " + str(tmp.status_code) + " while retrieving metadata."
        raise Exception
    tmp_dict = xmltodict.parse(tmp.text)
    meta = dict(tmp_dict['Document'])
    meta["URL"] = "http://www.parliament.gov.za/live/commonrepository/Processed/" + date_str + "/" + filename_orig

    filename = date_str[0:4] + "-" + date_str[4:6] + "-" + date_str[6:8] + "_" + filename_orig
    archive_filename = meta["DocumentTypeID"].lower() + "/" + filename
    add_to_archive(date_str, filename, meta)
    return archive_filename, meta


def get_file(file_name, file_url, meta):

    print("Downloading file from " + file_url)

    # prepare filename
    type_str = ""
    if meta and meta.get("DocumentTypeID"):
        # separate files into directories, based on type
        type_str = meta["DocumentTypeID"].lower() + "/"
        if not os.path.exists(BASE_DIR + "/" + type_str):
            os.makedirs(BASE_DIR + "/" + type_str)

    # download file
    tmp = requests.get(file_url)
    if tmp.status_code != 200:
        print "HTTP error " + str(tmp.status_code) + " while downloading file."
        raise Exception

    # save file to disc
    tmp_file = open(BASE_DIR + "/" + file_name, "wb")
    tmp_file.write(tmp.content)
    tmp_file.close()
    print "file downloaded"
    return file_name


f = []
for (dir_path, dir_names, file_names) in os.walk(ERROR_DIR):
    f.extend(file_names)
    break

base_url = "http://www.parliament.gov.za/live/commonrepository/Processed"

i = 0
for file_name in f:

    name_str, ext = file_name.split(".")

    if len(name_str) != 0:  # ignore dot-files
        date_uploaded = name_str[0:4] + name_str[5:7] + name_str[8:10]
        filename_orig = name_str[11::]
        tmp = base_url + "/" + date_uploaded + "/" + filename_orig + "."
        file_url = tmp + ext
        meta_url = tmp + "xml"
        print str(i) + ": \t" + file_url
        try:
            archive_filename, meta = get_metadata(meta_url, date_uploaded, filename_orig + "." + ext)
            get_file(archive_filename, file_url, meta)
            # remove error
            os.remove(ERROR_DIR + "/" + file_name)
        except NoMetaDataException:
            print "No meta data"
            try:
                date_str = date_uploaded
                get_file("unknown/" + date_str[0:4] + "-" + date_str[4:6] + "-" + date_str[6:8] + "_" + filename_orig + "." + ext, file_url, None)
            except Exception as e:
                print "\nError scraping " + file_url
                print e
                pass
            pass
        except Exception as e:
            print "\nError scraping " + file_url
            print e
            pass
        i += 1
        time.sleep(13)
