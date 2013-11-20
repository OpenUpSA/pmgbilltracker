import simplejson
from datetime import datetime, date
from models import *
from pmg_backend import db, logger


class CustomEncoder(simplejson.JSONEncoder):
    """
    Define encoding rules for fields that are not readily serializable.
    """

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            encoded_obj = obj.strftime("%B %d, %Y")
        elif isinstance(obj, db.Model):
            try:
                encoded_obj = simplejson.dumps(obj.to_dict(), cls=CustomEncoder)
                logger.debug(encoded_obj)
            except Exception:
                encoded_obj = str(obj)
        else:
            encoded_obj = simplejson.JSONEncoder.default(self, obj)
        return encoded_obj


class BaseSerializer():
    """
    Convert sqlalchemy models to Python dicts, before encoding them in JSON format.
    """

    def __init__(self):
        return

    def to_dict(self, obj):
        return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

    def serialize(self, obj_or_list):
        if isinstance(obj_or_list, db.Model):
            out = self.to_dict(obj_or_list)
            return simplejson.dumps(out, cls=CustomEncoder)
        else:
            out = []
            for obj in obj_or_list:
                out.append(self.to_dict(obj))
            return simplejson.dumps(out, cls=CustomEncoder)


# Entry stuff
#
#def to_dict(self):
#    entry_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
#    # nest related fields
#    entry_dict.pop('agent_id')
#    entry_dict['agent'] = self.agent.to_dict()
#    entry_dict.pop('stage_id')
#    entry_dict['stage'] = self.stage.to_dict()
#    entry_dict.pop('location_id')
#    entry_dict['location'] = self.location.to_dict()
#
#    versions = []
#    for item in self.bill_versions.all():
#        tmp = item.to_dict()
#        tmp.pop('entry_id')
#        versions.append(tmp)
#    entry_dict['versions'] = versions
#
#    content = {}
#    for item in self.content.all():
#        tmp = item.to_dict()
#        tmp.pop('entry_id')
#        content_type = tmp['type']
#        if content.get(content_type):
#            content[content_type].append(tmp)
#        else:
#            content[content_type] = [tmp, ]
#    entry_dict['content'] = content
#
#    entry_dict.pop('bill_id')
#    return entry_dict

# Bill stuff
#
#if include_related:
#    # add related entry objects
#    entry_list = []
#    if self.entries:
#        latest_version = None
#        current_status = None
#        for entry in self.entries.order_by(Entry.date):
#            # add entry
#            entry_list.append(entry.to_dict())
#            # extract latest bill version
#            if len(entry.bill_versions.all()) > 0:
#                latest_version = entry.bill_versions[-1].to_dict()
#                bill_dict['latest_version'] = latest_version
#            # extract current status
#            if entry.new_status:
#                current_status = entry.new_status
#                bill_dict['status'] = current_status
#    bill_dict['entries'] = entry_list
#return bill_dict

