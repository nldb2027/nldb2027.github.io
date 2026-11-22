#!/usr/bin/env python3
"""Generate nldb2027.ics from event_data.py (standard library only)."""
from datetime import date, datetime, timezone
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from event_data import EVENTS

def escape_ics(s: str) -> str:
    return str(s).replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')

def utc_string(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

def fold_ics(line: str) -> list[str]:
    # RFC 5545 recommends 75 octets max/line; fold at UTF-8 char boundaries.
    lines, current, width = [], '', 0
    for ch in line:
        n = len(ch.encode('utf8'))
        if current and width + n > 75:
            lines.append(current)
            current, width = ' ', 1
        current += ch
        width += n
    lines.append(current)
    return lines

def main():
    generated = datetime.now(timezone.utc)
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//NLDB//Lexicon Pelican template//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH', 'X-WR-CALNAME:NLDB 2027 deadlines']
    for event in EVENTS:
        if not event.get('date'):
            continue
        day = date.fromisoformat(event['date']).strftime('%Y%m%d')
        is_deadline = bool(event.get('deadline'))
        description = ('Deadline 23:59 AoE (UTC-12)' if is_deadline else 'NLDB 2027, Bucharest')
        if event.get('provisional'):
            description += ' (provisional)'
        lines += [
            'BEGIN:VEVENT',
            'UID:'+event['id']+'-2027@nldb2027',
            'DTSTAMP:'+utc_string(generated),
            'DTSTART;VALUE=DATE:'+day,
            'SUMMARY:'+escape_ics('NLDB 2027: '+event['label']),
            'DESCRIPTION:'+escape_ics(description),
            'TRANSP:TRANSPARENT',
            'END:VEVENT',
        ]
    lines.append('END:VCALENDAR')
    text='\r\n'.join(item for line in lines for item in fold_ics(line))+'\r\n'
    target = ROOT/'content'/'extra'/'nldb2027.ics'
    target.parent.mkdir(exist_ok=True, parents=True)
    target.write_bytes(text.encode('utf8'))
    print('Wrote', target)
if __name__ == '__main__': main()
