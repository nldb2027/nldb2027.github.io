"""Production overrides: edit the real URL and review content before publishing."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))
from pelicanconf import *  # noqa: F403,F401

SITEURL = 'https://example.org'  # Replace with your actual origin, no trailing slash.
BASE_PATH = '/'  # Change to '/lexicon/' when deployed in a subdirectory.
# The draft and noindex flags are inherited from pelicanconf.py until reviewed.
