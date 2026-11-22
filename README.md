# NLDB Lexicon — Markdown-powered Pelican website

## Quick start

```sh
python -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python tools/build_calendar.py
pelican content -s pelicanconf.py -o output
pelican --listen -o output          
```

Or `make build`, `make serve`, or `make publish` on systems with Make.
