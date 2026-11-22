"""Pelican configuration for the NLDB Lexicon website.

Only capitalized settings are exported to Jinja templates by Pelican.
SITE is a plain dict; change the branding below without editing partials.
"""
from datetime import datetime, timezone
from json import dumps
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))  # Run the Pelican CLI from this project directory.
from event_data import EVENTS

SITENAME = 'NLDB 2027'
AUTHOR = 'NLDB organisers'
DEFAULT_LANG = 'en'
TIMEZONE = 'Europe/Bucharest'

# For deployment at https://example.org/lexicon/: set BASE_PATH='/lexicon/'
# and SITEURL='https://example.org/lexicon' in publishconf.py.
BASE_PATH = '/'
SITEURL = ''  # For local `pelican --listen`. Set the public URL when publishing.
RELATIVE_URLS = False

SITE = {
    'name': SITENAME,
    'city': 'University of Bucharest',
    'description': 'NLDB 2027, the 32nd International Conference on Applications of Natural Language to Information Systems, Bucharest, Romania',
    'footerSummary': 'The 32nd International Conference on Applications of Natural Language to Information Systems, Bucharest, Romania, 16-18 June 2027.',
    'colophon': 'Static site with no cookies or trackers based on a template by Rareș Roșcan. Hosted by the Laboratory for Cybernetic Research and Good Life.',
    'organizer': 'University of Bucharest',  # Replace the placeholder 'university' when confirmed.
    'contactEmail': 'sergiu.nisioi@g.unibuc.ro',
    'lastUpdated': '21 November 2026',
    'draft': False,
    'noindex': True,  # Switch to False before launch when the content is confirmed.
    'navigation': [
        {'text':'Call for Papers', 'path':'call-for-papers/'},
        {'text':'Submission', 'path':'submission/'},
        #{'text':'Keynotes', 'path':'keynotes/'},
        #{'text':'Programme', 'path':'programme/'},
        #{'text':'Registration', 'path':'registration/'},
        {'text':'Committees', 'path':'committees/'},
        {'text':'Dates', 'path':'dates/'},
        {'text':'Venue & Travel', 'path':'venue/'},
    ],
}

# Escape JSON for safe embedding into an HTML <script type=application/json> node.
EVENTS_JSON = dumps(EVENTS, ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
NOW = datetime.now(timezone.utc)
NEXT_DEADLINE = next((e for e in EVENTS
                      if e.get('deadline') and datetime.fromisoformat(e['deadline']) >= NOW), None)

# Every public page is authored in content/pages/*.md. Templates only define
# the presentation and reusable components; there is no TEMPLATE_PAGES mapping.
from tools.lexicon_filters import entry_sections, entry_intro
JINJA_FILTERS = {'entry_sections': entry_sections, 'entry_intro': entry_intro}
MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
    },
    'output_format': 'html5',
}

PATH = 'content'
THEME = 'theme'
THEME_STATIC_DIR = 'assets'
THEME_STATIC_PATHS = ['static']
# The Markdown page content/pages/index.md publishes to index.html itself.
# Disable Pelican's built-in blog index to avoid a conflicting output file.
DIRECT_TEMPLATES = []
TEMPLATE_PAGES = {}
PAGE_PATHS = ['pages']
ARTICLE_PATHS = ['articles']
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'
ARTICLE_URL = 'news/{slug}/'
ARTICLE_SAVE_AS = 'news/{slug}/index.html'
DISPLAY_PAGES_ON_MENU = False  # The theme renders navigation explicitly.
DEFAULT_PAGINATION = False

STATIC_PATHS = ['extra/nldb2027.ics']
EXTRA_PATH_METADATA = {'extra/nldb2027.ics': {'path': 'nldb2027.ics'}}

# No blog feeds needed for this conference website.
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
FEED_ALL_RSS = None
