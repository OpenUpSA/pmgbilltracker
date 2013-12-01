import simplejson

f = open('archive.json', 'r')
archive = simplejson.load(f)
f.close()

archive_new = {}

print archive[0]
print archive[0]['files'][0]['meta']['DocumentTypeID']

print str(len(archive)) + " Directories archived"
num_files = 0
for directory in archive:
    num_files += len(directory['files'])
    for tmp_file in directory['files']:
        meta = tmp_file['meta']
        filename = tmp_file['file']
        if not meta:
            print "No metadata for file: " + filename
            continue
        file_type = meta['DocumentTypeID'].lower()
        if not archive_new.get(file_type):
            archive_new[file_type] = []
        record = {
            "file_name": filename,
            "url": "www.parliament.gov.za/live/commonrepository/Processed/" + directory['directory'] + meta['original_filename']
        }
        for key, val in meta.iteritems():
            if not (key in ['DocumentTypeID', 'original_filename'] or val in [None, '1/1/1753']):
                record[key] = val
        archive_new[file_type].append(record)
print str(num_files) + " Files"

print archive_new['hansard'][5]

print "Available types:"
for key, val in archive_new.iteritems():
    print "\t" + key

f = open('archive_new.json', 'w+')
f.write(simplejson.dumps(archive_new, indent=4))
f.close()