import json
from datetime import datetime, date
from pmg_backend import db, logger


class CustomEncoder(json.JSONEncoder):
    """
    Define encoding rules for fields that are not readily serializable.
    """

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            encoded_obj = obj.strftime("%B %d, %Y")
        elif isinstance(obj, db.Model):
            try:
                encoded_obj = json.dumps(obj.to_dict(), cls=CustomEncoder, indent=4)
                logger.debug(encoded_obj)
            except Exception:
                encoded_obj = str(obj)
        else:
            encoded_obj = json.JSONEncoder.default(self, obj)
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
        return json.dumps(out, cls=CustomEncoder, indent=4)


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
                if not entry.is_deleted:
                    entry_dict = BaseSerializer.to_dict(self, entry)
                    if entry.type == "bill":
                        latest_version_dict = entry_dict
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
