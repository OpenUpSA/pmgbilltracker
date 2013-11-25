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
        content = []
        if include_related:
            for tag in obj.content.all():
                tag_dict = BaseSerializer.to_dict(self, tag)
                tag_dict.pop('bill_id')
                entry_dict = BaseSerializer.to_dict(self, tag.entry)

                if tag.entry.location:
                    location_dict = BaseSerializer.to_dict(self, tag.entry.location)
                    entry_dict['location'] = location_dict
                if tag.entry.stage:
                    stage_dict = BaseSerializer.to_dict(self, tag.entry.stage)
                    entry_dict['stage'] = stage_dict
                if tag.entry.agent:
                    agent_dict = BaseSerializer.to_dict(self, tag.entry.agent)
                    entry_dict['agent'] = agent_dict

                entry_dict.pop('location_id')
                entry_dict.pop('stage_id')
                entry_dict.pop('agent_id')

                tag_dict['entry'] = entry_dict
                tag_dict.pop('entry_id')

                content.append(tag_dict)
                tmp_dict['content'] = content
        else:
            tmp_dict['content_count'] = obj.content.count()
        return tmp_dict