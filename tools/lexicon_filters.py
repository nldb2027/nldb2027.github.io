"""Build the original dictionary-grid page sections from *real Pelican Markdown*.

Only the Markdown heading hierarchy and two HTML comments are structural:

    ## Section title {#section-id}
    Ordinary **Markdown** paragraphs and lists.

    <!-- aside:start -->
    A sidebar in Markdown.
    <!-- aside:end -->

    <!-- lexicon:dates -->   # optional: data-driven calendar

All HTML is generated at build time; no special Pelican plugin is required.
"""
from html import escape
import re
import unicodedata

_HEADING = re.compile(r'<h2\b[^>]*>.*?</h2>', re.I | re.S)
_SIDE = re.compile(r'<!--\s*aside:start\s*-->(.*?)<!--\s*aside:end\s*-->', re.I | re.S)
_CUSTOM = re.compile(r'<!--\s*lexicon:(dates-big|dates|timezones)\s*-->', re.I)
_TAG_ATTR = re.compile(r'\bid\s*=\s*[\'\"]([^\'\"]+)[\'\"]', re.I)
_PAGE_LINK = re.compile(r'\b(href|src)=(\"|\')/(?!/)(.*?)\2', re.I | re.S)


def _slug(text):
    text = re.sub(r'<[^>]*>', '', text)
    ascii_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-z0-9]+', '-', ascii_text.lower()).strip('-')


def _calendar(events, next_deadline, big=False):
    """Keep dates from event_data.py instead of duplicating in Markdown files."""
    result = ['<ol class="dates%s">' % (' big' if big else '')]
    for e in events:
        deadline = e.get('deadline')
        css = ' class="next"' if next_deadline and next_deadline['id'] == e['id'] else ''
        attr = ' data-deadline="%s"' % escape(deadline, quote=True) if deadline else ''
        tag = '<span class="dagger" title="Provisional">†</span>' if e.get('provisional') else ''
        if e.get('date'):
            stamp = '<time class="d" datetime="%s">%s%s</time>' % (
                escape(e['date'], quote=True), escape(e['displayDate']), tag)
        else:
            stamp = '<span class="d"><span class="ph">%s</span> %s%s</span>' % (
                escape(e.get('placeholder', 'date')), escape(e['displayDate']), tag)
        result.append('<li%s%s><span class="ev">%s</span><span class="tag sc">next</span>'
                      '<span class="lead"></span>%s</li>' % (
                          css, attr, escape(e['label']), stamp))
    result.append('</ol>')
    return '\n'.join(result)


def _timezones(events):
    result = ['<div class="rule" hidden>',
              '<p><span class="sc">in your time zone</span><br><span class="muted" data-tz></span></p>',
              '<ul class="plain">']
    for e in events:
        if e.get('deadline'):
            result.append('<li>%s:<br><span data-local="%s"></span></li>' % (
                escape(e['label']), escape(e['deadline'], quote=True)))
    result.extend(['</ul>', '</div>'])
    return '\n'.join(result)


def _expand(fragment, events, next_deadline, base_path):
    def replacement(m):
        token = m.group(1).lower()
        if token == 'dates-big': return _calendar(events, next_deadline, big=True)
        if token == 'dates': return _calendar(events, next_deadline)
        if token == 'timezones': return _timezones(events)
        return m.group(0)
    fragment = _CUSTOM.sub(replacement, fragment)
    # Permit root-style Markdown links while supporting deployments under /lexicon/.
    base = (base_path or '/').rstrip('/') + '/'
    return _PAGE_LINK.sub(lambda m: '%s=%s%s%s%s' % (
        m.group(1), m.group(2), base, m.group(3), m.group(2)), fragment)


def entry_intro(rendered_html, events, next_deadline, base_path):
    """Homepage text before its first ## heading; hero is styled by home.html."""
    m = _HEADING.search(rendered_html)
    intro = rendered_html[:m.start()] if m else rendered_html
    return _expand(intro, events, next_deadline, base_path)


def entry_sections(rendered_html, events, next_deadline, base_path):
    """Split rendered Markdown at h2 headings, assigning numbered grid rows."""
    heads = list(_HEADING.finditer(rendered_html))
    rendered=[]
    for i, m in enumerate(heads):
        end = heads[i+1].start() if i+1<len(heads) else len(rendered_html)
        heading = m.group()
        content = rendered_html[m.end():end]
        sides = _SIDE.findall(content)
        content = _SIDE.sub('', content).strip()
        content = _expand(content, events, next_deadline, base_path)
        aside = _expand('\n'.join(s.strip() for s in sides), events, next_deadline, base_path)
        # Metadata ID is attached by Python-Markdown's attr_list extension.
        id_match = _TAG_ATTR.search(heading)
        section_id = id_match.group(1) if id_match else _slug(heading)
        # Keep the old TOPICS numbered-list type if the Markdown parser has not
        # assigned the attr_list class (useful for fallback renderers).
        if section_id in ('scope', 'cfp'):
            content = re.sub(r'<ol(?![^>]*\bclass=)', '<ol class="topics"', content, count=1)
        if section_id == 'did-you-mean':
            content = re.sub(r'<ul(?![^>]*\bclass=)', '<ul class="plain"', content, count=1)
        if section_id in ('general-chairs', 'programme-chairs',
                          'local-organising-committee', 'publicity-chair'):
            content = re.sub(r'<ul(?![^>]*\bclass=)', '<ul class="people"', content, count=1)
        heading = _expand(heading, events, next_deadline, base_path)
        row = '<section class="row" id="%s">\n' % escape(section_id, quote=True)
        row += '<div class="num">§&thinsp;%d</div>\n' % (i+1)
        row += '<div class="main">%s\n%s</div>\n' % (heading, content)
        row += '<aside class="side">%s</aside>\n</section>' % aside
        rendered.append(row)
    return '\n\n'.join(rendered)
