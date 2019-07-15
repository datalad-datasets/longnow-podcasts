#!/usr/bin/env python

from pathlib import Path
from datalad.api import (
    Dataset,
    # import to make sure the DataLad extension is loaded
    meta_dump,
)


def get_episode_metadata(dir):
    return [
        ep['metadata']['metalad_custom']
        for ep in ds.meta_dump(
            path=dir,
            reporton='files',
            result_renderer='disabled',
        )
        if 'metalad_custom' in ep['metadata']
    ]


def format_episode_list(meta):
    return '\n'.join(
        '* {title} ({published}) [{duration} min]'.format(
            title=m['name'],
            # just the date is enough
            published=m['datePublished'].split('T')[0],
            # full minutes are enough
            duration=m['duration'][2:].split('M')[0],
        )
        for m in meta
    )


def meta2episodelist(dir):
    return format_episode_list(
        sorted(
            get_episode_metadata(dir),
            key=lambda x: x['datePublished'],
        )
    )


readme_tmpl = (Path('.datalad') / 'maint' / 'README.md.in').read_text()
readme_file = Path('README.md')

ds = Dataset('.')
# get dataset-global metadata
dsmeta = ds.meta_dump(
    reporton='datasets',
    result_renderer='disabled',
)
# if there is more than one, someting is fishy and we want to fail
assert(len(dsmeta) == 1)

dsmeta = dsmeta[0]['metadata']

readme_file.write_text(readme_tmpl.format(
    title=dsmeta['metalad_custom']['name'],
    description=dsmeta['metalad_custom']['description'],
    saltepisodes=meta2episodelist(
        'Long_Now__Seminars_About_Long_term_Thinking'),
    intervalepisodes=meta2episodelist(
        'Long_Now__Conversations_at_The_Interval'),
))
