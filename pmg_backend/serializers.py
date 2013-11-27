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
    Convert SQLAlchemy models to Python dicts, before encoding them in JSON format.
    """

    def __init__(self):
        return

    def to_dict(self, obj, include_related=False):
        tmp_dict = {
            c.name: getattr(obj, c.name) for c in obj.__table__.columns
        }
        return tmp_dict

    def serialize(self, obj_or_list, include_related=False):
        if isinstance(obj_or_list, db.Model):
            out = self.to_dict(obj_or_list, include_related)
        else:
            out = []
            for obj in obj_or_list:
                out.append(self.to_dict(obj, include_related))
        return simplejson.dumps(out, cls=CustomEncoder)


class BillSerializer(BaseSerializer):
    """
    Handle Bill models, and their related content.
    """

    def __init__(self):
        return

    def to_dict(self, obj, include_related=False):
        tmp_dict = BaseSerializer.to_dict(self, obj)
        entries = []
        if include_related:
            latest_version_dict = {}
            for entry in obj.entries:
                entry_dict = BaseSerializer.to_dict(self, entry)
                if entry.type == "bill":
                    latest_version_dict = entry_dict
                if entry.stage:
                    stage_dict = BaseSerializer.to_dict(self, entry.stage)
                    entry_dict['stage'] = stage_dict
                    if entry.stage.location:
                        location_dict = BaseSerializer.to_dict(self, entry.stage.location)
                        entry_dict['stage']['location'] = location_dict
                        entry_dict['stage'].pop('location_id')
                    entry_dict.pop('stage_id')
                if entry.agent:
                    agent_dict = BaseSerializer.to_dict(self, entry.agent)
                    entry_dict['agent'] = agent_dict
                    entry_dict.pop('agent_id')

                entries.append(entry_dict)
                tmp_dict['entries'] = entries
            if latest_version_dict:
                tmp_dict['latest_version'] = latest_version_dict
        else:
            tmp_dict['entry_count'] = len(obj.entries)
        return tmp_dict