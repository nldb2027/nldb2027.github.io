"""Optional local smoke-test renderer when Pelican isn't installed.

This uses Mistune to approximate Python-Markdown and **is not** a substitute
for Pelican's actual build. It helps validate templates and internal links.
"""
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlsplit, unquote
from html import escape
import re
import sys

try:
    import mistune
    from bs4 import BeautifulSoup
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError as e:
    raise SystemExit('Preview check requires mistune, beautifulsoup4, and jinja2') from e

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from pelicanconf import SITE, SITENAME, EVENTS, NEXT_DEADLINE, BASE_PATH, EVENTS_JSON
from tools.lexicon_filters import entry_sections, entry_intro
out=root/'preview'
import shutil
if out.exists(): shutil.rmtree(out)
out.mkdir()
shutil.copytree(root/'theme/static',out/'assets')
shutil.copy(root/'content/extra/nldb2027.ics',out/'nldb2027.ics')
md=mistune.create_markdown(escape=False, plugins=['table','strikethrough'])
env=Environment(loader=FileSystemLoader(str(root/'theme/templates')),autoescape=False)
env.filters.update(entry_sections=entry_sections,entry_intro=entry_intro)

def md_to_html(body):
    # Mistune lacks Python-Markdown's attr_list extension; emulate just the
    # attributes used in this project when generating a test-only preview.
    attrs=[]
    for line in body.splitlines():
        m=re.search(r'^## (.+?) \{#([^}]+)\}$',line)
        if m:
            body=body.replace(line,'## '+m.group(1),1)
            attrs.append((m.group(1),m.group(2)))
    body=re.sub(r'(?m)^\{:\s*\.(topics|sc)\s*\}\s*$', '', body)
    html=md(body)
    for text, id_ in attrs:
        html=html.replace('<h2>'+escape(text)+'</h2>', '<h2 id="'+id_+'">'+escape(text)+'</h2>',1)
    html=re.sub(r'<ol>', '<ol class="topics">', html) if '<h3>topics include' in html else html
    html=html.replace('<h3>topics include, but are not limited to</h3>', '<h3 class="sc">topics include, but are not limited to</h3>')
    return html

for fp in sorted((root/'content/pages').glob('*.md')):
    source=fp.read_text()
    metadata_text,body=source.split('\n\n',1)
    meta=dict(line.split(': ',1) for line in metadata_text.splitlines() if ': ' in line)
    page=SimpleNamespace(**{k.lower():v for k,v in meta.items()})
    page.url=meta.get('URL',meta['Slug']+'/')
    page.content=md_to_html(body)
    filename=meta.get('Save_as',meta['Slug']+'/index.html')
    target=out/filename
    target.parent.mkdir(parents=True,exist_ok=True)
    html=env.get_template(meta.get('Template','page')+'.html').render(page=page,
        SITE=SITE, SITENAME=SITENAME,EVENTS=EVENTS,NEXT_DEADLINE=NEXT_DEADLINE,BASE_PATH=BASE_PATH,EVENTS_JSON=EVENTS_JSON)
    target.write_text(html,encoding='utf8')
    soup=BeautifulSoup(html,'html.parser')
    sections=soup.select('main.page section.row')
    print(fp.name,'->',target.relative_to(out),'sections',len(sections),'bytes',len(html))
    assert len(sections)>=2,fp.name

broken=[]
for fp in out.rglob('*.html'):
    soup=BeautifulSoup(fp.read_text(),'html.parser')
    for x in soup.select('[href],[src]'):
        href=x.get('href',x.get('src'))
        parsed=urlsplit(href)
        if not href.startswith('/') or parsed.netloc: continue
        if parsed.path=='/': expected=out/'index.html'
        elif parsed.path.endswith('/'): expected=out/parsed.path.lstrip('/')/'index.html'
        else: expected=out/parsed.path.lstrip('/')
        if not expected.exists(): broken.append((fp.relative_to(out),href))
        if parsed.fragment and expected.exists() and expected.suffix=='.html':
            if not BeautifulSoup(expected.read_text(),'html.parser').find(id=unquote(parsed.fragment)):
                broken.append((fp.relative_to(out),href+' [bad anchor]'))
print('broken links:',broken[:30],f'(total {len(broken)})')
if broken: raise SystemExit(1)
