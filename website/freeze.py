import mimetypes

from website import app
from website import util
from flask.ext.frozen import Freezer


# Seems to be available only on some systems...
mimetypes.add_type('application/atom+xml', '.atom')

freezer = Freezer(app)

