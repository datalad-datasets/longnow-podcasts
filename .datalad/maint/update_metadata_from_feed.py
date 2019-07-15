#!/usr/bin/env python

import feedparser

from datetime import datetime
import re
from urllib.parse import urlparse
from pathlib import (
    PosixPath,
    Path,
)
import simplejson as json

sanitize_re = re.compile('[^a-zA-Z0-9.]')


def main(url):
    """
    Parameters
    ----------
    url : str
      Feed URL
    """
    parsed = feedparser.parse(url)
    feeddir = Path(sanitize_re.sub('_', parsed['feed']['title']))
    meta_basepath = Path('.datalad') / 'feed_metadata'
    for entry in parsed['entries']:
        # first we need to build the target filename that annex importfeed
        # would generate so we know where to place the metadata
        published = datetime(*entry['published_parsed'][:6])
        published_date = published.date().strftime('%Y_%m_%d')
        fpath = PosixPath(urlparse(entry['link']).path)
        media_path = feeddir / '{}__{}{}'.format(
            published_date,
            sanitize_re.sub('_', entry['title']),
            fpath.suffix,
        )
        # p[ick out the link entry for the MP3
        media_link = [
            l for l in entry['links'] if l['type'] == 'audio/mpeg'][0]

        # now we can write out the metadata documents
        doc = {
            '@context': "https://schema.org/",
            '@type': 'MediaObject',
            'distribution': {
                '@type': 'DataDownload',
                'contentURL': entry['link'],
            },
            # duration in ISO_8601
            'duration': 'PT{}M{}S'.format(
                *entry['itunes_duration'].split(
                    ':' if ':' in entry['itunes_duration']
                    else '.')),
            'name': entry['title'],
            'description': entry['summary'],
            'encodingFormat': media_link['type'],
            'contentSize': media_link['length'],
            'creator': {
                "@type": "Organization",
                'name': entry['author'],
            },
            'datePublished': published.isoformat(),
        }
        meta_path = meta_basepath / '{}.json'.format(str(media_path))
        meta_path.parent.mkdir(exist_ok=True, parents=True)
        meta_path.write_text(
            # produce relatively compact, but also diff-friendly format
            json.dumps(
                doc,
                indent=0,
                separators=(',', ':\n'),
                sort_keys=True,
                ensure_ascii=False,
                encoding='utf-8',
            )
        )


if __name__ == "__main__":
    # execute only if run as a script
    import sys
    main(sys.argv[1])
