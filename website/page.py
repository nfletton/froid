import os

import werkzeug.utils
import yaml
from datetime import datetime
from flask import url_for


class Page(object):
    def __init__(self, head, body, content_path, modified_time, site):
        self.head = head
        self.body = body
        self.content_path = content_path
        self.modified_time = datetime.fromtimestamp(modified_time).isoformat() + '-07:00'
        self.name = os.path.split(os.path.splitext(content_path)[0])[1]
        self._active_trail = None
        self.region_blocks = {}

    def url(self, **kwargs):
        return url_for('content', url_path=self.name, **kwargs)

    @werkzeug.utils.cached_property
    def meta(self):
        return yaml.safe_load(self.head) or {}
