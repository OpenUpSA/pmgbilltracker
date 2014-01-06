import simplejson
from operator import itemgetter

BASE_DIR = "/Users/petrus/Desktop/archive"
ERROR_DIR = BASE_DIR + "/errors"

f = open(BASE_DIR + '/archive.json', 'r')
archive = simplejson.load(f)
f.close()

archive_new = {}

# print archive[0]
# print archive[0]['files'][0]['meta']['DocumentTypeID']

print str(len(archive)) + " Directories archived"
num_files = 0
for directory in archive:
    num_files += len(directory['files'])
    for tmp_file in directory['files']:
        meta = tmp_file['meta']
        filename = tmp_file['file']
        try:
            filename = filename.split("/")[1]
            file_type = meta['DocumentTypeID'].lower()
            if not archive_new.get(file_type):
                archive_new[file_type] = {}
            meta['FileName'] = filename
            meta["URL"] = "http://www.parliament.gov.za/live/commonrepository/Processed/" + directory['directory'] + meta['original_filename']
            rec = {}
            for key, val in meta.iteritems():
                if not (key in ['DocumentTypeID', 'original_filename'] or val in [None, '1/1/1753']):
                    rec[key] = val
            doc_id = meta["DocumentNumber"]
            tmp = []
            if archive_new[file_type].get(doc_id):
                tmp = archive_new[file_type][doc_id]
            tmp.append(rec)
            tmp_sorted = sorted(tmp, key=itemgetter('FileName'))
            archive_new[file_type][doc_id] = tmp_sorted
        except Exception:
            #  create ref in error directory, so that this record can be cleaned up later
            tmp = open(ERROR_DIR + "/" + filename, 'a')
            tmp.close()
print str(num_files) + " Files"

f = open(BASE_DIR + '/index.json', 'w+')
f.write(simplejson.dumps(archive_new, indent=4))
f.close()