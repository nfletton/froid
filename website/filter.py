"""
Froid filters
"""
from bs4 import BeautifulSoup

from website import app


@app.template_filter()
def truncate_html(html, length=4000):
    """
    Cleanly truncate a chunk of html
    """
    return unicode(BeautifulSoup(html[:length], "lxml"))[12:][:-14]
